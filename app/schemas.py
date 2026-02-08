from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, StringConstraints


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# 1. Users
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "patient"


class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8)]


class UserRead(UserBase):
    id: UUID


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    password: Optional[str] = None


# 2. Devices
class DeviceBase(BaseModel):
    chip_id: str
    name: str
    status: str = "offline"


class DeviceCreate(BaseModel):
    chip_id: str
    user_id: UUID
    name: str
    status: str = "offline"


class DeviceRead(DeviceCreate):
    last_seen: datetime
    api_key: str


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    api_key: Optional[str] = None


# 3. Schedules
class ScheduleBase(BaseModel):
    pillname: str
    dose_time: datetime
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
    dose_time: Optional[datetime] = None
    repeat_days: Optional[int] = None


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
