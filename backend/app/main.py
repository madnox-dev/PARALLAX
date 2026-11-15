import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.config import settings, BASE_DIR
from app.database import init_db, SessionLocal
from app.auth.earthdata import auth_manager
from app.routers.nasa import router as nasa_router
from app.routers.analysis import router as analysis_router
from app.routers.jobs import router as jobs_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("parallax.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing PARALLAX backend...")
    init_db()
    status = auth_manager.authenticate()
    logger.info(
        "NASA Earthdata Initialization: %s (Status: %s)",
        status["status"],
        "Authenticated" if status["authenticated"] else "Demo/Public Search Active"
    )
    yield
    logger.info("Shutting down PARALLAX backend...")

app = FastAPI(
    title="PARALLAX API — NASA Earthdata Integration",
    version="1.0.0",
    description=(
        "Production backend for NASA Space Apps PARALLAX. "
        "Integrates OPERA L2 RTC-S1 and L3 DSWx-S1 satellite datasets, "
        "executes dual-signature radar backscatter flood/inundated-vegetation detection, "
        "and provides cross-sensor gap intelligence."
    ),
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for data directory (GeoJSON, rasters, cases)
if settings.DATA_DIR.exists():
    app.mount("/data", StaticFiles(directory=str(settings.DATA_DIR)), name="data")

# Register API Routers
app.include_router(nasa_router)
app.include_router(analysis_router)
app.include_router(jobs_router)

# Mount compiled production frontend if available
frontend_dist = BASE_DIR / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dist), html=True), name="frontend_app")
    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="frontend_assets")

@app.get("/")
def root():
    return {
        "service": "PARALLAX NASA Earthdata Service",
        "status": "online",
        "docs_url": "/docs",
        "app_url": "/app/",
        "supported_datasets": ["OPERA_L3_DSWX-S1_V1", "OPERA_L2_RTC-S1_V1", "NISAR_L2_PR_GCOV_001"]
    }

@app.get("/health")
@app.get("/api/health")
def healthcheck():
    return {
        "status": "healthy",
        "earthdata_configured": bool(settings.EARTHDATA_USERNAME and settings.EARTHDATA_PASSWORD),
        "demo_scenes_ready": True
    }

@app.get("/readiness")
@app.get("/api/readiness")
def readiness_check():
    """Validates real backend dependencies (database, storage, Earthdata service) rather than hardcoded response."""
    db_ok = False
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        logger.error(f"Readiness check failed for database: {e}")

    disk_ok = settings.DATA_DIR.exists() and os.access(str(settings.DATA_DIR), os.W_OK)
    ed_status = auth_manager.authenticate()

    is_ready = db_ok and disk_ok
    status_code = 200 if is_ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "dependencies": {
                "database": "connected" if db_ok else "disconnected",
                "storage": "writable" if disk_ok else "unwritable",
                "earthdata": ed_status["status"],
                "demo_scenes": "available" if (settings.CASES_DIR / "demo_flood_case").exists() else "missing"
            }
        }
    )
