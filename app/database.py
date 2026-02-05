from databases import Database
from sqlalchemy import MetaData, create_engine

DATABASE_URL = "postgresql://fauxpg:kelapasawit1@db:5432/sapdb"

database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(DATABASE_URL)
