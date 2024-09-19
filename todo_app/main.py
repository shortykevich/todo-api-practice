from fastapi import FastAPI

from todo_app.database import engine, Base
from todo_app.routers import auth, todos, admin, users

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
