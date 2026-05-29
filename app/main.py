import asyncio
from datetime import datetime, timedelta
from typing import List
from uuid import UUID

import pytz
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from . import crud, firebase_client, schemas
from .database import database
from .models import device_tokens, devices, medlogs, schedules, users
from .security import (
    create_access_token,
    get_current_user_id,
    hash_password,
    verify_password,
)

wib = pytz.timezone("Asia/Jakarta")

app = FastAPI(title="SAP API")


# Startup event: connect to DB
@app.on_event("startup")
async def startup():
    await database.connect()
    asyncio.create_task(auto_offline_check())


# Shutdown event: disconnect from DB
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# ESP32 Auto-Offline Check: runs every 10 seconds, marks devices offline if no heartbeat in last 15 seconds
async def auto_offline_check():
    while True:
        cutoff = datetime.now(wib) - timedelta(seconds=15)
        query = (
            devices.update()
            .where(devices.c.last_seen < cutoff)
            .values(status="offline")
        )
        await database.execute(query)
        await asyncio.sleep(10)  # run every 10 seconds


# --- User Register ---
@app.post("/register")
async def register(user: schemas.UserCreate):
    # Check if email already exists
    existing_user = await database.fetch_one(
        users.select().where(users.c.email == user.email)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role
    if user.role not in ("patient", "caretaker"):
        raise HTTPException(
            status_code=400, detail="Role must be 'patient' or 'caretaker'"
        )

    # Enforce caretaker relationship rules
    if user.role == "patient" and not user.caretaker_id:
        raise HTTPException(status_code=400, detail="Patients must have a caretaker_id")
    if user.role == "caretaker" and user.caretaker_id is not None:
        raise HTTPException(
            status_code=400, detail="Caretakers cannot have a caretaker_id"
        )

    # Hash password securely
    hashed_pw = hash_password(user.password)

    # Insert and return UUID
    query = (
        users.insert()
        .values(
            name=user.name,
            email=user.email,
            password=hashed_pw,
            role=user.role,
            caretaker_id=user.caretaker_id,
        )
        .returning(users.c.id)
    )
    user_id = await database.execute(query)

    return {
        "id": str(user_id),
        "email": user.email,
        "role": user.role,
        "message": "User registered successfully",
    }


# JSON login
@app.post("/login", tags=["auth"])
async def login_json(credentials: schemas.LoginRequest):
    user = await database.fetch_one(
        users.select().where(users.c.email == credentials.email)
    )
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}


# Form login (for Swagger Authorize button)
@app.post("/login-form", tags=["auth"])
async def login_form(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await database.fetch_one(
        users.select().where(users.c.email == form_data.username)
    )
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(str(user["id"]))
    return {"access_token": token, "token_type": "bearer"}


# ---------------------------
# USERS (App + Admin)
# ---------------------------


@app.get("/me", response_model=schemas.UserMe)
async def read_me(current_user_id: str = Depends(get_current_user_id)):
    # Simply return the user_id from the JWT
    return {"user_id": current_user_id}


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


@app.put("/users/{user_id}/password")
async def update_user_password(user_id: UUID, payload: schemas.PasswordUpdate):
    try:
        result = await crud.update_password(user_id, payload.new_password)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}")
async def delete_user(user_id: UUID):
    await crud.delete_user(user_id)
    return {"detail": "User deleted"}


@app.get("/caretakers/{caretaker_id}/patients", response_model=List[schemas.UserOut])
async def list_patients_by_caretaker(
    caretaker_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
):
    # Ensure the caller is the caretaker themselves
    if str(caretaker_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view patients")

    patients_query = users.select().where(users.c.caretaker_id == caretaker_id)
    patients = await database.fetch_all(patients_query)

    if not patients:
        raise HTTPException(status_code=404, detail="No patients found for caretaker")

    return patients


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
@app.get("/devices/", response_model=List[schemas.DeviceRead])
async def list_devices():
    return await crud.get_devices()


@app.get("/devices")
async def get_device(
    patient_id: UUID | None = None,
    caretaker_id: UUID | None = None,
    chip_id: str | None = None,
):
    if patient_id:
        return await crud.get_device_by_patient(patient_id)
    if caretaker_id:
        return await crud.get_devices_by_caretaker(caretaker_id)
    if chip_id:
        return await crud.get_device_by_device(chip_id)
    raise HTTPException(status_code=400, detail="Must provide user_id or chip_id")


@app.post("/devices/", response_model=schemas.DeviceRead)
async def create_device(device: schemas.DeviceCreate):
    # Ensure patient exists and is role=patient
    patient = await database.fetch_one(
        users.select().where(users.c.id == device.patient_id)
    )
    if not patient or patient["role"] != "patient":
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    new_device = await crud.create_device(
        chip_id=device.chip_id,
        patient_id=device.patient_id,
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


@app.post("/devices/{chip_id}/heartbeat/")
async def post_heartbeat(
    chip_id: str,
    payload: schemas.HeartbeatPayload,
    x_api_key: str = Header(..., alias="X-API-Key"),  # API key header
):
    # Validate device + API key
    device = await database.fetch_one(
        devices.select().where(devices.c.chip_id == chip_id)
    )
    if not device or device["api_key"] != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid device API key")

    try:
        # Parse ISO8601 string with timezone offset
        dt = datetime.fromisoformat(payload.last_seen)
        # # Optionally normalize to UTC for consistency
        utc_dt = dt.astimezone(wib)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")

    query = (
        devices.update()
        .where(devices.c.chip_id == chip_id)
        .values(status="online", last_seen=utc_dt)  # <-- use instance
    )
    result = await database.execute(query)
    return bool(result)


# ---------------------------
# SCHEDULES (App + ESP32 + Admin)
# ---------------------------
# --- POST schedule for user_id (JWT protected) ---
@app.get("/schedules/by-user/{user_id}", response_model=List[schemas.ScheduleRead])
async def list_schedules_by_user(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user_id),  # JWT validation
):
    # Ensure the caller is the same as the requested user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these schedules"
        )

    # Fetch the user record
    user = await database.fetch_one(users.select().where(users.c.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] == "patient":
        # Patient: return only their schedules
        schedules_records = await crud.get_schedules_by_user(user_id)
        if not schedules_records:
            raise HTTPException(
                status_code=404, detail="No schedules found for patient"
            )
        return schedules_records

    elif user["role"] == "caretaker":
        # Caretaker: return schedules of all their patients
        patients_query = users.select().where(users.c.caretaker_id == user_id)
        patients = await database.fetch_all(patients_query)
        patient_ids = [p["id"] for p in patients]

        if not patient_ids:
            raise HTTPException(
                status_code=404, detail="No patients found for caretaker"
            )

        schedules_query = schedules.select().where(
            schedules.c.patient_id.in_(patient_ids)
        )
        schedules_records = await database.fetch_all(schedules_query)
        if not schedules_records:
            raise HTTPException(
                status_code=404, detail="No schedules found for caretaker’s patients"
            )
        return schedules_records

    else:
        raise HTTPException(status_code=400, detail="Invalid role")


@app.post("/schedules/{patient_id}", response_model=schemas.ScheduleRead)
async def create_schedule_for_patient(
    patient_id: UUID,
    schedule: schemas.ScheduleCreate,
    current_user_id: str = Depends(get_current_user_id),
):
    # Fetch patient record
    patient = await database.fetch_one(users.select().where(users.c.id == patient_id))
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Allow if current user is the patient OR their caretaker
    if (
        str(patient_id) != current_user_id
        and str(patient["caretaker_id"]) != current_user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create schedules for this patient",
        )

    schedule_data = schedule.dict()
    schedule_data["patient_id"] = patient_id  # use patient_id instead of user_id
    new_schedule = await crud.create_schedule_for_user(**schedule_data)
    return new_schedule


@app.get(
    "/schedules/by-caretaker/{caretaker_id}/{patient_id}",
    response_model=List[schemas.ScheduleRead],
)
async def list_schedules_certain_patient_by_caretaker(
    caretaker_id: UUID, patient_id: UUID
):
    # Verify patient belongs to caretaker
    patient = await database.fetch_one(
        users.select()
        .where(users.c.id == patient_id)
        .where(users.c.caretaker_id == caretaker_id)
    )
    if not patient:
        raise HTTPException(
            status_code=403, detail="Patient not managed by this caretaker"
        )

    schedules_records = await crud.get_schedules_by_user(patient_id)
    if not schedules_records:
        raise HTTPException(status_code=404, detail="No schedules found for patient")
    return schedules_records


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
    query = (
        schedules.update()
        .where(schedules.c.id == schedule_id)
        .values(**update.dict(exclude_unset=True))
        .returning(*schedules.c)  # return all columns
    )
    record = await database.fetch_one(query)

    if not record:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return record


@app.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: UUID):
    await crud.delete_schedule(schedule_id)
    return {"detail": "Schedule deleted"}


@app.delete("/schedules/delete/{patient_id}", response_model=schemas.DeleteResponse)
async def delete_schedules_by_patient(patient_id: UUID):
    query = (
        schedules.delete()
        .where(schedules.c.patient_id == patient_id)
        .returning(schedules.c.id)
    )
    rows = await database.fetch_all(query)
    count = len(rows)

    if count == 0:
        raise HTTPException(status_code=404, detail="No schedules found for this user")

    return {
        "message": f"Schedules for user {patient_id} deleted. {count} rows removed."
    }


# MEDLOGS (App + ESP32 + Admin)
# ---------------------------
# --- GET medlogs by user_id (JWT protected) ---
@app.get("/medlogs/{user_id}", response_model=List[schemas.MedlogRead])
async def list_medlogs_by_user(
    user_id: UUID,
    current_user_id: str = Depends(get_current_user_id),  # JWT validation
):
    # Ensure the caller is the same as the requested user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these medlogs"
        )

    # Fetch the user record
    user = await database.fetch_one(users.select().where(users.c.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["role"] == "patient":
        # Patient: return only their medlogs
        logs = await crud.get_medlogs_by_user(user_id)
        if not logs:
            raise HTTPException(status_code=404, detail="No medlogs found for patient")
        return logs

    elif user["role"] == "caretaker":
        # Caretaker: return medlogs of all their patients
        patients_query = users.select().where(users.c.caretaker_id == user_id)
        patients = await database.fetch_all(patients_query)
        patient_ids = [p["id"] for p in patients]

        if not patient_ids:
            raise HTTPException(
                status_code=404, detail="No patients found for caretaker"
            )

        medlogs_query = medlogs.select().where(medlogs.c.patient_id.in_(patient_ids))
        logs = await database.fetch_all(medlogs_query)
        if not logs:
            raise HTTPException(
                status_code=404, detail="No medlogs found for caretaker’s patients"
            )
        return logs

    else:
        raise HTTPException(status_code=400, detail="Invalid role")


@app.get(
    "/medlogs/{caretaker_id}/{patient_id}", response_model=List[schemas.MedlogRead]
)
async def list_medlogs_certain_patient_by_caretaker(
    caretaker_id: UUID, patient_id: UUID
):
    # Verify patient belongs to caretaker
    patient = await database.fetch_one(
        users.select()
        .where(users.c.id == patient_id)
        .where(users.c.caretaker_id == caretaker_id)
    )
    if not patient:
        raise HTTPException(
            status_code=403, detail="Patient not managed by this caretaker"
        )

    medlogs_records = await crud.get_medlogs_by_user(patient_id)
    if not medlogs_records:
        raise HTTPException(status_code=404, detail="No medlogs found for patient")
    return medlogs_records


from fastapi import Request


@app.post("/medlogs/debug/{chip_id}")
async def debug_medlog_payload(
    chip_id: str,
    x_api_key: str = Header(..., alias="X-API-Key"),
    request: Request = None,
):
    # Capture raw JSON body
    body = await request.json()
    print("Raw Medlog payload:", body)

    # Validate device + API key (optional, keep if you want to check auth)
    device = await database.fetch_one(
        devices.select().where(devices.c.chip_id == chip_id)
    )
    if not device or device["api_key"] != x_api_key:
        raise HTTPException(status_code=401, detail="Invalid device API key")

    # Just return the raw payload for debugging
    return {"received_payload": body}


# @app.post("/medlogs/{chip_id}", response_model=schemas.MedlogRead)
# async def create_medlog_by_device(
#     chip_id: str,
#     medlog: schemas.MedlogCreate,
#     x_api_key: str = Header(..., alias="X-API-Key"),
#     request: Request = None,  # add Request
# ):
#     # Debug: print raw JSON payload
#     body = await request.json()
#     print("Received Medlog payload:", body)

#     # Validate device + API key
#     device = await database.fetch_one(
#         devices.select().where(devices.c.chip_id == chip_id)
#     )
#     if not device or device["api_key"] != x_api_key:
#         raise HTTPException(status_code=401, detail="Invalid device API key")

#     new_log = await crud.create_medlog_by_device(
#         device_id=device["chip_id"],
#         patient_id=medlog.patient_id,
#         pillname=medlog.pillname,
#         scheduled_time=medlog.scheduled_time,
#         status=medlog.status,
#     )
#     return new_log


@app.put("/medlogs/{medlog_id}", response_model=schemas.MedlogRead)
async def update_medlog(medlog_id: UUID, update: schemas.MedlogUpdate):
    return await crud.update_medlog(medlog_id, update.dict(exclude_unset=True))


@app.delete("/medlogs/{medlog_id}")
async def delete_medlog(medlog_id: UUID):
    await crud.delete_medlog(medlog_id)
    return {"detail": "Medlog deleted"}


# ---------------------------
# DEVICE TOKENS (for push notifications)
# ---------------------------
# --- Register or update Android FCM token ---
@app.post("/register_token")
async def register_token(payload: schemas.TokenRegisterRequest):
    # Upsert logic: if token already exists for user, update it
    existing = await database.fetch_one(
        device_tokens.select().where(
            (device_tokens.c.user_id == payload.user_id)
            & (device_tokens.c.token == payload.token)
        )
    )
    if existing:
        # Already registered
        return {"message": "Token already registered"}

    # Insert new token
    query = device_tokens.insert().values(user_id=payload.user_id, token=payload.token)
    await database.execute(query)

    return {"message": "Token registered successfully"}


# --- List all device tokens ---
@app.get("/device_tokens/", response_model=list[schemas.DeviceTokenRead])
async def list_device_tokens():
    tokens = await crud.get_all_device_tokens(database)
    return tokens


# --- List device tokens for a specific user ---
@app.get("/device_tokens/{user_id}", response_model=list[schemas.DeviceTokenRead])
async def list_device_tokens_by_user(user_id: UUID):
    tokens = await crud.get_device_tokens_by_user(database, user_id)
    return tokens


@app.delete("/device-tokens/{user_id}")
async def delete_device_tokens(
    user_id: str, current_user_id: str = Depends(get_current_user_id)
):

    await crud.delete_device_tokens_by_user(database, user_id)
    return {"detail": "Token deleted"}


# --- Bulk cleanup of old device tokens ---
@app.delete("/device_tokens/cleanup", response_model=schemas.DeleteResponse)
async def cleanup_device_tokens(days: int = 90):
    result = await crud.cleanup_device_tokens(database, days)
    return {
        "message": f"Cleanup complete. {result} tokens deleted (older than {days} days)."
    }


# ---------------------------
# NOTIFICATIONS (App + ESP32)
# ---------------------------
# --- POST notification by device_id (API key protected) ---
@app.post("/notifications/{device_id}")
async def debug_notification(
    device_id: str,
    x_api_key: str = Header(..., alias="X-API-Key"),
    request: Request = None,
):
    body = await request.json()
    print("Raw Notification payload:", body)
    return {"debug": body}


# @app.post("/notifications/{device_id}", response_model=schemas.NotificationRead)
# async def create_notification_by_device(
#     device_id: str,
#     notif: schemas.NotificationCreate,
#     x_api_key: str = Header(..., alias="X-API-Key"),
#     request: Request = None,  # add Request
# ):
#     # Debug: print raw JSON payload
#     body = await request.json()
#     print("Received Notification payload:", body)

#     # Validate device + API key
#     device = await database.fetch_one(
#         devices.select().where(devices.c.chip_id == device_id)
#     )
#     if not device or device["api_key"] != x_api_key:
#         raise HTTPException(status_code=401, detail="Invalid device API key")

#     new_notif = await crud.create_notification_by_device(
#         database,
#         device_id=device_id,
#         user_id=notif.user_id,
#         message=notif.message,
#         created_at=notif.created_at,
#     )

#     tokens = await crud.get_device_tokens_by_user(database, notif.user_id)
#     for token in tokens:
#         firebase_client.send_push(token, "Medication Reminder", notif.message)

#     return new_notif


@app.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: UUID):
    await crud.delete_notification(notification_id)
    return {"detail": "Notification deleted"}
