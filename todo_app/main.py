from typing import Annotated

from fastapi import FastAPI, Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from todo_app.database import engine, SessionLocal
from todo_app import models
from todo_app.models import Todo

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=35)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get('/todos', status_code=status.HTTP_200_OK)
async def index_todos(db: db_dependency):
    return db.query(Todo).all()


@app.get('/todos/{id}', status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail='Todo not found.')


@app.post('/todos', status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todo(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@app.put('/todos/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    for key, val in todo_request.model_dump().items():
        setattr(todo, key, val)

    db.add(todo)
    db.commit()


@app.delete('/todos/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: int = Path(gt=0)):
    todo = db.query(Todo).filter(Todo.id == id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.delete(todo)
    db.commit()
