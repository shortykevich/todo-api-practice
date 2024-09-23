from fastapi import status

from todo_app.models.todos import Todo
from tests.conftest import client, TestingSessionLocal


def test_read_all():
    response = client.get('/todos/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': 1,
        'title': 'Learn to code!',
        'description': 'Need to learn every day',
        'priority': 5,
        'complete': False,
        'owner_id': 1
    }]


def test_read_one_not_found():
    response = client.get('/todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}


def test_add_todo():
    todo_request = {
        'title': 'Wash your car',
        'description': 'It\' now or never!',
        'priority': 3,
        'complete': False,
    }
    response = client.post('/todos/', json=todo_request)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 2).first()
    for field, value in todo_request.items():
        assert getattr(model, field) == value


def test_update_todo():
    todo_request = {
        'title': 'Learn to code!',
        'description': 'Need to learn every day',
        'priority': 5,
        'complete': True,
    }
    response = client.put('/todos/1', json=todo_request)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model.complete is True


def test_update_todo_not_found():
    todo_request = {
        'title': 'Learn to code!',
        'description': 'Need to learn every day',
        'priority': 5,
        'complete': True,
    }
    response = client.put('/todos/999', json=todo_request)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_todo():
    response = client.delete('todos/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
