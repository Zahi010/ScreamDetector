"""WebSocket Broadcaster & Connection Manager (Stage 8).

Provides real-time event, telemetry, and status broadcasting to connected React clients:
- Delivers initial snapshot upon connection.
- Uses bounded per-client asyncio queues (maxsize=100) to ensure slow or stalled clients
  can never block audio capture, ML inference, or other connected dashboard clients.
- Automatically discards oldest telemetry updates when a client queue is full.
- Thread-safe bridging from background audio worker thread into asyncio event loop.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.detector.service import DetectorService, get_detector_service

logger = logging.getLogger("api_websocket")

router = APIRouter(tags=["WebSocket"])


class WebSocketClient:
    """State and bounded outbound queue for a single connected dashboard client."""

    def __init__(self, websocket: WebSocket, max_queue_size: int = 100):
        self.websocket = websocket
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=max_queue_size)
        self.dropped_count: int = 0
        self.sender_task: Optional[asyncio.Task] = None
        try:
            self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

    async def run_sender(self) -> None:
        """Continuously pull messages from queue and send over WebSocket."""
        try:
            while True:
                message = await self.queue.get()
                await self.websocket.send_text(json.dumps(message))
                self.queue.task_done()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"Client sender task terminated: {e}")

    def enqueue_message(self, message: Dict[str, Any]) -> None:
        """Enqueue message without blocking. Drops oldest message if queue is full."""
        if self.queue.full():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
                self.dropped_count += 1
            except (asyncio.QueueEmpty, ValueError):
                pass

        try:
            self.queue.put_nowait(message)
        except asyncio.QueueFull:
            self.dropped_count += 1


class ConnectionManager:
    """Manages active WebSocket connections with non-blocking broadcasting."""

    def __init__(self):
        self.active_clients: Set[WebSocketClient] = set()
        self._lock = asyncio.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Store reference to running event loop for cross-thread scheduling."""
        self._loop = loop

    async def connect(self, websocket: WebSocket) -> WebSocketClient:
        """Accept new WebSocket connection and initialize client worker."""
        await websocket.accept()
        client = WebSocketClient(websocket)
        client.sender_task = asyncio.create_task(client.run_sender())

        async with self._lock:
            self.active_clients.add(client)

        logger.info(f"WebSocket client connected. Active clients: {len(self.active_clients)}")
        return client

    async def disconnect(self, client: WebSocketClient) -> None:
        """Remove and clean up disconnected client."""
        async with self._lock:
            self.active_clients.discard(client)

        if client.sender_task and not client.sender_task.done():
            client.sender_task.cancel()

        logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.active_clients)}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all active clients non-blockingly."""
        async with self._lock:
            clients = list(self.active_clients)

        for client in clients:
            client.enqueue_message(message)

    def dispatch_from_thread(self, message: Dict[str, Any]) -> None:
        """Thread-safe dispatch from audio inference thread into active client event loops."""
        clients = list(self.active_clients)
        for client in clients:
            try:
                client.loop.call_soon_threadsafe(client.enqueue_message, message)
            except Exception as e:
                logger.debug(f"Error dispatching to client: {e}")


# Global connection manager
manager = ConnectionManager()


def setup_detector_websocket_bridge(service: DetectorService, loop: asyncio.AbstractEventLoop) -> None:
    """Connect DetectorService event notifications to the WebSocket connection manager."""
    manager.set_event_loop(loop)
    service.set_async_loop(loop)

    def _on_detector_event(event: Dict[str, Any]) -> None:
        manager.dispatch_from_thread(event)

    service.add_listener(_on_detector_event)
    logger.info("DetectorService hooked to WebSocket ConnectionManager.")


@router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    """Real-time event and telemetry WebSocket endpoint."""
    client = await manager.connect(websocket)
    detector_service = get_detector_service()

    try:
        # Send initial snapshot immediately upon connection
        status_snapshot = detector_service.get_status()
        metrics_snapshot = detector_service.get_metrics()

        initial_msg = {
            "type": "initial_snapshot",
            "timestamp": datetime.now().isoformat(),
            "connection_status": "connected",
            "status": status_snapshot,
            "metrics": metrics_snapshot,
            "active_event": status_snapshot.get("active_event"),
            "disclaimer": "POSSIBLE SCREAM DETECTION ADVISORY: Automated acoustic alerts require human auditory verification.",
        }
        client.enqueue_message(initial_msg)

        # Receive loop for keepalive pings or client messages
        while True:
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
                if data.get("type") == "ping":
                    client.enqueue_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat(),
                    })
                elif data.get("type") == "request_status":
                    client.enqueue_message({
                        "type": "status_response",
                        "timestamp": datetime.now().isoformat(),
                        "status": detector_service.get_status(),
                        "metrics": detector_service.get_metrics(),
                    })
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        await manager.disconnect(client)
    except Exception as e:
        logger.debug(f"WebSocket client session terminated: {e}")
        await manager.disconnect(client)
