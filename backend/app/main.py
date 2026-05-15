import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine
import app.models_v2  # noqa — registers all ORM models with Base.metadata

from app.modules.procurement_module.po_sub_module.routers.po_router import router as po_router
from app.modules.procurement_module.goods_receipt_sub_module.routers.grn_router import router as grn_router
from app.modules.procurement_module.material_link_sub_module.routers.material_link_router import router as ml_router
from app.modules.procurement_module.dashboard_sub_module.routers.dashboard_router import router as dashboard_router
from app.modules.identity_module.routers.person_router import router as identity_router
from app.routers.schedule_read_router import router as schedule_read_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("procurement")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Procurement module started")
    yield
    await engine.dispose()
    logger.info("Procurement module shutdown")


app = FastAPI(
    title="AI-PMS Procurement & Supply Module",
    description="Standalone procurement module — PO, GRN, Material Links, Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s  →  %d  (%.0fms)", request.method, request.url.path, response.status_code, ms)
    return response


PREFIX = "/api/v1"
app.include_router(po_router, prefix=PREFIX)
app.include_router(grn_router, prefix=PREFIX)
app.include_router(ml_router, prefix=PREFIX)
app.include_router(dashboard_router, prefix=PREFIX)
app.include_router(identity_router, prefix=PREFIX)
app.include_router(schedule_read_router, prefix=PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "procurement-module"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
