from alembic.config import Config
from alembic import command
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()


def run_migrations():
    """Run alembic migrations (sync operation)"""
    alembic_cfg = Config("alembic.ini")
    db_url = os.getenv("DATABASE_URL")
    sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_db_url)
    command.upgrade(alembic_cfg, "head")


def init_db():
    """Initialize database with migrations on startup (runs in thread)"""
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(run_migrations).result()
        print("✓ Database migrations completed successfully")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise
