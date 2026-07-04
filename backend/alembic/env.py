from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
import sqlalchemy as sa
from alembic import context

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.models import target_metadata

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("sqlite:///", "sqlite:///").replace("sqlite://", "sqlite:///"))
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", db_path)
    config.set_main_option("sqlalchemy.url", "sqlite:///" + os.path.abspath(db_path))

def reflect_tables(connection):
    """Reflect existing tables from SQLite database."""
    target_metadata.clear()
    target_metadata.reflect(bind=connection)

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        reflect_tables(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_item=render_item,
        )
        with context.begin_transaction():
            context.run_migrations()

def render_item(type_, obj, autogen_context):
    if type_ == "type":
        if isinstance(obj, sa.Enum) and obj.name is not None:
            return f"sa.Enum('{obj.name}', name='{obj.name}')"
    return False

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
