import secrets

from sqlalchemy import (
    TIME,
    TIMESTAMP,
    UUID,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    func,
    text,
)

metadata = MetaData()


def generate_api_key():
    return secrets.token_hex(32)  # 64‑char secure random hex string


# 1. Users
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
    Column("email", String(100), unique=True, nullable=False),
    Column("password", String(255), nullable=False),
    Column("role", String(50), nullable=False),
    Column("caretaker_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=True),
    # Constraints
    CheckConstraint(
        "(role = 'patient' AND caretaker_id IS NOT NULL) "
        "OR (role = 'caretaker' AND caretaker_id IS NULL)",
        name="patient_caretaker_check",
    ),
    CheckConstraint("role IN ('caretaker','patient')", name="role_check"),
)

# 2. Devices
devices = Table(
    "devices",
    metadata,
    Column("chip_id", String(100), primary_key=True),
    Column("name", String(100), nullable=False),
    Column("status", String(50), server_default=text("'offline'")),
    Column(
        "last_seen",
        TIMESTAMP(timezone=True),
        server_default=text("now()"),
        nullable=False,
    ),
    Column("api_key", String(255), nullable=False),
    Column("patient_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
)

# 3. Schedules
schedules = Table(
    "schedules",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    ),
    Column("patient_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("device_id", String(100), ForeignKey("devices.chip_id"), nullable=False),
    Column("pillname", String(100), nullable=False),
    Column("dose_time", TIME(timezone=False), nullable=False),
    Column("repeat_days", Integer, default=0),
)

# 4. Medlogs
medlogs = Table(
    "medlogs",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    ),
    Column("patient_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("device_id", String(100), ForeignKey("devices.chip_id"), nullable=False),
    Column("pillname", String(100), nullable=False),
    Column("scheduled_time", TIMESTAMP(timezone=False), nullable=False),
    Column("status", String(50), nullable=False),  # "taken" or "missed"
)

# 5. Notifications
notifications = Table(
    "notifications",
    metadata,
    Column(
        "id",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    ),
    Column("device_id", String(100), ForeignKey("devices.chip_id"), nullable=False),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("message", String(255), nullable=False),
    Column(
        "created_at",
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        nullable=False,
    ),
)

# 6. Device Tokens (for push notifications)
device_tokens = Table(
    "device_tokens",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("token", String, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
