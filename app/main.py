from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.modules.procurement.routers.router import router as procurement_router
from app.core.migrations import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: run migrations
    init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(title="PMS Modular API", lifespan=lifespan)
app.include_router(procurement_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "running"}
