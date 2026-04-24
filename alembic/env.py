import sys
import os
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from alembic import context
from sqlalchemy import engine_from_config, pool
from app.core.database import Base
# from app.models.models import ProcurementOrder
from app.models.layer0 import *
from app.models.layer1 import *
from app.models.layer4 import *


config = context.config
target_metadata = Base.metadata


def get_sync_url():
    """Convert async database URL to sync for migrations"""
    db_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    return db_url.replace("postgresql+asyncpg://", "postgresql://")


if context.is_offline_mode():
    url = get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_sync_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()
