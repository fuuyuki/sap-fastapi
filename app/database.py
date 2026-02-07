import os

from databases import Database
from sqlalchemy import MetaData, create_engine

# Load DATABASE_URL from environment (set in docker-compose.yml)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://fauxpg:kelapasawit1@db:5432/sapdb",  # fallback default
)

# Async database connection (used with FastAPI)
database = Database(DATABASE_URL)

# SQLAlchemy metadata for models
metadata = MetaData()

# SQLAlchemy engine (for migrations, synchronous queries, etc.)
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # number of connections to keep open
    max_overflow=20,  # extra connections allowed beyond pool_size
    echo=False,  # set True for SQL debug logging
)
