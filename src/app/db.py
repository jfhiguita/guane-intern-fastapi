import os

# SQLAlchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    Table
)

# SQL query builder
from sqlalchemy.sql import func

from databases import Database

DATABASE_URL = os.getenv("DATABASE_URL")

# sqlAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()
dogs = Table(
    "dogs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("picture", String(100)),
    Column("is_adopted", Boolean),
    Column("create_date", DateTime, default=func.now(), nullable=False),
)

# databases query builder
database = Database(DATABASE_URL)


