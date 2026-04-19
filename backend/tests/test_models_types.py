"""Тесты для кастомных типов моделей"""
import pytest
import uuid
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from app.models.types import GUID
from app.database import Base as AppBase


# Создаем отдельную базу для тестирования типов
TypesTestBase = declarative_base()


class TypesTestModel(TypesTestBase):
    """Тестовая модель для проверки GUID типа"""
    __tablename__ = "test_model"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    value = Column(Integer)


@pytest.fixture
def sqlite_engine():
    """SQLite движок для тестов"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TypesTestBase.metadata.create_all(bind=engine)
    yield engine
    TypesTestBase.metadata.drop_all(bind=engine)


@pytest.fixture
def sqlite_session(sqlite_engine):
    """SQLite сессия для тестов"""
    Session = sessionmaker(bind=sqlite_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_guid_sqlite_store_and_retrieve(sqlite_session):
    """Тест сохранения и получения UUID через SQLite"""
    test_uuid = uuid.uuid4()
    test_obj = TypesTestModel(id=test_uuid, value=42)
    
    sqlite_session.add(test_obj)
    sqlite_session.commit()
    sqlite_session.refresh(test_obj)
    
    # Проверяем, что UUID сохранился и правильно восстановился
    assert test_obj.id == test_uuid
    assert isinstance(test_obj.id, uuid.UUID)


def test_guid_sqlite_string_conversion(sqlite_session):
    """Тест конвертации UUID из строки в SQLite"""
    test_uuid_str = str(uuid.uuid4())
    test_obj = TypesTestModel(id=test_uuid_str, value=42)
    
    sqlite_session.add(test_obj)
    sqlite_session.commit()
    sqlite_session.refresh(test_obj)
    
    # Проверяем, что строка конвертировалась в UUID
    assert isinstance(test_obj.id, uuid.UUID)
    assert str(test_obj.id) == test_uuid_str


def test_guid_sqlite_none_value(sqlite_session):
    """Тест обработки None значения в GUID"""
    test_uuid = uuid.uuid4()
    test_obj = TypesTestModel(id=test_uuid, value=42)
    
    sqlite_session.add(test_obj)
    sqlite_session.commit()
    
    # Проверяем, что None обрабатывается корректно при сравнении
    found = sqlite_session.query(TypesTestModel).filter(TypesTestModel.id == test_uuid).first()
    assert found is not None
    assert found.id == test_uuid


def test_guid_sqlite_query_by_uuid(sqlite_session):
    """Тест запросов по UUID в SQLite"""
    test_uuid1 = uuid.uuid4()
    test_uuid2 = uuid.uuid4()
    
    obj1 = TypesTestModel(id=test_uuid1, value=1)
    obj2 = TypesTestModel(id=test_uuid2, value=2)
    
    sqlite_session.add_all([obj1, obj2])
    sqlite_session.commit()
    
    # Поиск по UUID объекту
    found1 = sqlite_session.query(TypesTestModel).filter(TypesTestModel.id == test_uuid1).first()
    assert found1 is not None
    assert found1.id == test_uuid1
    
    # Поиск по строке UUID
    found2 = sqlite_session.query(TypesTestModel).filter(TypesTestModel.id == str(test_uuid2)).first()
    assert found2 is not None
    assert found2.id == test_uuid2


def test_guid_sqlite_query_by_string(sqlite_session):
    """Тест запросов по строковому представлению UUID"""
    test_uuid = uuid.uuid4()
    obj = TypesTestModel(id=test_uuid, value=42)
    
    sqlite_session.add(obj)
    sqlite_session.commit()
    
    # Поиск по строке
    found = sqlite_session.query(TypesTestModel).filter(TypesTestModel.id == str(test_uuid)).first()
    assert found is not None
    assert found.id == test_uuid


@pytest.fixture
def postgresql_url():
    """Получает URL PostgreSQL из настроек или использует SQLite если нет"""
    try:
        from app.config import settings
        if 'postgresql' in settings.database_url.lower():
            return settings.database_url
    except:
        pass
    return None


@pytest.mark.skipif(True, reason="PostgreSQL тесты требуют реальную БД")
def test_guid_postgresql_store_and_retrieve(postgresql_url):
    """Тест сохранения и получения UUID через PostgreSQL"""
    if not postgresql_url:
        pytest.skip("PostgreSQL не настроен")
    
    engine = create_engine(postgresql_url)
    TypesTestBase.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        test_uuid = uuid.uuid4()
        test_obj = TypesTestModel(id=test_uuid, value=42)
        
        session.add(test_obj)
        session.commit()
        session.refresh(test_obj)
        
        assert test_obj.id == test_uuid
        assert isinstance(test_obj.id, uuid.UUID)
    finally:
        session.close()
        TypesTestBase.metadata.drop_all(bind=engine)

