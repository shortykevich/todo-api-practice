import pytest
from jose import jwt
from datetime import timedelta
from fastapi import HTTPException
from starlette import status

from todo_app.models.users import User
from tests.conftest import TestingSessionLocal, client
from todo_app.utils.auth import (
    authenticate_user,
    SECRET_KEY,
    ALGORITHM,
    create_access_token,
    get_current_user
)


def test_authenticate_user(dependencies_override_not_authenticated, test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existing_user = authenticate_user('wrong', 'user', db)
    assert non_existing_user is False

    wrong_password_user = authenticate_user(test_user.username, 'testpassword1', db)
    assert wrong_password_user is False


def test_create_access_token(test_user):
    token = create_access_token(
        test_user.username,
        test_user.id,
        test_user.role,
        timedelta(days=1)
    )
    decoded_token = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={'verify_signature': False}
    )
    assert decoded_token['sub'] == test_user.username
    assert decoded_token['id'] == test_user.id
    assert decoded_token['role'] == test_user.role


@pytest.mark.asyncio
async def test_get_current_user(test_user):
    encode = {
        'sub': test_user.username,
        'id': test_user.id,
        'role': test_user.role
    }
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    user = await get_current_user(token)
    assert user == {
        'username': test_user.username,
        'id': test_user.id,
        'role': test_user.role
    }


@pytest.mark.asyncio
async def test_get_current_user_invalid(test_user):
    encode = {}
    token = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    with pytest.raises(HTTPException) as e:
        await get_current_user(token)

    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.detail == 'Invalid credentials'


def test_user_create(dependencies_override_not_authenticated, test_user):
    response = client.post('/auth', json={
        'username': 'testuser',
        'email': 'test@gmail.com',
        'first_name': 'test',
        'last_name': 'user',
        'role': 'user',
        'password': 'Passw0rd!',
        'phone_number': '+7(800)555-35-35',
    })
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    created_user = db.query(User).filter(User.username == 'testuser').first()
    assert created_user is not None
    assert created_user.username == 'testuser'
    assert created_user.email == 'test@gmail.com'
    assert created_user.first_name == 'test'
    assert created_user.last_name == 'user'
    assert created_user.phone_number == 'tel:+7-800-555-35-35'
    assert created_user.is_active is True
    assert created_user.role == 'user'


def test_authenticattion(dependencies_override_not_authenticated, test_user):
    response = client.post('/auth/token', data={
        'username': 'shortyk',
        'password': 'testpassword',
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['access_token'] is not None
    assert response.json()['token_type'] is not None


def test_wrong_authentication(dependencies_override_not_authenticated, test_user):
    response = client.post('/auth/token', data={
            'username': 'wrongusername',
            'password': 'wrongpassword',
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['detail'] == 'Invalid credentials'
