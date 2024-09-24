from starlette import status

from tests.conftest import TestingSessionLocal, client
from todo_app.models.users import User


def test_return_user(dependencies_override, test_user):
    response = client.get('user')
    assert response.status_code == status.HTTP_200_OK

    user = response.json()
    assert user['username'] == 'shortyk'
    assert user['email'] == 'shortykofficial@gmail.com'
    assert user['first_name'] == 'Kirill'
    assert user['last_name'] == 'Dvoretsky'
    assert user['role'] == 'admin'
    assert user['phone_number'] == '89119540929'


def test_change_password(dependencies_override, test_user):
    response = client.put('user/change-password', json={
        'password': 'testpassword',
        'new_password': 'password',
        'confirm_password': 'password'
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_invalid_password(dependencies_override, test_user):
    response = client.put('user/change-password', json={
        'password': 'testpasswor',
        'new_password': 'password',
        'confirm_password': 'password'
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect password'}

    response = client.put('user/change-password', json={
        'password': 'testpassword',
        'new_password': 'password',
        'confirm_password': 'password1'
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'New password does not match confirmation password'}


def test_change_phone_number(dependencies_override, test_user):
    response = client.put('user/change-phone-number', json={'phone_number': '89119540930'})
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == 1).first()
    assert user.phone_number == '89119540930'

