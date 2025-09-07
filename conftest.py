import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models import User, Task
from auth import create_access_token

# Configuración de base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Crear las tablas
    Base.metadata.create_all(bind=engine)
    
    # Crear una nueva sesión para la prueba
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpiar las tablas después de la prueba
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    # Sobrescribir la dependencia de la base de datos
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "testpassword"
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def second_user(db_session):
    user = User(
        email="user2@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        full_name="Second User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def second_user_headers(second_user):
    token = create_access_token({"sub": second_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def task_factory(db_session, test_user):
    def _task_factory(**kwargs):
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium",
            "user_id": test_user.id,
            **kwargs
        }
        task = Task(**task_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task
    return _task_factory