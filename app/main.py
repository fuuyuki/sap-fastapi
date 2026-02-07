import asyncio
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from . import crud, schemas
from .database import database, engine, metadata
from .models import devices, medlogs, schedules, users
from .security import (
    create_access_token,
    get_current_user_id,
    hash_password,
    verify_password,
)

metadata.create_all(engine)
app = FastAPI(title="SAP API")


@app.on_event("startup")
async def startup():
    await database.connect()
    asyncio.create_task(auto_offline_check())


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


async def auto_offline_check():
    while True:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
        query = (
            devices.update()
            .where(devices.c.last_seen < cutoff)
            .values(status="offline")
        )
        await database.execute(query)
        await asyncio.sleep(60)  # run every 60 seconds


@app.post("/register")
async def register(user: schemas.UserIn):
    # Check if email already exists
    existing_user = await database.fetch_one(
        users.select().where(users.c.email == user.email)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password securely
    hashed_pw = hash_password(user.password)

    # Insert and return UUID
    query = (
        users.insert()
        .values(
            name=user.name,
            email=user.email,
            password=hashed_pw,
        )
        .returning(users.c.id)
    )

    user_id = await database.execute(query)

    return {
        "id": str(user_id),
        "email": user.email,
        "message": "User registered successfully",
    }


# --- User Login ---
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await database.fetch_one(
        users.select().where(users.c.email == form_data.username)
    )
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}


# --- User Endpoints ---
@app.get("/users/", response_model=list[schemas.UserOut])
async def read_users():
    return await crud.get_users()


@app.get("/users/{user_id}", response_model=schemas.UserOut)
async def read_user(user_id: UUID):
    user = await crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}")
async def update_user(user_id: UUID, user: schemas.UserIn):
    updated = await crud.update_user(user_id, user.name, user.email, user.password)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully", "user": updated}


@app.delete("/users/{user_id}")
async def delete_user(user_id: UUID):
    deleted = await crud.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully", "user": deleted}


@app.get("/users/{user_id}/adherence-streak", response_model=schemas.AdherenceStreak)
async def adherence_streak(user_id: UUID):
    streak = await crud.get_adherence_streak(user_id)
    return schemas.AdherenceStreak(streak=streak)


@app.get("/users/{user_id}/next-dose", response_model=schemas.NextDose)
async def next_dose(user_id: UUID):
    dose = await crud.get_next_dose(user_id)
    if not dose:
        raise HTTPException(status_code=404, detail="No upcoming dose found")
    return schemas.NextDose(
        schedule_id=dose["id"], pillname=dose["pillname"], dose_time=dose["dose_time"]
    )


@app.get("/users/{user_id}/weekly-adherence", response_model=schemas.WeeklyAdherence)
async def weekly_adherence(user_id: UUID):
    adherence = await crud.get_weekly_adherence(user_id)
    return schemas.WeeklyAdherence(adherence=adherence)


# --- Device Endpoints ---
@app.post("/devices/", response_model=schemas.DeviceOut)
async def create_device(
    device: schemas.DeviceIn, user_id: UUID = Depends(get_current_user_id)
):
    device_id = await crud.create_device(user_id, device.name, device.chip_id)
    new_device = await database.fetch_one(
        devices.select().where(devices.c.id == device_id)
    )
    return new_device


@app.get("/devices/", response_model=list[schemas.DeviceOut])
async def read_my_devices(user_id: UUID = Depends(get_current_user_id)):
    return await crud.get_devices(user_id)


@app.get("/devices/{device_id}", response_model=schemas.DeviceOut)  # ✅ fixed
async def read_device(device_id: UUID, user_id: UUID = Depends(get_current_user_id)):
    device = await crud.get_device_by_user(
        device_id, user_id
    )  # ✅ safer ownership check
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.put("/devices/{device_id}", response_model=schemas.DeviceOut)
async def update_my_device(
    device_id: UUID,
    device: schemas.DeviceIn,
    user_id: UUID = Depends(get_current_user_id),
):
    existing = await crud.get_device_by_user(
        device_id, user_id
    )  # ✅ safer ownership check
    if not existing:
        raise HTTPException(status_code=404, detail="Device not found")

    await crud.update_device(device_id, device.name, device.chip_id)
    updated = await crud.get_device(device_id)
    return updated


@app.post("/devices/{chip_id}/heartbeat", response_model=schemas.DeviceOut)
async def heartbeat(chip_id: str):
    updated = await crud.update_device_heartbeat(chip_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Device not found")

    device = await database.fetch_one(
        devices.select().where(devices.c.chip_id == chip_id)
    )
    if device is None:  # safeguard
        raise HTTPException(status_code=404, detail="Device not found")

    return schemas.DeviceOut(**dict(device))


@app.delete("/devices/{device_id}")
async def delete_my_device(
    device_id: UUID, user_id: UUID = Depends(get_current_user_id)
):
    existing = await crud.get_device_by_user(
        device_id, user_id
    )  # ✅ safer ownership check
    if not existing:
        raise HTTPException(status_code=404, detail="Device not found")

    deleted = await crud.delete_device(device_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Device deleted successfully", "device_id": deleted}


# --- Schedule Endpoints ---
@app.post("/schedules/", response_model=schemas.ScheduleOut)
async def create_schedule(
    schedule: schemas.ScheduleIn, user_id: UUID = Depends(get_current_user_id)
):
    schedule_id = await crud.create_schedule(
        user_id,
        schedule.device_id,
        schedule.pillname,
        schedule.dose_time,
        schedule.repeat_days,
    )
    new_schedule = await database.fetch_one(
        schedules.select().where(schedules.c.id == schedule_id)
    )
    return new_schedule


@app.get("/schedules/", response_model=list[schemas.ScheduleOut])
async def read_my_schedules(user_id: UUID = Depends(get_current_user_id)):
    return await crud.get_schedules(user_id)


@app.put("/schedules/{schedule_id}", response_model=schemas.ScheduleOut)
async def update_my_schedule(
    schedule_id: UUID,
    schedule: schemas.ScheduleIn,
    user_id: UUID = Depends(get_current_user_id),
):
    # Ensure the schedule belongs to this user
    existing = await crud.get_schedule_by_user(schedule_id, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await crud.update_schedule(
        schedule_id, schedule.pillname, schedule.dose_time, schedule.repeat_days
    )
    updated = await crud.get_schedule(schedule_id)
    return updated


@app.delete("/schedules/{schedule_id}")
async def delete_my_schedule(
    schedule_id: UUID, user_id: UUID = Depends(get_current_user_id)
):
    # Ensure the schedule belongs to this user
    existing = await crud.get_schedule_by_user(schedule_id, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Schedule not found")

    deleted = await crud.delete_schedule(schedule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted successfully", "schedule_id": deleted}


# --- Medlog Endpoints ---
@app.post("/medlogs/", response_model=schemas.MedlogOut)
async def create_medlog(
    medlog: schemas.MedlogIn,
    user_id: UUID = Depends(get_current_user_id),  # automated user_id
):
    medlog_id = await crud.create_medlog(
        user_id,
        medlog.device_id,
        medlog.pillname,
        medlog.status,
    )
    new_medlog = await database.fetch_one(
        medlogs.select().where(medlogs.c.id == medlog_id)
    )
    return new_medlog


@app.get("/medlogs/", response_model=list[schemas.MedlogOut])
async def read_my_medlogs(user_id: UUID = Depends(get_current_user_id)):
    return await crud.get_medlogs(user_id)


@app.delete("/medlogs/{medlog_id}")
async def delete_my_medlog(
    medlog_id: UUID, user_id: UUID = Depends(get_current_user_id)
):
    existing = await crud.get_medlog_by_user(medlog_id, user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Medlog not found")

    deleted = await crud.delete_medlog(medlog_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Medlog not found")
    return {"message": "Medlog deleted successfully", "medlog_id": deleted}
