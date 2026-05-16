import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.models_v2.base import Base  # noqa: F401 — single Base instance from shared submodule

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
async_session = SessionLocal  # alias for seed scripts


async def get_db():
    async with SessionLocal() as session:
        yield session
