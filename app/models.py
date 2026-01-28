from sqlalchemy import (
    TIMESTAMP,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .database import metadata

users = Table(
    "users",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    ),
    Column("name", String(100), nullable=False),
    Column("email", String(150), unique=True, nullable=False),
    Column("password", Text, nullable=False),
    Column("created_at", TIMESTAMP, server_default=func.now(), nullable=False),
)
devices = Table(
    "devices",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    ),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("name", String(100), nullable=False),
    Column("chip_id", String(100), unique=True, nullable=False),
    Column("paired_at", TIMESTAMP, server_default=func.now(), nullable=False),
)
schedules = Table(
    "schedules",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "device_id",
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("pillname", String(100), nullable=False),
    Column("dose_time", TIMESTAMP, nullable=False),
    Column("repeat_days", Integer, server_default="0"),
    Column("created_at", TIMESTAMP, server_default=func.now(), nullable=False),
)
medlogs = Table(
    "medlogs",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "device_id",
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("pillname", String(100)),
    Column("taken_at", TIMESTAMP, server_default=func.now(), nullable=False),
    Column("status", String(20), nullable=False),
    CheckConstraint("status IN ('taken','missed')", name="status_check"),
)
