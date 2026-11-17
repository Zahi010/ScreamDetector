# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""
FastAPI REST & WebSocket Routes for Research Demonstration Dashboard (Stage 8.9.67).

Provides:
- GET  /api/research/models
- GET  /api/research/models/active
- POST /api/research/models/select
- POST /api/research/inference/file
- GET  /api/research/metrics
- GET  /api/research/evaluation/summary
- GET  /api/research/events
- POST /api/research/events/clear
- GET  /api/research/session/export
- WS   /ws/research/live

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Response,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from pydantic import BaseModel, Field

import time
import numpy as np
from pathlib import Path
from src.research_service import get_research_service, StreamingAudioBuffer

REPO_ROOT = Path(__file__).resolve().parents[3]
logger = logging.getLogger("research_routes")

research_router = APIRouter(prefix="/api/research", tags=["Research Demonstration (Stage 8.9.67)"])
research_ws_router = APIRouter(tags=["Research WebSocket"])


class ModelSelectionRequest(BaseModel):
    model_id: str = Field(..., description="ID of the research or production model to activate")


@research_router.get("/models")
async def list_registered_models():
    """List all registered models with their metadata, thresholds, and audit verdicts."""
    svc = get_research_service()
    return {"models": svc.list_models(), "active_model_id": svc.active_model_id}


@research_router.get("/models/active")
async def get_active_model():
    """Retrieve currently selected active model for inference."""
    svc = get_research_service()
    return svc.get_active_model()


@research_router.post("/models/select")
async def select_active_model(req: ModelSelectionRequest):
    """Switch active model between Production Baseline, Candidate 65-F, and Candidate 67-D."""
    svc = get_research_service()
    try:
        updated = svc.select_model(req.model_id)
        return {"success": True, "active_model": updated}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@research_router.post("/inference/file")
async def infer_audio_file(
    file: UploadFile = File(...),
    model_id: Optional[str] = None,
):
    """Run scream detection inference on an uploaded WAV file using active or specified model."""
    svc = get_research_service()
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .wav audio files are currently supported for research inference.",
        )

    try:
        content = await file.read()
        res = svc.infer_file_bytes(content, filename=file.filename, model_id=model_id)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error("Error during research file inference: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Inference error: {e}")


@research_router.get("/metrics")
async def get_performance_metrics():
    """Real-time performance monitoring metrics (P50, P95, P99 latency, processed windows)."""
    svc = get_research_service()
    return svc.get_metrics()


@research_router.get("/events")
async def get_session_events():
    """Recent scream-like detection event history."""
    svc = get_research_service()
    return {"events": svc.get_events()}


@research_router.post("/events/clear")
async def clear_session_events():
    """Clear session event history for research demonstration."""
    svc = get_research_service()
    svc.clear_events()
    return {"success": True, "message": "Session event history cleared."}


@research_router.get("/evaluation/summary")
async def get_evaluation_summary():
    """Complete Five-Gate acceptance scorecard and candidate comparison data."""
    svc = get_research_service()
    return svc.get_evaluation_summary()


@research_router.get("/session/export")
async def export_session_summary(format: str = "csv"):
    """Export session event and telemetry summary."""
    svc = get_research_service()
    if format == "csv":
        csv_data = svc.export_session_csv()
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=research_demonstration_session.csv"},
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported format. Use 'csv'.")


@research_router.get("/samples/scream")
async def get_sample_scream_pcm():
    """Returns 1.0s of genuine benchmark scream audio encoded as 16 kHz 16-bit PCM for hardware testing."""
    scream_path = REPO_ROOT / "backend/experiments/stage8_9_20_acoustic_discriminability/data/supplementary_short_screams/supp_short_scream_001_v2_nigens_HUMAN-SCREAM_GEN-HDF-15246.wav"
    if scream_path.exists():
        import soundfile as sf
        audio, sr = sf.read(scream_path)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != 16000:
            import scipy.signal as sp_signal
            audio = sp_signal.resample(audio, int(len(audio) * 16000 / sr))
        if len(audio) < 16000:
            audio = np.pad(audio, (0, 16000 - len(audio)))
        else:
            audio = audio[:16000]
        pcm16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)
        return Response(content=pcm16.tobytes(), media_type="application/octet-stream")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample scream file not found.")


@research_router.get("/samples/speech")
async def get_sample_speech_pcm():
    """Returns 1.0s of genuine hard-negative speech audio encoded as 16 kHz 16-bit PCM for hardware testing."""
    hn_files = list((REPO_ROOT / "backend/dataset/stage8_8_hard_negatives/approved").glob("*.wav"))
    if hn_files:
        import soundfile as sf
        audio, sr = sf.read(hn_files[0])
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != 16000:
            import scipy.signal as sp_signal
            audio = sp_signal.resample(audio, int(len(audio) * 16000 / sr))
        if len(audio) < 16000:
            audio = np.pad(audio, (0, 16000 - len(audio)))
        else:
            audio = audio[:16000]
        pcm16 = np.clip(audio * 32767.0, -32768, 32767).astype(np.int16)
        return Response(content=pcm16.tobytes(), media_type="application/octet-stream")
    # Fallback to synthesized speech-like tone
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    synthetic_speech = 0.3 * np.sin(2 * np.pi * 220.0 * t) + 0.2 * np.sin(2 * np.pi * 440.0 * t)
    pcm16 = np.clip(synthetic_speech * 32767.0, -32768, 32767).astype(np.int16)
    return Response(content=pcm16.tobytes(), media_type="application/octet-stream")


# ==============================================================================
# Live Audio Streaming WebSocket
# ==============================================================================

@research_ws_router.websocket("/ws/research/live")
async def research_live_websocket(websocket: WebSocket):
    """High-performance WebSocket for real-time live audio streaming inference.
    Accepts raw binary PCM (16 kHz, 16-bit mono) or JSON telemetry messages,
    maintains a rolling audio buffer (16,000 samples = 1.0s, hop = 4,000 samples = 0.25s),
    runs active research model inference, and broadcasts real-time probability & latency.
    """
    await websocket.accept()
    svc = get_research_service()
    buffer = StreamingAudioBuffer(sample_rate=16000, window_size=16000, hop_size=4000)
    logger.info("Research live WebSocket client connected; initialized streaming buffer (16k window, 4k hop).")

    # Send initial handshake snapshot
    await websocket.send_text(
        json.dumps({
            "type": "HANDSHAKE",
            "active_model": svc.get_active_model(),
            "metrics": svc.get_metrics(),
            "buffer_status": buffer.get_status(),
            "safety_notice": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE",
        })
    )

    try:
        while True:
            msg = await websocket.receive()
            if "bytes" in msg and msg["bytes"]:
                raw_bytes = msg["bytes"]
                # Convert raw PCM int16 bytes to float32
                if len(raw_bytes) % 2 == 0:
                    audio_np = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    buffer.append(audio_np)

                    if buffer.is_ready_for_inference():
                        window = buffer.get_latest_window()
                        res = svc.infer_audio_array(window, sr=16000)
                        buffer.mark_inference_complete()
                        res["type"] = "INFERENCE_UPDATE"
                        res["buffer_status"] = buffer.get_status()
                        res["is_buffering"] = False
                        await websocket.send_text(json.dumps(res))
                    else:
                        # Low-overhead update during initial buffering phase
                        b_status = buffer.get_status()
                        if b_status["samples_buffered"] < buffer.window_size:
                            await websocket.send_text(json.dumps({
                                "type": "BUFFERING_UPDATE",
                                "buffer_status": b_status,
                                "model_id": svc.active_model_id,
                                "state": "INITIALIZING STREAM",
                                "calibrated_probability": 0.0,
                                "raw_probability": 0.0,
                                "is_detected": False,
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            }))

            elif "text" in msg and msg["text"]:
                try:
                    payload = json.loads(msg["text"])
                    cmd = payload.get("command")
                    if cmd == "PING":
                        await websocket.send_text(json.dumps({
                            "type": "PONG",
                            "timestamp": time.time(),
                            "buffer_status": buffer.get_status(),
                        }))
                    elif cmd == "SELECT_MODEL":
                        mid = payload.get("model_id")
                        if mid:
                            updated = svc.select_model(mid)
                            buffer.reset()
                            await websocket.send_text(json.dumps({
                                "type": "MODEL_CHANGED",
                                "active_model": updated,
                                "buffer_status": buffer.get_status(),
                            }))
                    elif cmd == "RESET_BUFFER":
                        buffer.reset()
                        await websocket.send_text(json.dumps({
                            "type": "BUFFER_RESET",
                            "buffer_status": buffer.get_status(),
                        }))
                except json.JSONDecodeError:
                    pass
    except WebSocketDisconnect:
        logger.info("Research live WebSocket client disconnected.")
    except Exception as e:
        logger.warning("Research live WebSocket exception: %s", e)

