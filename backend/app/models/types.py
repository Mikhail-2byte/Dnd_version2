from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class GUID(TypeDecorator):
    """Cross-database GUID type compatible with PostgreSQL and SQLite"""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # as_uuid=True so psycopg2 exchanges uuid.UUID objects — required for
            # SQLAlchemy 2.x insertmanyvalues sentinel matching to work correctly.
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            # Return uuid.UUID so the type matches process_result_value output.
            if isinstance(value, uuid.UUID):
                return value
            try:
                return uuid.UUID(str(value))
            except (ValueError, TypeError):
                return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            try:
                uuid.UUID(str(value))
                return str(value)
            except (ValueError, TypeError):
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(value)
        except (ValueError, TypeError):
            return value

