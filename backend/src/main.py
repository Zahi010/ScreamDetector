"""Festival Scream Detector - Main FastAPI Application Entrypoint (Stage 8).

Integrates:
- Real-time streaming scream detection engine.
- REST API endpoints for status, config, metrics, events, and control.
- WebSocket broadcaster with per-client bounded queues.
- Localhost security, restricted CORS, and graceful lifespan management.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import (
    api_router,
    experimental_router,
    experimental_ws_router,
    get_multi_model_service,
    research_router,
    research_ws_router,
    review_router,
    setup_detector_websocket_bridge,
    setup_multi_model_bridge,
    websocket_router,
)
from src.config import BACKEND_HOST, BACKEND_PORT, CORS_ORIGINS
from src.detector.service import get_detector_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("festival-scream-detector")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycles."""
    loop = asyncio.get_running_loop()
    service = get_detector_service()
    multi_service = get_multi_model_service()

    # Bridge service event notifications to WebSockets
    setup_detector_websocket_bridge(service, loop)
    setup_multi_model_bridge(multi_service, loop)
    logger.info("FastAPI application initialized. WebSocket bridges active.")
    logger.info("Configured CORS origins: %s", CORS_ORIGINS)

    yield

    # Clean shutdown
    logger.info("FastAPI application shutting down. Gracefully stopping detectors...")
    service.stop()
    multi_service.stop_testing()
    logger.info("Detectors stopped. Lifespan shutdown complete.")


app = FastAPI(
    title="Festival Scream Detection API",
    description="Real-time acoustic surveillance and AI scream detection system for live festival security.",
    version="0.8.0",
    lifespan=lifespan,
)

# Restrict CORS to configured frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Register REST and WebSocket routers
app.include_router(api_router)
app.include_router(review_router)
app.include_router(websocket_router)
app.include_router(experimental_router)
app.include_router(experimental_ws_router)
app.include_router(research_router)
app.include_router(research_ws_router)


@app.get("/", tags=["Root"])
async def root():
    """System identity, service status, and API discovery."""
    return {
        "service": "Festival Scream Detection System",
        "stage": "Stage 8.9: Human Review Studio & Real-Time Dashboard",
        "status": "online",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "metrics": "/api/metrics",
            "config": "/api/config",
            "start": "/api/detector/start",
            "stop": "/api/detector/stop",
            "events": "/api/events",
            "devices": "/api/devices",
            "review_summary": "/api/review/summary",
            "review_recordings": "/api/review/recordings",
            "review_export": "/api/review/export.csv",
            "websocket": "/ws/events",
            "docs": "/docs",
        },
        "advisory": "POSSIBLE SCREAM DETECTION ADVISORY: Automated acoustic alerts require human auditory verification.",
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server on %s:%d", BACKEND_HOST, BACKEND_PORT)
    uvicorn.run("src.main:app", host=BACKEND_HOST, port=BACKEND_PORT, reload=True)
