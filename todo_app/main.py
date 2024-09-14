from fastapi import FastAPI

from todo_app.database import engine
from todo_app import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get('/')
async def index():
    return {'Hello': 'World'}
