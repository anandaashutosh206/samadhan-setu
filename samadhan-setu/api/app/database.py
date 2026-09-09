from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# api/ package root — used to anchor relative sqlite paths so the DB resolves
# to the same file regardless of the working directory a script is run from
# (e.g. `cd api && uvicorn ...` vs `python scripts/seed.py` from repo root).
_API_ROOT = Path(__file__).resolve().parents[1]


def _resolve_database_url(url: str) -> str:
    prefix = "sqlite:///./"
    if url.startswith(prefix):
        relative_path = url[len(prefix):]
        absolute_path = (_API_ROOT / relative_path).resolve()
        return f"sqlite:///{absolute_path}"
    return url


DATABASE_URL = _resolve_database_url(settings.DATABASE_URL)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
