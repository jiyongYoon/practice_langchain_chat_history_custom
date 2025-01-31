from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg

from env import connection_path


# SQLAlchemy
engine = create_engine(connection_path)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# psycopg

def initialize_sync_connection():
    return psycopg.connect(connection_path)


async def initialize_async_connection():
    return await psycopg.AsyncConnection.connect(connection_path)
