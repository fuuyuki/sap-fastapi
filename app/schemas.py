from datetime import datetime, time
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, StringConstraints


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# 1. Users
class UserMe(BaseModel):
    user_id: UUID


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "patient"


class UserCreate(BaseModel):
    name: str
    email: str
    password_hash: Annotated[str, StringConstraints(min_length=8)]
    role: str = "patient"


class UserRead(UserBase):
    id: UUID


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None


class PasswordUpdate(BaseModel):
    new_password: str


# 2. Devices
class DeviceBase(BaseModel):
    chip_id: str
    name: str
    status: str = "offline"


# --- For creating devices ---
class DeviceCreate(BaseModel):
    chip_id: str
    user_id: UUID  # link to a user
    name: str
    status: str = "offline"


# class DeviceRead(DeviceCreate):
#     last_seen: datetime
#     api_key: str


class DeviceRead(BaseModel):
    chip_id: str
    user_id: UUID  # validated as UUID
    name: str
    status: str
    last_seen: datetime
    api_key: str


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    api_key: Optional[str] = None


class HeartbeatPayload(BaseModel):
    last_seen: str


# 3. Schedules
class ScheduleBase(BaseModel):
    pillname: str
    dose_time: time
    repeat_days: int = 0


class ScheduleCreate(ScheduleBase):
    user_id: UUID
    device_id: str


class ScheduleRead(ScheduleBase):
    id: UUID
    user_id: UUID
    device_id: str


class ScheduleUpdate(BaseModel):
    pillname: Optional[str] = None
    dose_time: Optional[time] = None
    repeat_days: Optional[int] = None


class BulkScheduleCreate(BaseModel):
    schedules: list[ScheduleCreate]


# 4. Medlogs
class MedlogBase(BaseModel):
    pillname: str
    scheduled_time: datetime
    status: str  # "taken" or "missed"


class MedlogCreate(MedlogBase):
    user_id: UUID
    device_id: str


class MedlogRead(MedlogBase):
    id: UUID
    user_id: UUID
    device_id: str


class MedlogUpdate(BaseModel):
    pillname: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None


# 5. Notifications
class NotificationBase(BaseModel):
    message: str


class NotificationCreate(NotificationBase):
    device_id: str
    user_id: UUID
    created_at: datetime


class NotificationRead(NotificationBase):
    id: UUID
    device_id: str
    user_id: UUID
    created_at: datetime


# 6. Device Tokens
class TokenRegisterRequest(BaseModel):
    user_id: UUID
    token: str


class DeviceTokenRead(BaseModel):
    id: int
    user_id: UUID
    token: str
    created_at: datetime


# 7. WiFi Configurations
class WiFiConfigBase(BaseModel):
    ssid: str
    password: str
    device_id: str


class WiFiConfigCreate(WiFiConfigBase):
    user_id: UUID
    device_id: str


class WiFiConfigOut(WiFiConfigBase):
    id: UUID
    user_id: UUID
    created_at: datetime


class DeleteResponse(BaseModel):
    message: str
