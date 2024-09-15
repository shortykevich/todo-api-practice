from fastapi import FastAPI

from todo_app import models
from todo_app.database import engine
from todo_app.routers import auth, todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
