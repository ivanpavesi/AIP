"""Alembic usa la stessa configurazione dell'app, senza collegamenti all'avvio web."""
from logging.config import fileConfig
from alembic import context
from app.core.config import get_settings
from app.db.base import Base
from app.db import models  # noqa: F401 — registra i modelli nel metadata
from app.db.session import get_engine

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# Esclude tabelle esterne (es. auth/storage Supabase) dalle future autogenerazioni.
def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name in (None, "identity_data", "clinical_data")
    if type_ == "table":
        return parent_names["schema_qualified_table_name"] in Base.metadata.tables
    return True


if context.is_offline_mode():
    url = get_settings().database_url
    # Solo compilazione SQL: URL privo di credenziali, nessuna connessione.
    context.configure(
        url=url.get_secret_value() if url else "postgresql+psycopg://localhost/aip",
        target_metadata=Base.metadata, literal_binds=True, dialect_opts={"paramstyle": "named"},
        include_schemas=True, include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata,
                          include_schemas=True, include_name=include_name, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
