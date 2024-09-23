from fastapi import FastAPI

from todo_app.database import engine, Base
from todo_app.routers import auth, todos, admin, users

app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.get('/healthy')
async def health_check():
    return {'status': 'healthy'}



@app.get("/items/")
async def read_items(q: str | None = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
