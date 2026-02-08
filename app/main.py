from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from . import crud, schemas
from .database import database
from .models import devices, users
from .security import (  # implement in auth.py
    create_access_token,
    get_current_user_id,
    hash_password,
    verify_password,
)

app = FastAPI(title="SAP API")


# Startup event: connect to DB
@app.on_event("startup")
async def startup():
    await database.connect()


# Shutdown event: disconnect from DB
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# --- User Register ---
@app.post("/register")
async def register(user: schemas.UserCreate):
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
            name=user.name, email=user.email, password_hash=hashed_pw, role=user.role
        )
        .returning(users.c.id)
    )
    user_id = await database.execute(query)

    return {
        "id": str(user_id),
        "email": user.email,
        "message": "User registered successfully",
    }


# JSON login
@app.post("/login", tags=["auth"])
async def login_json(credentials: schemas.LoginRequest):
    user = await database.fetch_one(
        users.select().where(users.c.email == credentials.email)
    )
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}


# Form login (for Swagger Authorize button)
@app.post("/login-form", tags=["auth"])
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await database.fetch_one(
        users.select().where(users.c.email == form_data.username)
    )
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------
# USERS (App + Admin)
# ---------------------------
@app.get("/users/", response_model=List[schemas.UserRead])
async def list_users():
    return await crud.get_users()


@app.get("/users/{user_id}", response_model=schemas.UserRead)
async def get_user(user_id: UUID):
    user = await crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=schemas.UserRead)
async def update_user(user_id: UUID, update: schemas.UserUpdate):
    return await crud.update_user(user_id, update.dict(exclude_unset=True))


@app.delete("/users/{user_id}")
async def delete_user(user_id: UUID):
    await crud.delete_user(user_id)
    return {"detail": "User deleted"}


# ---------------------------
# ADHERENCE SUMMARY (App)
# ---------------------------
@app.get("/users/{user_id}/adherence-summary")
async def adherence_summary(user_id: UUID):
    streak = await crud.get_adherence_streak(user_id)
    next_dose = await crud.get_next_dose(user_id)
    weekly = await crud.get_weekly_adherence(user_id)
    return {
        "user_id": str(user_id),
        "adherence_streak": streak,
        "next_dose": next_dose,
        "weekly_adherence": weekly,
    }


# ---------------------------
# DEVICES (ESP32 + Admin)
# ---------------------------
@app.get("/devices/{user_id}", response_model=List[schemas.DeviceRead])
async def list_devices(user_id: UUID):
    devices = await crud.get_devices_by_user(user_id)
    if not devices:
        raise HTTPException(status_code=404, detail="No devices found for this user")
    return devices


@app.post("/devices/", response_model=schemas.DeviceRead)
async def create_device(device: schemas.DeviceCreate):
    new_device = await crud.create_device(
        chip_id=device.chip_id,
        user_id=device.user_id,
        name=device.name,
        status=device.status,
    )
    if not new_device:
        raise HTTPException(status_code=400, detail="Device creation failed")
    return new_device


@app.put("/devices/{chip_id}", response_model=schemas.DeviceRead)
async def update_device(chip_id: str, update: schemas.DeviceUpdate):
    return await crud.update_device(chip_id, update.dict(exclude_unset=True))


@app.delete("/devices/{chip_id}")
async def delete_device(chip_id: str):
    await crud.delete_device(chip_id)
    return {"detail": "Device deleted"}


@app.post("/devices/{chip_id}/heartbeat")
async def post_heartbeat(chip_id: str):
    await crud.heartbeat_device(chip_id)
    return {"chip_id": chip_id, "status": "online", "last_seen": datetime.now()}


# ---------------------------
# SCHEDULES (App + ESP32 + Admin)
# ---------------------------


# --- GET schedules by user_id (JWT protected) ---
@app.get("/schedules/{user_id}", response_model=List[schemas.ScheduleRead])
async def list_schedules_by_user(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user_id),  # JWT validation
):
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these schedules"
        )

    schedules = await crud.get_schedules_by_user(user_id)
    if not schedules:
        raise HTTPException(status_code=404, detail="No schedules found for user")
    return schedules


# --- POST schedule for user_id (JWT protected) ---
@app.post("/schedules/{user_id}", response_model=schemas.ScheduleRead)
async def create_schedule_for_user(
    user_id: UUID,
    schedule: schemas.ScheduleCreate,
    current_user_id: str = Depends(get_current_user_id),
):
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to create schedules for this user"
        )

    schedule_data = schedule.dict()
    schedule_data["user_id"] = user_id
    new_schedule = await crud.create_schedule_for_user(**schedule_data)
    return new_schedule


# --- GET schedules by chip_id (API key protected) ---
@app.get("/schedules/device/{chip_id}", response_model=List[schemas.ScheduleRead])
async def list_schedules_by_device(
    chip_id: str,
    x_api_key: str = Header(..., alias="X-API-Key"),  # API key header
):
    # Validate device + API key
    device = await database.fetch_one(
        devices.select().where(devices.c.chip_id == chip_id)
    )
    if not device or device["api_key"] != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid device API key")

    schedules = await crud.get_schedules_by_device(chip_id)
    if not schedules:
        raise HTTPException(status_code=404, detail="No schedules found for device")
    return schedules


@app.put("/schedules/{schedule_id}", response_model=schemas.ScheduleRead)
async def update_schedule(schedule_id: UUID, update: schemas.ScheduleUpdate):
    return await crud.update_schedule(schedule_id, update.dict(exclude_unset=True))


@app.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: UUID):
    await crud.delete_schedule(schedule_id)
    return {"detail": "Schedule deleted"}


# ---------------------------
# MEDLOGS (App + ESP32 + Admin)
# ---------------------------


# --- GET medlogs by user_id (JWT protected) ---
@app.get("/medlogs/{user_id}", response_model=List[schemas.MedlogRead])
async def list_medlogs_by_user(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user_id),  # JWT validation
):
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these medlogs"
        )

    logs = await crud.get_medlogs_by_user(user_id)
    if not logs:
        raise HTTPException(status_code=404, detail="No medlogs found for user")
    return logs


# --- POST medlog by device (API key protected) ---
@app.post("/medlogs/{chip_id}", response_model=schemas.MedlogRead)
async def create_medlog_by_device(
    chip_id: str,
    medlog: schemas.MedlogCreate,
    x_api_key: str = Header(..., alias="X-API-Key"),  # API key header
):
    # Validate device + API key
    device = await database.fetch_one(
        devices.select().where(devices.c.chip_id == chip_id)
    )
    if not device or device["api_key"] != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid device API key")

    new_log = await crud.create_medlog_by_device(
        chip_id=chip_id,
        user_id=medlog.user_id,
        pillname=medlog.pillname,
        scheduled_time=medlog.scheduled_time,
        status=medlog.status,
    )
    return new_log


@app.put("/medlogs/{medlog_id}", response_model=schemas.MedlogRead)
async def update_medlog(medlog_id: UUID, update: schemas.MedlogUpdate):
    return await crud.update_medlog(medlog_id, update.dict(exclude_unset=True))


@app.delete("/medlogs/{medlog_id}")
async def delete_medlog(medlog_id: UUID):
    await crud.delete_medlog(medlog_id)
    return {"detail": "Medlog deleted"}


# ---------------------------
# NOTIFICATIONS (App + ESP32)
# ---------------------------


# --- GET notifications by user_id (JWT protected) ---
@app.get("/notifications/{user_id}", response_model=List[schemas.NotificationRead])
async def list_notifications_by_user(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user_id),  # JWT validation
):
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these notifications"
        )

    notifs = await crud.get_notifications_by_user(user_id)
    if not notifs:
        raise HTTPException(status_code=404, detail="No notifications found for user")
    return notifs


# --- POST notification by device_id (API key protected) ---
@app.post("/notifications/{device_id}", response_model=schemas.NotificationRead)
async def create_notification_by_device(
    device_id: str,
    notif: schemas.NotificationCreate,
    x_api_key: str = Header(..., alias="X-API-Key"),  # API key header
):
    # Validate device + API key
    device = await database.fetch_one(
        devices.select().where(devices.c.chip_id == device_id)
    )
    if not device or device["api_key"] != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid device API key")

    new_notif = await crud.create_notification_by_device(
        device_id=device_id,
        user_id=notif.user_id,
        message=notif.message,
        created_at=notif.created_at,
    )
    return new_notif


@app.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: UUID):
    await crud.delete_notification(notification_id)
    return {"detail": "Notification deleted"}
