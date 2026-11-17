"""FastAPI REST API Endpoints for Festival Scream Detection System (Stage 8).

Implements strictly validated, production-grade endpoints:
- GET  /api/health
- GET  /api/status
- GET  /api/metrics
- GET  /api/config
- PATCH /api/config
- POST /api/detector/start
- POST /api/detector/stop
- GET  /api/events
- POST /api/events/{event_id}/acknowledge
- GET  /api/devices
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from src.api.schemas import (
    AudioDevicesResponse,
    DetectorActionResponse,
    DetectorConfigPatchRequest,
    DetectorConfigResponse,
    DetectorStartRequest,
    DetectorStatusResponse,
    EventAcknowledgeRequest,
    EventAcknowledgeResponse,
    EventsListResponse,
    ExperimentalModelShowcaseResponse,
    HealthResponse,
    MetricsResponse,
    ModelComparisonItem,
    AcceptanceGateItem,
    ConfusionMatrixData,
    DatasetCohortInfo,
    StageHistoryItem,
)
from src.config import BACKEND_DIR, MODELS_DIR
from src.detector.mic_capture import list_audio_input_devices
from src.detector.service import get_detector_service

logger = logging.getLogger("api_routes")

router = APIRouter(prefix="/api", tags=["Detector API"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health & Readiness",
    description="Check backend system health, model readiness, and version.",
)
async def get_health():
    """Verify backend API readiness and model artifact presence."""
    classifier_file = MODELS_DIR / "scream_classifier.joblib"
    classifier_status = "READY" if classifier_file.exists() else "MODEL_MISSING"

    return HealthResponse(
        status="healthy" if classifier_status == "READY" else "degraded",
        yamnet_model="Google YAMNet (Pretrained 1024-dim Embeddings)",
        classifier_model=f"Stage 5 Logistic Regression ({classifier_status})",
        version="0.8.0",
        timestamp=datetime.now().isoformat(),
    )


@router.get(
    "/status",
    response_model=DetectorStatusResponse,
    summary="Detector Stream & State Status",
    description="Get current stream state, microphone availability, active event, and config.",
)
async def get_status():
    """Return live status snapshot of the scream detection engine."""
    service = get_detector_service()
    status_data = service.get_status()
    return DetectorStatusResponse(**status_data)


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Inference & Stream Performance Metrics",
    description="Retrieve actual window latency, throughput, processed windows, and errors.",
)
async def get_metrics():
    """Return genuine, non-fabricated performance and latency metrics."""
    service = get_detector_service()
    metrics_data = service.get_metrics()
    return MetricsResponse(**metrics_data)


@router.get(
    "/config",
    response_model=DetectorConfigResponse,
    summary="Current Detection Configuration",
    description="Retrieve safe-to-expose runtime detection and smoothing parameters.",
)
async def get_config():
    """Return current detection settings (threshold, smoothing, cooldown)."""
    service = get_detector_service()
    cfg = service.get_config()
    return DetectorConfigResponse(**cfg)


@router.patch(
    "/config",
    response_model=DetectorConfigResponse,
    summary="Update Detection Configuration",
    description="Safely validate and apply runtime settings without modifying classifier weights.",
)
async def update_config(payload: DetectorConfigPatchRequest):
    """Update runtime detection parameters with strict boundary validation."""
    service = get_detector_service()

    try:
        updated = service.update_config(
            threshold=payload.threshold,
            cooldown_seconds=payload.cooldown_seconds,
            min_consecutive_positive=payload.min_consecutive_positive,
            smoothing_alpha=payload.smoothing_alpha,
            max_gap_negative_windows=payload.max_gap_negative_windows,
        )
        return DetectorConfigResponse(**updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error updating config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply configuration update.",
        )


@router.post(
    "/detector/start",
    response_model=DetectorActionResponse,
    summary="Start Live Detector",
    description="Idempotently start live microphone capture and background inference worker.",
)
async def start_detector(payload: Optional[DetectorStartRequest] = None):
    """Start detection engine. Safe against multiple concurrent calls."""
    service = get_detector_service()
    device_idx = payload.device_index if payload else None
    result = service.start(device_index=device_idx)
    return DetectorActionResponse(**result)


@router.post(
    "/detector/stop",
    response_model=DetectorActionResponse,
    summary="Stop Live Detector",
    description="Gracefully stop live microphone capture and background inference worker.",
)
async def stop_detector():
    """Stop detection engine gracefully and idempotently."""
    service = get_detector_service()
    result = service.stop()
    return DetectorActionResponse(**result)


@router.get(
    "/events",
    response_model=EventsListResponse,
    summary="Paginated Detection Event History",
    description="Retrieve historical scream detection events from JSONL log with acknowledgments.",
)
async def get_events(
    limit: int = Query(50, ge=1, le=500, description="Max records to return."),
    offset: int = Query(0, ge=0, description="Offset for pagination."),
    event_status: Optional[str] = Query(None, description="Filter by event status."),
):
    """Fetch persisted detection events."""
    service = get_detector_service()
    data = service.get_events(limit=limit, offset=offset, event_status=event_status)
    return EventsListResponse(**data)


@router.post(
    "/events/{event_id}/acknowledge",
    response_model=EventAcknowledgeResponse,
    summary="Acknowledge Detection Event",
    description="Submit human operator acknowledgment and optional log notes for an event.",
)
async def acknowledge_event(
    event_id: str,
    payload: Optional[EventAcknowledgeRequest] = None,
):
    """Record operator verification for a detection alert."""
    service = get_detector_service()
    note = payload.operator_note if payload else None
    record = service.acknowledge_event(event_id=event_id, operator_note=note)
    return EventAcknowledgeResponse(**record)


@router.get(
    "/devices",
    response_model=AudioDevicesResponse,
    summary="Enumerate Audio Input Devices",
    description="List available physical microphones and PortAudio input channels.",
)
async def get_audio_devices():
    """Query system audio input devices via sounddevice."""
    devices = list_audio_input_devices()
    return AudioDevicesResponse(devices=devices)


@router.get(
    "/experimental/demo-metrics",
    response_model=ExperimentalModelShowcaseResponse,
    summary="Experimental Model Showcase Metrics (Stage 8.9.14)",
    description="Read-only benchmark and evaluation ledger showcasing D_v4 + Family A for team demonstration.",
)
@router.get(
    "/experimental/models",
    response_model=ExperimentalModelShowcaseResponse,
    include_in_schema=False,
)
async def get_experimental_demo_metrics():
    """Return verified offline evaluation metrics for D_v4 + Family A and candidate comparisons."""
    return ExperimentalModelShowcaseResponse(
        model_id="D_v4_plus_Family_A",
        model_name="D_v4 + Family A (Stage 8.9.14 Acoustic Discriminability Model)",
        model_badge="EXPERIMENTAL DEMONSTRATION MODEL — NOT PRODUCTION CERTIFIED",
        selection_rationale=(
            "Selected because it provides the strongest reported balance of event recall (90.83%), "
            "hard-negative control (7.07%), shouting rejection (9.52%), crowd rejection (11.63%), "
            "and edge streaming latency (15.40 ms) among all evaluated candidates."
        ),
        production_model_status="STRICTLY FROZEN (Stage 5 Logistic Regression, Threshold: 0.3500)",
        last_evaluation_stage="Stage 8.9.14 (Stage 8.9.15 candidates rejected)",
        live_inference_notice=(
            "Live microphone streaming executes on the verified Production Baseline (Threshold: 0.3500). "
            "Experimental benchmark metrics are shown separately for evaluation."
        ),
        safety_notice="Possible scream detected — requires human auditory verification. Automated acoustic alerts do not confirm an emergency.",
        reported_metrics={
            "event_recall_pct": 90.83,
            "hard_negative_fpr_pct": 7.07,
            "shouted_speech_fpr_pct": 9.52,
            "crowd_fpr_pct": 11.63,
            "short_scream_recall_pct": 100.0,
            "short_screams_detected_vs_total": "5/5",
            "brief_scream_recall_1_5s_pct": 92.31,
            "brief_screams_detected_vs_total": "24/26",
            "pr_auc": 0.9231,
            "roc_auc": 0.9570,
            "precision": 0.8761,
            "f1_score": 0.8919,
            "median_latency_ms": 15.40,
            "p95_latency_ms": 19.24,
            "operating_threshold": 0.4200,
        },
        acceptance_gates=[
            AcceptanceGateItem(
                gate_name="Event-Level Scream Recall",
                metric_target=">= 96.0%",
                reported_value="90.83%",
                gate_status="FAIL",
                notes="Misses 10 out of 109 scream events on held-out test split.",
            ),
            AcceptanceGateItem(
                gate_name="Short-Scream Recall (< 1.0s)",
                metric_target=">= 90.0%",
                reported_value="100.0% (5/5)",
                gate_status="PRELIMINARY_UNCONFIRMED",
                notes="Cohort size N=5 is critically small and does not constitute certified proof.",
            ),
            AcceptanceGateItem(
                gate_name="Hard-Negative Event FPR",
                metric_target="<= 5.0%",
                reported_value="7.07%",
                gate_status="FAIL",
                notes="14 false alarms out of 198 hard negatives.",
            ),
            AcceptanceGateItem(
                gate_name="Shouted-Speech FPR",
                metric_target="<= 15.0%",
                reported_value="9.52%",
                gate_status="PASS",
                notes="4 false alarms out of 42 shouting/speech files.",
            ),
            AcceptanceGateItem(
                gate_name="End-to-End Latency",
                metric_target="<= 25.0 ms",
                reported_value="15.40 ms (p95: 19.24 ms)",
                gate_status="PASS",
                notes="60.8% of available 25.0 ms edge streaming budget consumed.",
            ),
        ],
        model_comparison=[
            ModelComparisonItem(
                model_id="Stage_8_9_22_Full_SDDFR",
                model_name="Candidate 8: Full SDDFR Two-Tier Architecture (Stage 8.9.22)",
                architecture_type="Signal-Driven Dynamic Routing (SNR Sigmoid) + High-Energy Pitch + Dual-Stream + Tier 2 (1,054 dims)",
                operating_threshold=0.35,
                event_recall_pct=78.21,
                hard_negative_fpr_pct=7.03,
                shouted_speech_fpr_pct=11.90,
                crowd_fpr_pct=5.36,
                latency_ms=12.80,
                p95_latency_ms=16.40,
                short_scream_recall_pct=86.36,
                pr_auc=0.6762,
                is_recommended_demo=True,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_20_Model_E",
                model_name="Model E: Error-Aware Adaptive (Stage 8.9.20)",
                architecture_type="Formant Dispersion + Pitch Perturbation + Short-Scale Bypass (3,110 dims)",
                operating_threshold=0.24,
                event_recall_pct=87.18,
                hard_negative_fpr_pct=7.55,
                shouted_speech_fpr_pct=21.43,
                crowd_fpr_pct=3.57,
                latency_ms=11.90,
                p95_latency_ms=15.80,
                short_scream_recall_pct=90.91,
                pr_auc=0.7122,
                is_recommended_demo=True,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_20_Model_D",
                model_name="Model D: Acoustic & YAMNet Fusion (Stage 8.9.20)",
                architecture_type="D_v4 (3,080) + Pitch/Harmonic (22) + Subband Turbulence (8) (3,110 dims)",
                operating_threshold=0.39,
                event_recall_pct=88.46,
                hard_negative_fpr_pct=7.29,
                shouted_speech_fpr_pct=19.05,
                crowd_fpr_pct=5.36,
                latency_ms=11.60,
                p95_latency_ms=15.60,
                short_scream_recall_pct=90.91,
                pr_auc=0.7441,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_20_Model_B",
                model_name="Model B: Pitch & Harmonic Model (Stage 8.9.20)",
                architecture_type="Random Forest over F0, Jitter, Shimmer, LPC Formants F1-F3 (22 dims)",
                operating_threshold=0.32,
                event_recall_pct=75.64,
                hard_negative_fpr_pct=8.85,
                shouted_speech_fpr_pct=14.29,
                crowd_fpr_pct=1.79,
                latency_ms=10.80,
                p95_latency_ms=14.50,
                short_scream_recall_pct=90.91,
                pr_auc=0.6300,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_19_Model_C",
                model_name="Model C: Multi-Scale Routing (Stage 8.9.19)",
                architecture_type="Multi-Scale Hierarchical Fusion (Short/Med/Long Routing)",
                operating_threshold=0.24,
                event_recall_pct=92.31,
                hard_negative_fpr_pct=9.90,
                shouted_speech_fpr_pct=21.43,
                crowd_fpr_pct=7.14,
                latency_ms=11.90,
                p95_latency_ms=15.50,
                short_scream_recall_pct=100.0,
                pr_auc=0.7612,
                is_recommended_demo=True,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_19_Model_B",
                model_name="Model B: Context-Dependent Gating (Stage 8.9.19)",
                architecture_type="Dynamic Context Gating Network (12 Context Dims)",
                operating_threshold=0.27,
                event_recall_pct=88.46,
                hard_negative_fpr_pct=9.64,
                shouted_speech_fpr_pct=20.24,
                crowd_fpr_pct=7.14,
                latency_ms=12.10,
                p95_latency_ms=15.80,
                short_scream_recall_pct=92.86,
                pr_auc=0.7485,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_19_Model_E",
                model_name="Model E: Neural Attention Fusion (Stage 8.9.19)",
                architecture_type="2-Layer MLP with Residual Context Attention",
                operating_threshold=0.15,
                event_recall_pct=56.41,
                hard_negative_fpr_pct=2.60,
                shouted_speech_fpr_pct=8.33,
                crowd_fpr_pct=3.57,
                latency_ms=12.40,
                p95_latency_ms=16.20,
                short_scream_recall_pct=85.71,
                pr_auc=0.6210,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_19_Model_A",
                model_name="Model A: Weighted Fusion (Stage 8.9.19)",
                architecture_type="Calibrated Convex Linear Combination",
                operating_threshold=0.15,
                event_recall_pct=76.92,
                hard_negative_fpr_pct=4.69,
                shouted_speech_fpr_pct=15.48,
                crowd_fpr_pct=5.36,
                latency_ms=11.80,
                p95_latency_ms=15.40,
                short_scream_recall_pct=85.71,
                pr_auc=0.7240,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_18_Model_D",
                model_name="Model D: Hybrid Fusion (Stage 8.9.18)",
                architecture_type="D_v4 (3,080) + 32 Temporal + CNN Sequence Prob (3,112 dims)",
                operating_threshold=0.37,
                event_recall_pct=88.46,
                hard_negative_fpr_pct=7.55,
                shouted_speech_fpr_pct=21.43,
                crowd_fpr_pct=7.14,
                latency_ms=11.30,
                p95_latency_ms=15.20,
                short_scream_recall_pct=92.86,
                pr_auc=0.7424,
                is_recommended_demo=True,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_18_Model_B",
                model_name="Model B: 1D Dilated Temporal CNN (Stage 8.9.18)",
                architecture_type="Lightweight Dilated Conv1D (70x16 sequence, ~5.2k params)",
                operating_threshold=0.36,
                event_recall_pct=67.95,
                hard_negative_fpr_pct=6.77,
                shouted_speech_fpr_pct=10.71,
                crowd_fpr_pct=5.36,
                latency_ms=12.10,
                p95_latency_ms=16.10,
                short_scream_recall_pct=78.57,
                pr_auc=0.5891,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_18_Model_A",
                model_name="Model A: Handcrafted Temporal Baseline (Stage 8.9.18)",
                architecture_type="Linear Regularized Logistic Regression (32 temporal dims)",
                operating_threshold=0.53,
                event_recall_pct=62.82,
                hard_negative_fpr_pct=8.59,
                shouted_speech_fpr_pct=13.10,
                crowd_fpr_pct=8.93,
                latency_ms=10.90,
                p95_latency_ms=14.80,
                short_scream_recall_pct=85.71,
                pr_auc=0.6061,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_18_Model_C",
                model_name="Model C: YAMNet Temporal Sequence (Stage 8.9.18)",
                architecture_type="Multi-pooled Frame Statistics + Deltas (5,120 dims)",
                operating_threshold=0.49,
                event_recall_pct=82.05,
                hard_negative_fpr_pct=6.51,
                shouted_speech_fpr_pct=19.05,
                crowd_fpr_pct=5.36,
                latency_ms=11.60,
                p95_latency_ms=15.60,
                short_scream_recall_pct=92.86,
                pr_auc=0.7389,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_17_Ref_D_v4",
                model_name="D_v4 Reconstructed Calibrated (Stage 8.9.17)",
                architecture_type="Linear Logistic Regression (3,080 dims, Calibrated)",
                operating_threshold=0.43,
                event_recall_pct=87.18,
                hard_negative_fpr_pct=8.07,
                shouted_speech_fpr_pct=20.24,
                crowd_fpr_pct=7.14,
                latency_ms=10.80,
                p95_latency_ms=15.20,
                short_scream_recall_pct=92.86,
                pr_auc=0.7407,
                is_recommended_demo=False,
                verdict="REJECTED — RESEARCH ONLY",
            ),
            ModelComparisonItem(
                model_id="D_v4_plus_Family_A",
                model_name="D_v4 + Family A (Turbulence)",
                architecture_type="Linear Logistic Regression (3,080 dims)",
                operating_threshold=0.42,
                event_recall_pct=90.83,
                hard_negative_fpr_pct=7.07,
                shouted_speech_fpr_pct=9.52,
                crowd_fpr_pct=11.63,
                latency_ms=15.40,
                p95_latency_ms=19.24,
                short_scream_recall_pct=100.0,
                pr_auc=0.9231,
                is_recommended_demo=False,
                verdict="REJECTED — ACCEPTANCE CRITERIA NOT MET",
            ),
            ModelComparisonItem(
                model_id="D_v4_plus_Family_B",
                model_name="D_v4 + Family B (Spectral Dynamics)",
                architecture_type="Linear Logistic Regression (3,080 dims)",
                operating_threshold=0.65,
                event_recall_pct=81.65,
                hard_negative_fpr_pct=4.55,
                shouted_speech_fpr_pct=7.14,
                crowd_fpr_pct=4.65,
                latency_ms=15.40,
                p95_latency_ms=19.24,
                short_scream_recall_pct=80.0,
                pr_auc=0.9229,
                is_recommended_demo=False,
                verdict="REJECTED — ACCEPTANCE CRITERIA NOT MET",
            ),
            ModelComparisonItem(
                model_id="F_v6_Acoustic_Full",
                model_name="F_v6 Acoustic Full (30 Acoustic Features)",
                architecture_type="Linear Logistic Regression (3,102 dims)",
                operating_threshold=0.36,
                event_recall_pct=87.16,
                hard_negative_fpr_pct=6.57,
                shouted_speech_fpr_pct=9.52,
                crowd_fpr_pct=6.98,
                latency_ms=15.40,
                p95_latency_ms=19.24,
                short_scream_recall_pct=80.0,
                pr_auc=0.9134,
                is_recommended_demo=False,
                verdict="REJECTED — ACCEPTANCE CRITERIA NOT MET",
            ),
            ModelComparisonItem(
                model_id="Stage_8_9_15_Temporal_CNN",
                model_name="Stage 8.9.15 Temporal Dilated CNN",
                architecture_type="Deep 1D Dilated Residual CNN (70x1024 + 30 ac)",
                operating_threshold=0.61,
                event_recall_pct=94.50,
                hard_negative_fpr_pct=17.17,
                shouted_speech_fpr_pct=21.43,
                crowd_fpr_pct=25.58,
                latency_ms=55.63,
                p95_latency_ms=71.23,
                short_scream_recall_pct=80.0,
                pr_auc=0.8992,
                is_recommended_demo=False,
                verdict="REJECTED — ACCEPTANCE CRITERIA NOT MET",
            ),
            ModelComparisonItem(
                model_id="Production_Baseline",
                model_name="Production Baseline (Stage 5)",
                architecture_type="Linear Logistic Regression (1,024 dims)",
                operating_threshold=0.35,
                event_recall_pct=87.16,
                hard_negative_fpr_pct=10.10,
                shouted_speech_fpr_pct=16.67,
                crowd_fpr_pct=13.95,
                latency_ms=16.62,
                p95_latency_ms=20.15,
                short_scream_recall_pct=80.0,
                pr_auc=0.8845,
                is_recommended_demo=False,
                verdict="FROZEN PRODUCTION MODEL",
            ),
        ],
        confusion_matrix=ConfusionMatrixData(
            true_positives=99,
            false_negatives=10,
            false_positives=14,
            true_negatives=184,
            total_eval_samples=307,
            precision_pct=87.61,
            specificity_pct=92.93,
            f1_pct=89.19,
            derivation_note="Derived from Stage 8.9.14 single-shot held-out test evaluation cohort (109 screams, 198 hard negatives at threshold 0.4200).",
        ),
        dataset_cohort=DatasetCohortInfo(
            total_held_out=307,
            scream_events=109,
            hard_negatives=198,
            short_screams_under_1s=5,
            short_screams_recall_pct=100.0,
            brief_screams_up_to_1_5s=26,
            brief_screams_recall_pct=92.31,
            provenance_license="Strictly isolated source groups; CC0, CC BY, and cleared academic sources only.",
            environment_disclaimer="Reported evaluation reflects curated dataset distributions; real-world festival acoustic variability remains uncertified.",
        ),
        stage_history=[
            StageHistoryItem(
                stage_id="Stage 8.9.14",
                stage_title="Acoustic Discriminability Research",
                status="COMPLETED",
                summary="D_v4 + Family A identified as the strongest balanced candidate model (90.83% recall, 7.07% FPR, 15.40 ms latency). All candidates failed simultaneous acceptance criteria.",
            ),
            StageHistoryItem(
                stage_id="Stage 8.9.15",
                stage_title="Hierarchical Phonation Discrimination",
                status="COMPLETED (REJECTED)",
                summary="Investigated 2-stage distress gating and temporal dilated CNN. All candidates rejected due to 152.97 ms latency breach, crowd FPR surge to 20.93%, and short-scream recall drop to 80.0%.",
            ),
            StageHistoryItem(
                stage_id="Stage 8.9.16",
                stage_title="Lightweight Event-Aware Research",
                status="PENDING_AUTHORIZATION",
                summary="Not started. Production classifier and threshold remain strictly frozen awaiting explicit team direction.",
            ),
        ],
        what_system_can_demonstrate=[
            "Acoustic Scream Detection: 90.83% event recall on held-out test split.",
            "Shouting Rejection: Shouted-speech FPR controlled to 9.52% (passing the <= 15% gate).",
            "Crowd-Noise Discrimination: Crowd chanting and cheering FPR benchmarked at 11.63%.",
            "Short-Event Sensitivity: 100.0% recall on initial 5-example short-scream test cohort (< 1.0s).",
            "Sub-20 ms Real-Time Streaming Latency: 15.40 ms median, 19.24 ms p95 (passing the <= 25 ms gate).",
        ],
        current_limitations=[
            "Event recall remains at 90.83%, failing the >= 96.0% safety-critical target.",
            "Hard-negative event FPR remains at 7.07%, failing the <= 5.0% operational false-alarm target.",
            "Short-scream test cohort is critically small (N=5 test examples); 100% recall is preliminary and uncertified.",
            "High-pitch shouting (F0 > 700 Hz with subharmonic bifurcation) remains an irreducible acoustic false-positive mode.",
            "Real-world festival environment performance with extreme crowd reverberation and pyrotechnics is not yet certified.",
        ],
    )


@router.get(
    "/experimental/stage8-9-22",
    summary="Stage 8.9.22 Research Architecture & Forensic Data",
    description="Read-only endpoint exposing Stage 8.9.22 SDDFR forensic audit, candidate matrix, per-recording telemetry, and SNR mixture benchmarks.",
)
async def get_stage8_9_22_research_data():
    """Return verified Stage 8.9.22 research results, telemetry, and per-recording decisions."""
    import json
    import csv

    stage_dir = BACKEND_DIR / "research" / "stage_8_9_22"
    summary_file = stage_dir / "reports" / "stage_8_9_22_experiment_summary.json"
    snr_file = stage_dir / "reports" / "snr_mixture_benchmark.json"
    abl_file = stage_dir / "reports" / "feature_ablation_results.json"
    decisions_file = stage_dir / "data" / "per_recording_routing_decisions.csv"

    summary_data = {}
    if summary_file.exists():
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_data = json.load(f)

    snr_data = {}
    if snr_file.exists():
        with open(snr_file, "r", encoding="utf-8") as f:
            snr_data = json.load(f)

    abl_data = {}
    if abl_file.exists():
        with open(abl_file, "r", encoding="utf-8") as f:
            abl_data = json.load(f)

    samples = []
    if decisions_file.exists():
        with open(decisions_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                samples.append(row)

    return {
        "status": "COMPLETED",
        "stage": "8.9.22",
        "title": "Signal-Driven Dynamic Feature Routing (SDDFR)",
        "verdict": "REJECTED — RESEARCH ONLY",
        "production_status": "STRICTLY FROZEN (Stage 5 Baseline, Threshold 0.3500)",
        "summary": summary_data,
        "snr_benchmarks": snr_data,
        "ablations": abl_data,
        "samples": samples[:100],
        "total_samples_evaluated": len(samples),
    }


