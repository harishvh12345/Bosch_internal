import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.api import api_router
from app.services.mcp.queue import process_simulation_queue

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static file routes for accessing simulation charts and uploaded documents
app.mount("/data/simulations", StaticFiles(directory=settings.SIMULATION_DIR), name="simulations")

# Include main versioned router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Global background tasks reference to avoid garbage collection
background_tasks = set()

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing application startup processes...")
    # Spawn background queue worker for MATLAB simulations
    loop = asyncio.get_event_loop()
    task = loop.create_task(process_simulation_queue())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    logger.info("MATLAB simulation background worker task started.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Performing application cleanup...")
    # Cancel all running tasks
    for task in background_tasks:
        task.cancel()
    logger.info("Clean shutdown completed.")

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "api_docs": "/docs"
    }
