from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.common.settings import settings

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://admin:{settings.postgres_password}@postgres:5432/analytics"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
