from typing import Annotated
from fastapi import APIRouter, Path
from fastapi.params import Depends
from starlette import status
from starlette.exceptions import HTTPException

from todo_app.models.users import User
from todo_app.models.todos import Todo
from todo_app.schemas.todos import TodoRequest
from todo_app.database import db_dependency
from todo_app.utils.auth import get_current_user


router = APIRouter(
    prefix='/todos',
    tags=['todos']
)
user_dependency = Annotated[User, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def index_todos(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed')

    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()


@router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed')

    todo = (
        db.query(Todo)
        .filter(Todo.id == id)
        .filter(Todo.owner_id == user.get('id'))
        .first()
    )
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail='Todo not found.')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed')

    todo_model = Todo(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()


@router.put('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed')

    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    for key, val in todo_request.model_dump().items():
        setattr(todo, key, val)

    db.add(todo)
    db.commit()


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication failed')

    todo = (
        db.query(Todo)
        .filter(Todo.id == id)
        .filter(Todo.owner_id == user.get('id'))
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.delete(todo)
    db.commit()
