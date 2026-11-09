"""Alembic migrations create the full schema."""

from pathlib import Path

import pytest
import sqlalchemy

alembic = pytest.importorskip("alembic")

from alembic.config import Config

from alembic import command
from app.core.database import Base

API_ROOT = Path(__file__).resolve().parent.parent


def test_migration_upgrade_creates_tables(tmp_path, monkeypatch):
    db_path = tmp_path / "migrated.db"
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("ALEMBIC_URL", url)

    cfg = Config(str(API_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(API_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url)

    command.upgrade(cfg, "head")

    engine = sqlalchemy.create_engine(url)
    inspector = sqlalchemy.inspect(engine)
    tables = set(inspector.get_table_names())
    assert set(Base.metadata.tables.keys()).issubset(tables)
    assert "users" in tables
    assert "sources" in tables
    assert "alembic_version" in tables
    engine.dispose()
