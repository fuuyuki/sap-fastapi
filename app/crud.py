import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import database
from .models import devices, medlogs, notifications, schedules, users
from .security import hash_password


# ---------------------------
# USERS
# ---------------------------
async def create_user(name: str, email: str, password_hash: str, role: str = "patient"):
    query = (
        users.insert()
        .values(name=name, email=email, password_hash=password_hash, role=role)
        .returning(users.c.id)
    )
    return await database.execute(query)


async def get_user(user_id: UUID):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


async def get_users():
    query = users.select()
    return await database.fetch_all(query)


async def update_user(user_id: UUID, data: dict):
    query = users.update().where(users.c.id == user_id).values(**data)
    await database.execute(query)
    return await get_user(user_id)


async def delete_user(user_id: UUID):
    query = users.delete().where(users.c.id == user_id)
    return await database.execute(query)


async def update_password(user_id: UUID, new_password: str):
    # Hash the password using your Argon2 helper
    hashed_pw = hash_password(new_password)

    query = users.update().where(users.c.id == user_id).values(password=hashed_pw)
    await database.execute(query)
    return {"msg": "Password updated successfully"}


# ---------------------------
# DEVICES
# ---------------------------


async def create_device(
    chip_id: str, user_id: UUID, name: str, status: str = "offline"
):
    # Generate a secure random API key
    api_key = secrets.token_hex(32)

    query = (
        devices.insert()
        .values(
            chip_id=chip_id,
            user_id=user_id,
            name=name,
            api_key=api_key,
            last_seen=datetime.now(),
            status=status,
        )
        .returning(
            devices.c.chip_id,
            devices.c.user_id,
            devices.c.name,
            devices.c.last_seen,
            devices.c.api_key,
            devices.c.status,
        )
    )

    return await database.fetch_one(query)


# --- Get schedules by user_id ---
async def get_device_by_user(user_id: UUID):
    query = devices.select().where(devices.c.user_id == user_id)
    record = await database.fetch_one(query)
    return dict(record) if record else None


# --- Get schedules by chip_id (device) ---
async def get_device_by_device(chip_id: str):
    query = devices.select().where(devices.c.chip_id == chip_id)
    return await database.fetch_one(query)


async def get_devices():
    query = devices.select()
    return await database.fetch_all(query)


async def update_device(chip_id: str, data: dict):
    query = devices.update().where(devices.c.chip_id == chip_id).values(**data)
    await database.fetch_one(query)
    return await get_device_by_device(chip_id)


async def delete_device(chip_id: str):
    query = devices.delete().where(devices.c.chip_id == chip_id)
    return await database.execute(query)


async def heartbeat_device(chip_id: str):
    query = (
        devices.update()
        .where(devices.c.chip_id == chip_id)
        .values(status="online", last_seen=datetime.now(timezone.utc))
    )
    return await database.execute(query)


# ---------------------------
# SCHEDULES
# ---------------------------
async def create_schedule_for_user(
    user_id: UUID,
    chip_id: str,
    pillname: str,
    dose_time: datetime,
    repeat_days: int = 0,
):
    query = (
        schedules.insert()
        .values(
            user_id=user_id,
            chip_id=chip_id,
            pillname=pillname,
            dose_time=dose_time,
            repeat_days=repeat_days,
        )
        .returning(schedules.c.id)
    )
    schedule_id = await database.execute(query)
    return await database.fetch_one(
        schedules.select().where(schedules.c.id == schedule_id)
    )


async def get_schedule(schedule_id):
    query = schedules.select().where(schedules.c.id == schedule_id)
    return await database.fetch_one(query)


# --- Get schedules by user_id ---
async def get_schedules_by_user(user_id: UUID):
    query = schedules.select().where(schedules.c.user_id == user_id)
    return await database.fetch_all(query)


# --- Get schedules by chip_id (device) ---
async def get_schedules_by_device(chip_id: str):
    query = schedules.select().where(schedules.c.chip_id == chip_id)
    return await database.fetch_all(query)


async def update_schedule(schedule_id: UUID, data: dict):
    query = schedules.update().where(schedules.c.id == schedule_id).values(**data)
    await database.execute(query)
    return await get_schedule(schedule_id)


async def delete_schedule(schedule_id: UUID):
    query = schedules.delete().where(schedules.c.id == schedule_id)
    return await database.execute(query)


# ---------------------------
# MEDLOGS
# ---------------------------


# --- Get medlogs by user_id ---
async def get_medlogs_by_user(user_id: UUID):
    query = medlogs.select().where(medlogs.c.user_id == user_id)
    return await database.fetch_all(query)


# --- Create medlog by device (chip_id) ---
async def create_medlog_by_device(
    chip_id: str, user_id: UUID, pillname: str, scheduled_time: datetime, status: str
):
    query = (
        medlogs.insert()
        .values(
            user_id=user_id,
            chip_id=chip_id,
            pillname=pillname,
            scheduled_time=scheduled_time,
            status=status,
        )
        .returning(medlogs.c.id)
    )
    medlog_id = await database.execute(query)
    return await database.fetch_one(medlogs.select().where(medlogs.c.id == medlog_id))


async def get_medlog(medlog_id: UUID):
    query = medlogs.select().where(medlogs.c.id == medlog_id)
    return await database.fetch_one(query)


async def update_medlog(medlog_id: UUID, data: dict):
    query = medlogs.update().where(medlogs.c.id == medlog_id).values(**data)
    await database.execute(query)
    return await get_medlog(medlog_id)


async def delete_medlog(medlog_id: UUID):
    query = medlogs.delete().where(medlogs.c.id == medlog_id)
    return await database.execute(query)


# ---------------------------
# NOTIFICATIONS
# ---------------------------
# --- Get notifications by user_id ---
async def get_notifications_by_user(user_id: UUID):
    query = notifications.select().where(notifications.c.user_id == user_id)
    return await database.fetch_all(query)


# --- Create notification by device (chip_id) ---
async def create_notification_by_device(
    chip_id: str, user_id: UUID, message: str, created_at: datetime
):
    query = (
        notifications.insert()
        .values(
            user_id=user_id, chip_id=chip_id, message=message, created_at=created_at
        )
        .returning(notifications.c.id)
    )
    notif_id = await database.execute(query)
    return await database.fetch_one(
        notifications.select().where(notifications.c.id == notif_id)
    )


async def get_notifications(user_id: UUID = None, chip_id: str = None):
    query = notifications.select()
    if user_id:
        query = query.where(notifications.c.user_id == user_id)
    if chip_id:
        query = query.where(notifications.c.chip_id == chip_id)
    return await database.fetch_all(query)


async def delete_notification(notification_id: UUID):
    query = notifications.delete().where(notifications.c.id == notification_id)
    return await database.execute(query)


# ---------------------------
# ADHERENCE ANALYTICS
# ---------------------------


async def get_adherence_streak(user_id: UUID) -> int:
    """Count consecutive 'taken' doses until first 'missed' in last 30 days."""
    start = datetime.now(timezone.utc).date() - timedelta(days=30)
    query = (
        medlogs.select()
        .where(medlogs.c.user_id == user_id, medlogs.c.scheduled_time >= start)
        .order_by(medlogs.c.scheduled_time.desc())
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
    """Return the next scheduled dose for a user."""
    query = (
        schedules.select()
        .where(schedules.c.user_id == user_id, schedules.c.dose_time > datetime.now(timezone.utc)))
        .order_by(schedules.c.dose_time.asc())
        .limit(1)
    )
    row = await database.fetch_one(query)
    return dict(row) if row else None


async def get_weekly_adherence(user_id: UUID) -> float:
    """Return adherence percentage for last 7 days."""
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
    return adherence
