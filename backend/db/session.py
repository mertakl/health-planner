from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel
from sqlmodel import create_engine

from backend.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False}  # for SQLite
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
