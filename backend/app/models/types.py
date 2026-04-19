from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class GUID(TypeDecorator):
    """Cross-database GUID type compatible with PostgreSQL and SQLite"""
    impl = CHAR
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            # Для SQLite используем стандартный строковый формат UUID (с дефисами)
            if not isinstance(value, uuid.UUID):
                # Если уже строка, проверяем что это валидный UUID
                try:
                    uuid.UUID(value)
                    return value
                except (ValueError, TypeError):
                    return str(value)
            return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        # Конвертируем строку в UUID объект
        try:
            return uuid.UUID(value)
        except (ValueError, TypeError):
            # Если не удалось создать UUID, возвращаем как есть
            return value

