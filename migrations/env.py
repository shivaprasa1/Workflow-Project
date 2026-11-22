
from logging.config import fileConfig

from alembic import context

from app.database.database import Base, DATABASE_URL

# Import all models so SQLAlchemy registers their tables.
from app.models.user import User
from app.models.task import Task
from app.models.notification import Notification


from app.models.user import User
from app.models.task import Task
from app.models.notification import Notification

from app.models.device_token import DeviceToken


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Tell Alembic which SQLAlchemy models to compare.
target_metadata = Base.metadata


# Use the database URL from the existing .env configuration.
database_url = DATABASE_URL.render_as_string(
    hide_password=False
)

# Escape percent signs for ConfigParser.
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%")
)


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live database connection."""

    from sqlalchemy import create_engine

    connectable = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
