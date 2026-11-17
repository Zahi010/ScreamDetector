"""FastAPI REST & WebSocket Endpoints for Multi-Model Live Audio Testing Lab.

Provides isolated experimental endpoints:
- GET  /api/experimental/live/models
- POST /api/experimental/live/start
- POST /api/experimental/live/stop
- GET  /api/experimental/live/status
- POST /api/experimental/live/config
- POST /api/experimental/live/session/start
- POST /api/experimental/live/session/stop
- POST /api/experimental/live/review
- GET  /api/experimental/live/session/{session_id}
- GET  /api/experimental/live/sessions
- POST /api/experimental/live/simulate-audio
- WebSocket /ws/experimental/multi-model
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import numpy as np
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field

from src.detector.mic_capture import list_audio_input_devices
from src.experimental.multi_model_engine import (
    MultiModelLiveEngine,
    MultiModelLiveService,
)
from src.experimental.session_store import ExperimentalSessionStore

logger = logging.getLogger("experimental_routes")

router = APIRouter(prefix="/api/experimental/live", tags=["Experimental Multi-Model Lab"])
ws_router = APIRouter(tags=["Experimental WebSocket"])

_service_instance: Optional[MultiModelLiveService] = None
_service_lock = threading.Lock()


def get_multi_model_service() -> MultiModelLiveService:
    """Return thread-safe singleton MultiModelLiveService."""
    global _service_instance
    with _service_lock:
        if _service_instance is None:
            engine = MultiModelLiveEngine()
            store = ExperimentalSessionStore()
            _service_instance = MultiModelLiveService(engine=engine, session_store=store)
        return _service_instance


# -----------------------------------------------------------------------------
# Request & Response Schemas
# -----------------------------------------------------------------------------

class StartLabRequest(BaseModel):
    device_index: Optional[int] = Field(None, description="Optional audio input device index")
    session_notes: Optional[str] = Field("", description="Optional notes for the testing session")
    enabled_models: Optional[List[str]] = Field(None, description="List of model IDs to enable")


class ToggleModelConfigRequest(BaseModel):
    model_id: str = Field(..., description="Target model ID")
    enabled: bool = Field(..., description="Enable or disable flag")


class ToggleAcousticGateRequest(BaseModel):
    enabled: bool = Field(..., description="Enable or disable the acoustic activity gate")
    rms_threshold: Optional[float] = Field(None, description="RMS silence cutoff threshold (default 0.0035)")
    peak_threshold: Optional[float] = Field(None, description="Peak silence cutoff threshold (default 0.010)")


class StartSessionRequest(BaseModel):
    notes: str = Field("", description="Session test plan or notes")
    enabled_models: Optional[List[str]] = Field(None, description="List of model IDs active in session")


class HumanReviewRequest(BaseModel):
    session_id: str = Field(..., description="Experimental session ID")
    event_id: str = Field(..., description="Candidate event ID")
    window_start_idx: int = Field(..., description="Start window index")
    window_end_idx: int = Field(..., description="End window index")
    timestamp_start: float = Field(..., description="Start timestamp")
    timestamp_end: float = Field(..., description="End timestamp")
    ground_truth_label: str = Field(..., description="SCREAM, NON_SCREAM, or AMBIGUOUS")
    sound_class: Optional[str] = Field("", description="screaming, cheering, shout, music, speech, synthetic")
    reviewer_notes: Optional[str] = Field("", description="Notes on auditory characteristics")


class SimulateAudioRequest(BaseModel):
    signal_type: str = Field("scream_burst", description="scream_burst, high_pitch_shout, crowd_noise, silence, chirp")
    duration_seconds: float = Field(1.5, ge=0.5, le=10.0, description="Audio duration in seconds")
    amplitude: float = Field(0.5, ge=0.01, le=1.0, description="Amplitude scaling factor")


# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------

@router.get(
    "/models",
    summary="List Registered Experimental & Baseline Models",
    description="Retrieve all candidate models with thresholds, feature dimensions, SHA-256 hashes, and statuses.",
)
async def get_registered_models():
    service = get_multi_model_service()
    models = service.engine.get_models_overview()
    audit = service.engine.registry.get_audit_dict()
    return {
        "status": "success",
        "primary_model_id": "D_V4_FAMILY_A",
        "production_model_id": "PRODUCTION_BASELINE",
        "models": models,
        "audit": audit,
    }


@router.get(
    "/status",
    summary="Multi-Model Lab Health & Stream Status",
    description="Get live stream state, microphone availability, active session ID, uptime, and buffer stats.",
)
async def get_lab_status():
    service = get_multi_model_service()
    status_dict = service.get_status()
    devices = list_audio_input_devices()
    return {
        "status": "success",
        "lab_status": status_dict,
        "audio_devices": devices,
    }


@router.post(
    "/start",
    summary="Start Shared Microphone Capture & Multi-Model Inference",
    description="Begins real-time evaluation across all enabled models on the single audio stream.",
)
async def start_lab(req: StartLabRequest):
    service = get_multi_model_service()

    # Optional model toggles
    if req.enabled_models is not None:
        for mid in service.engine.registry.list_models():
            service.engine.set_model_enabled(mid.model_id, mid.model_id in req.enabled_models)

    # Start optional formal session
    sess_id = service.session_store.start_session(
        enabled_models=[m for m, en in service.engine.enabled_models.items() if en],
        notes=req.session_notes or "Live testing session",
    )
    service.active_session_id = sess_id

    result = service.start_testing(device_index=req.device_index)
    return {
        "status": "success",
        "session_id": sess_id,
        "details": result,
    }


@router.post(
    "/stop",
    summary="Stop Multi-Model Live Audio Testing",
    description="Gracefully halts microphone capture and closes active experimental session.",
)
async def stop_lab():
    service = get_multi_model_service()
    result = service.stop_testing()
    return {
        "status": "success",
        "details": result,
    }


@router.post(
    "/config",
    summary="Configure Active Models",
    description="Enable or disable individual comparison models without restarting capture.",
)
async def toggle_model_config(req: ToggleModelConfigRequest):
    service = get_multi_model_service()
    success = service.engine.set_model_enabled(req.model_id, req.enabled)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model ID '{req.model_id}' not found in registry.",
        )
    return {
        "status": "success",
        "model_id": req.model_id,
        "enabled": req.enabled,
        "enabled_models": service.engine.enabled_models,
    }


@router.post(
    "/acoustic-gate",
    summary="Configure Acoustic Activity Gate",
    description="Toggle acoustic activity gate or adjust RMS / peak silence thresholds for diagnostic mode.",
)
async def configure_acoustic_gate(req: ToggleAcousticGateRequest):
    service = get_multi_model_service()
    service.engine.set_acoustic_gate(
        enabled=req.enabled,
        rms_threshold=req.rms_threshold,
        peak_threshold=req.peak_threshold,
    )
    return {
        "status": "success",
        "acoustic_gate": {
            "enabled": service.engine.acoustic_gate_enabled,
            "rms_threshold": service.engine.acoustic_gate_rms_threshold,
            "peak_threshold": service.engine.acoustic_gate_peak_threshold,
        },
    }


@router.post(
    "/session/start",
    summary="Start Formal Testing Session",
    description="Creates a new experimental session record in database/experimental_sessions.db.",
)
async def start_session(req: StartSessionRequest):
    service = get_multi_model_service()
    enabled = req.enabled_models or [m for m, en in service.engine.enabled_models.items() if en]
    sess_id = service.session_store.start_session(enabled_models=enabled, notes=req.notes)
    service.active_session_id = sess_id
    return {"status": "success", "session_id": sess_id}


@router.post(
    "/session/stop",
    summary="Stop Current Testing Session",
    description="Finalizes active session and computes review metrics.",
)
async def stop_session():
    service = get_multi_model_service()
    sess_id = service.active_session_id
    if not sess_id:
        return {"status": "warning", "message": "No active session to stop"}

    service.session_store.stop_session(
        sess_id,
        total_windows=service.window_counter,
        dropped_windows=service.dropped_windows_total,
    )
    service.active_session_id = None
    session_data = service.session_store.get_session(sess_id)
    return {"status": "success", "session": session_data}


@router.post(
    "/review",
    summary="Submit Human Ground-Truth Label for an Event",
    description="Records human verification for an acoustic event to calculate non-fabricated live metrics.",
)
async def submit_human_review(req: HumanReviewRequest):
    service = get_multi_model_service()
    rev_id = service.session_store.add_human_review(
        session_id=req.session_id,
        event_id=req.event_id,
        window_start_idx=req.window_start_idx,
        window_end_idx=req.window_end_idx,
        timestamp_start=req.timestamp_start,
        timestamp_end=req.timestamp_end,
        ground_truth_label=req.ground_truth_label,
        sound_class=req.sound_class or "",
        reviewer_notes=req.reviewer_notes or "",
    )
    # Update event verification status in service history
    for evt in service._event_history:
        if evt.get("event_id") == req.event_id:
            evt["verification_status"] = req.ground_truth_label.upper()
            evt["human_notes"] = req.reviewer_notes

    metrics = service.session_store.compute_session_metrics(req.session_id)
    return {
        "status": "success",
        "review_id": rev_id,
        "session_metrics": metrics,
    }


@router.get(
    "/session/{session_id}",
    summary="Get Session Details & Review Metrics",
    description="Retrieve session metadata, reviewed events, and calculated event-level metrics.",
)
async def get_session(session_id: str):
    service = get_multi_model_service()
    data = service.session_store.get_session(session_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experimental session '{session_id}' not found.",
        )
    return {"status": "success", "session": data}


@router.get(
    "/sessions",
    summary="List Past Experimental Sessions",
    description="List historical live testing sessions with review counts.",
)
async def list_sessions(limit: int = Query(50, ge=1, le=100)):
    service = get_multi_model_service()
    sessions = service.session_store.list_sessions(limit=limit)
    return {"status": "success", "sessions": sessions}


@router.get(
    "/events",
    summary="Get Recent Candidate Events",
    description="Retrieve candidate scream events detected in the current testing lab run.",
)
async def get_events(limit: int = Query(50, ge=1, le=100)):
    service = get_multi_model_service()
    return {"status": "success", "events": service.get_event_history(limit=limit)}


@router.get(
    "/history",
    summary="Recent Synchronized Window Predictions",
    description="Retrieve last N synchronized multi-model window predictions.",
)
async def get_window_history(limit: int = Query(50, ge=1, le=100)):
    service = get_multi_model_service()
    return {"status": "success", "windows": service.get_window_history(limit=limit)}


@router.post(
    "/simulate-audio",
    summary="Inject Synthetic or Preset Audio for Testing",
    description="Pushes synthetic audio samples (screams, shouts, crowd, silence) into the shared buffer.",
)
async def simulate_audio(req: SimulateAudioRequest):
    service = get_multi_model_service()
    sr = service.sample_rate
    n_samples = int(sr * req.duration_seconds)
    t = np.linspace(0, req.duration_seconds, n_samples, endpoint=False)

    if req.signal_type == "scream_burst":
        # Frequency modulated acoustic scream simulation (1500 Hz - 3200 Hz with roughness)
        carrier = np.sin(2 * np.pi * (1800 + 800 * np.sin(2 * np.pi * 7 * t)) * t)
        roughness = np.sin(2 * np.pi * 95 * t)  # Subharmonic roughness
        envelope = np.exp(-((t - req.duration_seconds * 0.4) ** 2) / 0.15)
        wave = carrier * (1.0 + 0.3 * roughness) * envelope * req.amplitude
    elif req.signal_type == "high_pitch_shout":
        # Formant-based vocal shout (800 Hz fundamental + strong 2nd/3rd harmonics)
        wave = (
            np.sin(2 * np.pi * 850 * t)
            + 0.5 * np.sin(2 * np.pi * 1700 * t)
            + 0.25 * np.sin(2 * np.pi * 2550 * t)
        )
        envelope = np.exp(-((t - req.duration_seconds * 0.5) ** 2) / 0.4)
        wave = wave * envelope * req.amplitude * 0.6
    elif req.signal_type == "crowd_noise":
        # Low-pass pink noise with random chatter bursts
        noise = np.random.randn(n_samples)
        wave = np.convolve(noise, np.ones(25) / 25, mode="same") * req.amplitude * 0.3
    elif req.signal_type == "chirp":
        # Linear sweep 300 Hz -> 4000 Hz
        freq = np.linspace(300, 4000, n_samples)
        wave = np.sin(2 * np.pi * freq * t) * req.amplitude * 0.4
    else:  # silence
        wave = (np.random.randn(n_samples) * 0.001 * req.amplitude).astype(np.float32)

    wave = wave.astype(np.float32)
    service.feed_audio(wave)

    return {
        "status": "success",
        "signal_type": req.signal_type,
        "duration_seconds": req.duration_seconds,
        "samples_injected": len(wave),
        "buffer_stats": service.get_status()["buffer_stats"],
    }


# -----------------------------------------------------------------------------
# WebSocket Implementation
# -----------------------------------------------------------------------------

class MultiModelWSClient:
    """Manages outbound bounded queue for a connected multi-model lab dashboard."""

    def __init__(self, ws: WebSocket, maxsize: int = 100):
        self.ws = ws
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=maxsize)
        self.sender_task: Optional[asyncio.Task] = None

    async def run(self) -> None:
        try:
            while True:
                msg = await self.queue.get()
                await self.ws.send_text(json.dumps(msg))
                self.queue.task_done()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug("MultiModelWSClient sender task finished: %s", e)

    def enqueue(self, msg: Dict[str, Any]) -> None:
        if self.queue.full():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except (asyncio.QueueEmpty, ValueError):
                pass
        try:
            self.queue.put_nowait(msg)
        except asyncio.QueueFull:
            pass


class MultiModelConnectionManager:
    """Connection manager for Multi-Model Lab WebSocket broadcaster."""

    def __init__(self):
        self.clients: Set[MultiModelWSClient] = set()
        self._lock = asyncio.Lock()
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop

    async def connect(self, ws: WebSocket) -> MultiModelWSClient:
        await ws.accept()
        client = MultiModelWSClient(ws)
        client.sender_task = asyncio.create_task(client.run())
        async with self._lock:
            self.clients.add(client)
        logger.info("Multi-Model Lab WebSocket client connected. Total: %d", len(self.clients))
        return client

    async def disconnect(self, client: MultiModelWSClient) -> None:
        async with self._lock:
            self.clients.discard(client)
        if client.sender_task and not client.sender_task.done():
            client.sender_task.cancel()
        logger.info("Multi-Model Lab WebSocket client disconnected. Total: %d", len(self.clients))

    def broadcast_from_thread(self, message: Dict[str, Any]) -> None:
        if not self.loop or self.loop.is_closed():
            return
        self.loop.call_soon_threadsafe(self._enqueue_to_all, message)

    def _enqueue_to_all(self, message: Dict[str, Any]) -> None:
        for c in list(self.clients):
            c.enqueue(message)


ws_manager = MultiModelConnectionManager()


def setup_multi_model_bridge(service: MultiModelLiveService, loop: asyncio.AbstractEventLoop) -> None:
    """Connect service callbacks to WebSocket broadcaster."""
    ws_manager.set_loop(loop)
    service.subscribe(ws_manager.broadcast_from_thread)


@ws_router.websocket("/ws/experimental/multi-model")
async def websocket_multi_model_endpoint(websocket: WebSocket):
    """Real-time synchronized multi-model telemetry WebSocket stream."""
    service = get_multi_model_service()
    client = await ws_manager.connect(websocket)

    # Send initial status snapshot
    initial_msg = {
        "type": "multimodel_snapshot",
        "timestamp": datetime.now().isoformat(),
        "status": service.get_status(),
        "models": service.engine.get_models_overview(),
        "recent_windows": service.get_window_history(limit=20),
        "recent_events": service.get_event_history(limit=10),
    }
    client.enqueue(initial_msg)

    try:
        while True:
            # Keep alive and receive client control messages
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                cmd = msg.get("command")
                if cmd == "ping":
                    client.enqueue({"type": "pong", "timestamp": datetime.now().isoformat()})
                elif cmd == "toggle_model":
                    mid = msg.get("model_id")
                    en = msg.get("enabled", True)
                    service.engine.set_model_enabled(mid, en)
                    ws_manager.broadcast_from_thread({
                        "type": "model_config_updated",
                        "model_id": mid,
                        "enabled": en,
                        "enabled_models": service.engine.enabled_models,
                    })
            except Exception as e:
                logger.warning("Error processing client WS message: %s", e)
    except WebSocketDisconnect:
        await ws_manager.disconnect(client)
    except Exception as e:
        logger.debug("WebSocket client terminated: %s", e)
        await ws_manager.disconnect(client)
