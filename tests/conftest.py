import pytest
from sqlalchemy import text, create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from todo_app.main import app
from todo_app.database import Base, get_db
from todo_app.models.todos import Todo
from todo_app.models.users import User
from todo_app.utils.passwords import get_password_hash
from todo_app.utils.auth import get_current_user


DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_current_user():
    return {
        'username': 'shortyk',
        'id': 1,
        'role': 'admin'
    }


@pytest.fixture
def dependencies_override():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    yield client
    app.dependency_overrides = {}


@pytest.fixture
def dependencies_override_not_authenticated():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: None
    yield client
    app.dependency_overrides = {}


@pytest.fixture
def test_todo():
    todo = Todo(
        title='Learn to code!',
        description='Need to learn every day',
        priority=5,
        complete=False,
        owner_id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield db

    with engine.connect() as conn:
        conn.execute(text('DELETE FROM todos;'))
        conn.commit()


@pytest.fixture
def test_user():
    user = User(
        username='shortyk',
        email='shortykofficial@gmail.com',
        first_name='Kirill',
        last_name='Dvoretsky',
        hashed_password=get_password_hash('testpassword'),
        role='admin',
        phone_number='89119540929'
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as conn:
        conn.execute(text('DELETE FROM users;'))
        conn.commit()
