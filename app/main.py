from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

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

# Mount frontend static files
frontend_path = os.path.join(os.getcwd(), "frontend")
if os.path.exists(frontend_path):
    # Map /css and /js directly for easier reference in index.html
    app.mount("/css", StaticFiles(directory=os.path.join(frontend_path, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(frontend_path, "js")), name="js")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Return index.html for any path that doesn't start with /api or the static folders
    if not full_path.startswith("api") and not any(full_path.startswith(d) for d in ["css", "js", "assets"]):
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    return {"detail": "Not Found"}
