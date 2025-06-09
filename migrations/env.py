from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.models import Base
from app.models import Wallet, Transaction # noqa
from app.database import SQLALCHEMY_DATABASE_URL

config = context.config
script_location = config.get_main_option("script_location")
versions_path = os.path.join(script_location, "versions")

print(f"script_location: {script_location}")
print(f"versions_path: {versions_path}")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = (
            os.getenv("DATABASE_URL")
            or SQLALCHEMY_DATABASE_URL
    )


    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = (
            os.getenv("DATABASE_URL")
            or SQLALCHEMY_DATABASE_URL
    )

    connectable = create_engine(url, pool_pre_ping=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
