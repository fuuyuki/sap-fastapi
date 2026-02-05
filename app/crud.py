from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func

from .database import database
from .models import devices, medlogs, schedules, users
from .security import hash_password, verify_password


# User Section
async def authenticate_user(email: str, password: str):
    query = users.select().where(users.c.email == email)
    user = await database.fetch_one(query)
    if not user or not verify_password(password, user["password"]):
        return None
    return user


async def get_users():
    query = users.select()
    return await database.fetch_all(query)


async def get_user(user_id: UUID):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


async def update_user(user_id: UUID, name: str, email: str, password: str):
    query = (
        users.update()
        .where(users.c.id == user_id)
        .values(name=name, email=email, password=password)
        .returning(users.c.id)
    )
    return await database.fetch_one(query)


async def delete_user(user_id: UUID):
    query = users.delete().where(users.c.id == user_id).returning(users.c.id)
    return await database.fetch_one(query)


# Device Section
async def create_device(user_id, name, chip_id):
    query = devices.insert().values(user_id=user_id, name=name, chip_id=chip_id)
    return await database.execute(query)


async def get_devices(user_id):
    query = devices.select().where(devices.c.user_id == user_id)
    return await database.fetch_all(query)


async def get_device(device_id):
    query = devices.select().where(devices.c.id == device_id)
    return await database.fetch_one(query)


async def get_device_by_user(device_id, user_id):
    query = devices.select().where(
        (devices.c.id == device_id) & (devices.c.user_id == user_id)
    )
    return await database.fetch_one(query)


async def update_device(device_id, name, chip_id):
    query = (
        devices.update()
        .where(devices.c.id == device_id)
        .values(name=name, chip_id=chip_id)
    )
    return await database.execute(query)


async def update_device_heartbeat(device_id: UUID) -> bool:
    query = (
        devices.update()
        .where(devices.c.id == device_id)
        .values(status="online", last_seen=datetime.now(timezone.utc))
    )
    result = await database.execute(query)
    return result


async def delete_device(device_id):
    query = devices.delete().where(devices.c.id == device_id).returning(devices.c.id)
    return await database.fetch_one(query)


# Schedule Section
async def create_schedule(user_id, device_id, pillname, dose_time, repeat_days=0):
    query = schedules.insert().values(
        user_id=user_id,
        device_id=device_id,
        pillname=pillname,
        dose_time=dose_time,
        repeat_days=repeat_days,
    )
    return await database.execute(query)


async def get_schedules(user_id):
    query = schedules.select().where(schedules.c.user_id == user_id)
    return await database.fetch_all(query)


async def get_schedule(schedule_id):
    query = schedules.select().where(schedules.c.id == schedule_id)
    return await database.fetch_one(query)


async def get_schedule_by_user(schedule_id, user_id):
    query = schedules.select().where(
        (schedules.c.id == schedule_id) & (schedules.c.user_id == user_id)
    )
    return await database.fetch_one(query)


async def update_schedule(schedule_id, pillname, dose_time, repeat_days):
    query = (
        schedules.update()
        .where(schedules.c.id == schedule_id)
        .values(pillname=pillname, dose_time=dose_time, repeat_days=repeat_days)
    )
    return await database.execute(query)


async def delete_schedule(schedule_id):
    query = (
        schedules.delete()
        .where(schedules.c.id == schedule_id)
        .returning(schedules.c.id)
    )
    return await database.fetch_one(query)


# Medlog Section
async def create_medlog(user_id, device_id, pillname, status):
    query = medlogs.insert().values(
        user_id=user_id,
        device_id=device_id,
        pillname=pillname,
        status=status,
    )
    return await database.execute(query)


async def get_medlogs(user_id):
    query = (
        medlogs.select()
        .where(medlogs.c.user_id == user_id)
        .order_by(medlogs.c.taken_at.desc())
    )
    return await database.fetch_all(query)


async def get_medlog_by_user(medlog_id, user_id):
    query = medlogs.select().where(
        (medlogs.c.id == medlog_id) & (medlogs.c.user_id == user_id)
    )
    return await database.fetch_one(query)


async def update_medlog(medlog_id, pillname, status):
    query = (
        medlogs.update()
        .where(medlogs.c.id == medlog_id)
        .values(pillname=pillname, status=status)
    )
    return await database.execute(query)


async def delete_medlog(medlog_id):
    query = medlogs.delete().where(medlogs.c.id == medlog_id).returning(medlogs.c.id)
    return await database.fetch_one(query)


async def get_adherence_streak(user_id: UUID) -> int:
    # Get last 30 days of logs (adjust window as needed)
    start = datetime.now().date() - timedelta(days=30)
    query = (
        medlogs.select()
        .where(medlogs.c.user_id == user_id, medlogs.c.schedule_time >= start)
        .order_by(medlogs.c.schedule_time.desc())
    )

    rows = await database.fetch_all(query)
    streak = 0
    for row in rows:
        if row["status"] == "taken":
            streak += 1
        else:
            break
    return streak


async def get_next_dose(user_id: UUID):
    query = (
        schedules.select()
        .where(schedules.c.user_id == user_id, schedules.c.dose_time > datetime.now())
        .order_by(schedules.c.dose_time.asc())
        .limit(1)
    )
    row = await database.fetch_one(query)
    return dict(row) if row else None


async def get_weekly_adherence(user_id: UUID) -> float:
    start = datetime.now() - timedelta(days=7)

    # Count taken doses
    taken_query = (
        medlogs.select()
        .with_only_columns(func.count())
        .where(
            medlogs.c.user_id == user_id,
            medlogs.c.status == "taken",
            medlogs.c.scheduled_time >= start,
        )
    )
    taken = await database.fetch_val(taken_query)

    # Count missed doses
    missed_query = (
        medlogs.select()
        .with_only_columns(func.count())
        .where(
            medlogs.c.user_id == user_id,
            medlogs.c.status == "missed",
            medlogs.c.scheduled_time >= start,
        )
    )
    missed = await database.fetch_val(missed_query)

    total = taken + missed
    adherence = taken / total if total > 0 else 0.0
    return adherence * 100
