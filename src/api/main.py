import sys
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from fastapi.exceptions import RequestValidationError # type: ignore
from fastapi.responses import JSONResponse # type: ignore

from api.routes import router, set_dependencies  # type: ignore
from api.websocket import ConnectionManager  # type: ignore
from db.database import Database  # type: ignore
from agent.scheduler import AgentScheduler  # type: ignore

# Critical: Set WindowsProactorEventLoopPolicy BEFORE any loop is created or other imports.
if sys.platform == "win32":
    try:
        from asyncio import WindowsProactorEventLoopPolicy, set_event_loop_policy
        set_event_loop_policy(WindowsProactorEventLoopPolicy())
    except ImportError:
        pass

from utils.logger import setup_logger # type: ignore

logger = setup_logger("api.main")

# Shared instances
db = Database()
ws_manager = ConnectionManager()
scheduler: AgentScheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown lifecycle."""
    global scheduler

    # Startup
    loop = asyncio.get_running_loop()
    logger.info(f"Starting DPS Agent Booking System... (Loop: {type(loop).__name__})")
    
    if sys.platform == "win32" and "Proactor" not in type(loop).__name__:
        logger.warning(f"CRITICAL: Event loop is {type(loop).__name__}, but ProactorEventLoop is required for Playwright on Windows!")

    await db.connect()
    logger.info("Database connected")

    scheduler = AgentScheduler(db, broadcast=ws_manager.broadcast)
    scheduler.start()
    logger.info("Scheduler started")

    set_dependencies(db, scheduler)

    # Resume any active jobs from the database
    active_jobs = await db.get_active_jobs()
    for job in active_jobs:
        logger.info(f"Resuming job: {job['id']}")
        await scheduler.start_job(job['id'])

    yield

    # Shutdown
    logger.info("Shutting down DPS Agent Booking System...")
    scheduler.stop()
    await db.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="DPS Agent Booking System",
    description="Intelligent, autonomous Texas DPS appointment booking agent",
    version="2.0.0",
    lifespan=lifespan,
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router)


# ─── WebSocket Endpoint ─────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time job status updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            # Echo back as acknowledgment
            await ws_manager.send_personal(websocket, {
                "type": "ack",
                "message": f"Received: {data}"
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.debug(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# ─── Serve Frontend (production) ─────────────────────────────────

frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn  # type: ignore
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
