from starlette import status

from todo_app.models.todos import Todo
from tests.conftest import TestingSessionLocal, client


def test_admin_get_all_todos():
    response = client.get('/admin/todos')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'title': 'Learn to code!',
        'description': 'Need to learn every day',
        'priority': 5,
        'complete': False,
        'owner_id': 1,
        'id': 1
    }]


def test_admin_delete():
    response = client.delete('/admin/todos/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo = db.query(Todo).filter(Todo.id == 1).first()
    assert todo is None


def test_admin_delete_not_found():
    response = client.delete('/admin/todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
