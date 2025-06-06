from fastapi import FastAPI
from .routers import users, posts
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog API (4lab)")

app.include_router(users.router)
app.include_router(posts.router)

@app.get("/ping")
def ping():
    return {"status": "ok"}
