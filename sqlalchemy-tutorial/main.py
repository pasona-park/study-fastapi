from fastapi import FastAPI
from seed import init_db

from routers import router

init_db()

app = FastAPI(title="FastAPI Tutorial")
app.include_router(router)
