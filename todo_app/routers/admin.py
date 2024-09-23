from typing import Annotated
from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status
from starlette.exceptions import HTTPException

from todo_app.models.todos import Todo
from todo_app.models.users import User
from todo_app.database import db_dependency
from todo_app.utils.auth import get_current_user


router = APIRouter(
    prefix='/admin',
    tags=['admin'],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/todos', status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User unauthorized')
    return db.query(Todo).all()


@router.delete('/todos/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='User unauthorized')

    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Todo not found')
    db.delete(todo)
    db.commit()
