from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class DeviceIn(BaseModel):
    name: str
    chip_id: str


class DeviceOut(DeviceIn):
    id: UUID
    user_id: UUID
    paired_at: datetime


class ScheduleIn(BaseModel):
    device_id: UUID
    pillname: str
    dose_time: time
    repeat_days: int = 0


class ScheduleOut(ScheduleIn):
    id: UUID
    created_at: datetime


class MedlogIn(BaseModel):
    device_id: UUID
    pillname: str
    status: str  # must be "taken" or "missed"


class MedlogOut(MedlogIn):
    id: UUID
    user_id: UUID
    taken_at: datetime
