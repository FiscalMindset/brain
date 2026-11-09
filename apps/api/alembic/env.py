"""Alembic environment: reads DATABASE_URL from app config and uses Base.metadata."""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import create_engine, pool

from alembic import context

# Ensure the project root (apps/api) is importable so ``app`` resolves.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.models import models  # noqa: F401,E402  # ensure metadata is populated

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Prefer explicit ALEMBIC_URL / DATABASE_URL env override, else app settings.
config.set_main_option(
    "sqlalchemy.url",
    os.getenv("ALEMBIC_URL") or os.getenv("DATABASE_URL") or settings.DATABASE_URL,
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
