from sqlalchemy import MetaData
from sqlalchemy.schema import CreateTable

from app.models.dw_tables import Base


def get_all_ddl() -> dict[str, str]:
    """Generate DDL statements from ORM metadata with column comments."""
    ddls = {}
    for table in Base.metadata.sorted_tables:
        create = CreateTable(table)
        ddls[table.name] = str(create.compile(dialect=None)).strip() + ";"
    return ddls


def get_ddl_for_tables(table_names: list[str]) -> str:
    """Concatenate DDL for the given table names, used by NL2SQL schema injection."""
    metadata = Base.metadata
    parts = []
    for name in table_names:
        table = metadata.tables.get(name)
        if table is not None:
            create = CreateTable(table)
            parts.append(str(create.compile(dialect=None)).strip() + ";")
    return "\n\n".join(parts)
