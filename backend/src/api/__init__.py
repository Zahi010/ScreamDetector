"""FastAPI API module for Festival Scream Detector."""

from src.api.routes import router as api_router
from src.api.review_routes import router as review_router
from src.api.websocket import router as websocket_router, setup_detector_websocket_bridge
from src.api.experimental_routes import (
    router as experimental_router,
    ws_router as experimental_ws_router,
    setup_multi_model_bridge,
    get_multi_model_service,
)
from src.api.research_routes import (
    research_router,
    research_ws_router,
)

__all__ = [
    "api_router",
    "review_router",
    "websocket_router",
    "setup_detector_websocket_bridge",
    "experimental_router",
    "experimental_ws_router",
    "setup_multi_model_bridge",
    "get_multi_model_service",
    "research_router",
    "research_ws_router",
]

