"""FastAPI Router for Stage 8.9 Human Review Studio.

Endpoints:
- GET  /api/review/summary
- GET  /api/review/recordings
- GET  /api/review/recordings/{recording_id}
- GET  /api/review/recordings/{recording_id}/audio
- POST /api/review/recordings/{recording_id}/decision
- GET  /api/review/recordings/{recording_id}/history
- POST /api/review/evaluate
- GET  /api/review/export.csv
"""

from __future__ import annotations

import logging
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse, StreamingResponse

from src.api.schemas import (
    EvaluationReportResponse,
    EvaluationRequest,
    EvaluationResponse,
    RecordingItemResponse,
    RecordingsListResponse,
    RecoveryRunRequest,
    RecoveryRunResponse,
    RecoveryStatusResponse,
    ReviewAuditLogItem,
    ReviewDecisionRequest,
    ReviewDecisionResponse,
    ReviewHistoryResponse,
    ReviewSummaryResponse,
    RunInferenceRequest,
    RunInferenceResponse,
    TriageRunRequest,
    TriageRunResponse,
)
from src.database.review_store import (
    OverwriteConfirmationRequired,
    ReviewStore,
    get_review_store,
)
from src.dataset.acquisition_evaluator import (
    AcquiredAudioEvaluator,

    EXPECTED_CLASSIFIER_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.dataset.triage_analyzer import (
    AutomatedTriageEngine,
    TriageAnalysisResult,
    TriageGroup,
)

logger = logging.getLogger("review_routes")

router = APIRouter(prefix="/api/review", tags=["Review Studio API"])

CHUNK_SIZE = 64 * 1024  # 64 KB chunks for streaming audio


def range_stream_file(
    filepath: Path,
    start: int,
    end: int,
    chunk_size: int = CHUNK_SIZE,
) -> Generator[bytes, None, None]:
    """Yield chunks of a file for HTTP Range requests without loading entire file into memory."""
    with open(filepath, "rb") as f:
        f.seek(start)
        bytes_to_read = end - start + 1
        while bytes_to_read > 0:
            read_size = min(chunk_size, bytes_to_read)
            data = f.read(read_size)
            if not data:
                break
            bytes_to_read -= len(data)
            yield data


@router.get(
    "/summary",
    response_model=ReviewSummaryResponse,
    summary="Review Queue Summary & Counters",
    description="Retrieve live counters for discovered, available, reviewed, and pending candidates.",
)
async def get_review_summary():
    """Return genuine live counters and breakdown statistics."""
    store = get_review_store()
    return store.get_summary()


@router.get(
    "/recordings",
    response_model=RecordingsListResponse,
    summary="Filterable & Sortable Review Queue",
    description="Query candidates by category, source, license, status, audio availability, score, with pagination.",
)
async def list_review_recordings(
    category: Optional[str] = Query(None, description="Target sound category filter"),
    source: Optional[str] = Query(None, description="Dataset/source provider filter"),
    license: Optional[str] = Query(None, description="Commercial license classification filter"),
    status: Optional[str] = Query(None, description="Review status filter"),
    triage_group: Optional[str] = Query(None, description="Triage category filter: 'LIKELY_NON_SCREAM', 'POSSIBLE_SCREAM', 'AMBIGUOUS', 'REVIEW_REQUIRED'"),
    audio: Optional[str] = Query(None, description="Audio availability: 'all', 'available', 'missing'"),
    score_filter: Optional[str] = Query(None, description="Score filter: 'all', 'high_risk', 'low_risk', 'missing'"),
    search: Optional[str] = Query(None, description="Search term for ID, filename, or title"),
    sort_by: str = Query("priority", description="Sort by: 'priority', 'triage', 'model_score', 'category', 'status', 'source', 'recording_id', 'duration'"),
    sort_order: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(25, ge=1, le=200, description="Items per page"),
):
    """Retrieve paginated candidates matching the specified filter criteria."""
    store = get_review_store()
    items, total = store.get_recordings(
        category=category,
        source=source,
        license_status=license,
        review_status=status,
        triage_group=triage_group,
        audio_availability=audio,
        score_filter=score_filter,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return RecordingsListResponse(
        items=[RecordingItemResponse(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/recordings/{recording_id}",
    response_model=RecordingItemResponse,
    summary="Get Single Candidate Details",
    description="Retrieve full metadata and review details for a specific recording ID.",
)
async def get_recording_detail(recording_id: str):
    """Return details for a single candidate recording."""
    store = get_review_store()
    item = store.get_recording(recording_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate recording '{recording_id}' not found.",
        )
    return RecordingItemResponse(**item)


@router.get(
    "/recordings/{recording_id}/audio",
    summary="Stream Audio for Selected Candidate",
    description="Stream audio file with HTTP Range support for seeking. Resolves path from trusted manifest/DB only.",
)
async def get_recording_audio(recording_id: str, request: Request):
    """Serve audio stream for the selected candidate supporting HTTP Range requests."""
    store = get_review_store()
    audio_path = store.get_secure_audio_path(recording_id)
    if not audio_path or not audio_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file for recording '{recording_id}' not found or unavailable.",
        )

    file_size = audio_path.stat().st_size
    range_header = request.headers.get("range")

    content_type = "audio/wav"
    if audio_path.suffix.lower() == ".flac":
        content_type = "audio/flac"
    elif audio_path.suffix.lower() == ".mp3":
        content_type = "audio/mpeg"
    elif audio_path.suffix.lower() == ".ogg":
        content_type = "audio/ogg"

    if range_header:
        # Parse range header: e.g. "bytes=0-1024" or "bytes=1024-"
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
        if range_match:
            start_str, end_str = range_match.groups()
            start = int(start_str)
            end = int(end_str) if end_str else file_size - 1

            if start >= file_size or end >= file_size or start > end:
                return Response(
                    status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                    headers={"Content-Range": f"bytes */{file_size}"},
                )

            content_length = end - start + 1
            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Type": content_type,
            }

            return StreamingResponse(
                range_stream_file(audio_path, start, end),
                status_code=status.HTTP_206_PARTIAL_CONTENT,
                headers=headers,
            )

    # Standard full response with Accept-Ranges
    return FileResponse(
        path=str(audio_path),
        media_type=content_type,
        headers={"Accept-Ranges": "bytes"},
    )


@router.post(
    "/recordings/{recording_id}/decision",
    response_model=ReviewDecisionResponse,
    summary="Submit Human Review Decision",
    description="Save intentional review decision (APPROVED_NON_SCREAM, SCREAM_PRESENT, AMBIGUOUS, EXCLUDED) with audit log.",
)
async def submit_review_decision(recording_id: str, payload: ReviewDecisionRequest):
    """Save review decision with audit history. Requires explicit confirmation if overwriting."""
    store = get_review_store()
    try:
        updated = store.submit_decision(
            recording_id=recording_id,
            new_status=payload.decision,
            reason_code=payload.reason_code,
            notes=payload.notes,
            reviewer=payload.reviewer or "human_reviewer",
            confirm_overwrite=payload.confirm_overwrite,
        )
        return ReviewDecisionResponse(
            success=True,
            recording=RecordingItemResponse(**updated),
            message=f"Review decision '{payload.decision}' recorded successfully.",
        )
    except OverwriteConfirmationRequired as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": str(exc),
                "current_status": exc.current_status,
                "new_status": exc.new_status,
                "requires_confirmation": True,
            },
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate recording '{recording_id}' not found.",
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )


@router.get(
    "/recordings/{recording_id}/history",
    response_model=ReviewHistoryResponse,
    summary="Get Candidate Review Audit History",
    description="Retrieve immutable, append-only history of human decisions and notes for this recording.",
)
async def get_recording_history(recording_id: str):
    """Return chronological review audit log."""
    store = get_review_store()
    candidate = store.get_recording(recording_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate recording '{recording_id}' not found.",
        )

    history_rows = store.get_history(recording_id)
    items = [ReviewAuditLogItem(**h) for h in history_rows]
    return ReviewHistoryResponse(recording_id=recording_id, history=items)


@router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    summary="Evaluate Local Audio with Frozen Classifier",
    description="Explicit, bounded, non-destructive inference on local audio using frozen YAMNet + Logistic Regression at threshold 0.35.",
)
async def evaluate_local_audio(payload: EvaluationRequest):
    """Run frozen inference on local audio files without modifying model or historical splits."""
    verified, audit = verify_frozen_model_artifacts()
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Frozen model artifact integrity verification failed: {audit}",
        )

    store = get_review_store()
    evaluator = AcquiredAudioEvaluator(threshold=FROZEN_THRESHOLD)

    # Determine targets
    targets: List[Dict[str, Any]] = []
    if payload.recording_id:
        rec = store.get_recording(payload.recording_id)
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recording '{payload.recording_id}' not found.",
            )
        if not rec.get("has_audio"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Recording '{payload.recording_id}' does not have local audio on disk to evaluate.",
            )
        targets = [rec]
    else:
        # Batch of eligible recordings with local audio
        score_filter = "missing" if payload.only_missing else None
        items, _ = store.get_recordings(
            audio_availability="available",
            score_filter=score_filter,
            page=1,
            page_size=payload.batch_size or 50,
            sort_by="priority",
        )
        targets = items

    results: List[Dict[str, Any]] = []
    alerts_count = 0

    for item in targets:
        rec_id = item["recording_id"]
        audio_path = store.get_secure_audio_path(rec_id)
        if not audio_path or not audio_path.exists():
            continue

        try:
            pred_res = evaluator.classifier.predict_file(audio_path, custom_threshold=FROZEN_THRESHOLD)
            prob = float(pred_res["scream_probability"])
            alert = bool(pred_res["is_scream"])

            store.record_model_evaluation(
                recording_id=rec_id,
                model_score=prob,
                is_alert=alert,
                threshold=FROZEN_THRESHOLD,
                artifact_hash=EXPECTED_CLASSIFIER_SHA256,
                status="COMPLETED",
            )

            if alert:
                alerts_count += 1

            results.append({
                "recording_id": rec_id,
                "model_score": prob,
                "is_alert": alert,
                "status": "COMPLETED",
            })
        except Exception as e:
            logger.warning("Evaluation failed for '%s': %s", rec_id, e)
            store.record_model_evaluation(
                recording_id=rec_id,
                model_score=-1.0,
                is_alert=False,
                threshold=FROZEN_THRESHOLD,
                artifact_hash=EXPECTED_CLASSIFIER_SHA256,
                status=f"FAILED: {e}",
            )
            results.append({
                "recording_id": rec_id,
                "error": str(e),
                "status": "FAILED",
            })

    return EvaluationResponse(
        success=True,
        evaluated_count=len(results),
        alerts_count=alerts_count,
        threshold=FROZEN_THRESHOLD,
        model_hash=EXPECTED_CLASSIFIER_SHA256,
        results=results,
    )


_triage_engine: Optional[AutomatedTriageEngine] = None


def get_triage_engine() -> AutomatedTriageEngine:
    """Retrieve or initialize singleton AutomatedTriageEngine instance."""
    global _triage_engine
    if _triage_engine is None:
        _triage_engine = AutomatedTriageEngine()
    return _triage_engine


@router.post(
    "/triage/run",
    response_model=TriageRunResponse,
    summary="Run Automated Hard-Negative Triage",
    description="Analyze audio candidates using frozen classifier and YAMNet to compute transparent triage groups.",
)
async def run_automated_triage(payload: TriageRunRequest = TriageRunRequest()):
    """Execute acoustic triage analysis and update recommendation groupings."""
    store = get_review_store()
    engine = get_triage_engine()

    with store._get_connection() as conn:
        if payload.recording_id:
            rows = conn.execute(
                "SELECT recording_id, local_path, has_audio FROM candidates WHERE recording_id = ?",
                (payload.recording_id,),
            ).fetchall()
        elif payload.only_untriaged:
            rows = conn.execute(
                "SELECT recording_id, local_path, has_audio FROM candidates WHERE triaged_at IS NULL LIMIT ?",
                (payload.batch_size,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT recording_id, local_path, has_audio FROM candidates ORDER BY has_audio DESC, recording_id ASC LIMIT ?",
                (payload.batch_size,),
            ).fetchall()

    triaged_count = 0
    failed_count = 0
    results: List[Dict[str, Any]] = []

    for r in rows:
        rec_id = r["recording_id"]
        has_audio = bool(r["has_audio"])

        audio_path = store.get_secure_audio_path(rec_id) if has_audio else None

        if audio_path and audio_path.is_file():
            try:
                res = engine.analyze_audio_file(audio_path, recording_id=rec_id)
            except Exception as exc:
                logger.warning("Triage analysis exception for '%s': %s", rec_id, exc)
                failed_count += 1
                res = TriageAnalysisResult(
                    recording_id=rec_id,
                    triage_group=TriageGroup.REVIEW_REQUIRED.value,
                    triage_reason=f"Analysis error: {str(exc)[:100]}",
                    classifier_score=None,
                    is_classifier_alert=None,
                    has_audio=True,
                    status=f"ERROR: {exc}",
                )
        else:
            res = TriageAnalysisResult(
                recording_id=rec_id,
                triage_group=TriageGroup.REVIEW_REQUIRED.value,
                triage_reason="Audio file not found on local disk.",
                classifier_score=None,
                is_classifier_alert=None,
                has_audio=False,
                status="FILE_NOT_FOUND",
            )

        store.save_triage_result(res)
        triaged_count += 1
        results.append({
            "recording_id": rec_id,
            "triage_group": res.triage_group,
            "triage_reason": res.triage_reason,
            "classifier_score": res.classifier_score,
            "has_audio": res.has_audio,
            "status": res.status,
        })

    # Fetch live summary counts for response
    summary = store.get_summary()
    triage_counts = summary.get("triage_counts", {})

    return TriageRunResponse(
        success=True,
        triaged_count=triaged_count,
        triage_counts=triage_counts,
        failed_count=failed_count,
        results=results,
    )


@router.get(
    "/export.csv",
    summary="Export Review Dataset as CSV",
    description="Download complete review dataset with provenance, review decisions, notes, and model scores. Never exports secrets.",
)
async def export_review_csv():
    """Stream complete candidate review queue and provenance as CSV attachment."""
    store = get_review_store()
    return StreamingResponse(
        store.export_csv_stream(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=festival_dataset_review_export.csv",
            "Cache-Control": "no-cache",
        },
    )


@router.get(
    "/recovery/status",
    response_model=RecoveryStatusResponse,
    summary="Get Missing Audio Recovery Audit Status",
    description="Retrieve comprehensive audit of missing recordings categorized by source, disk presence, licensing, and recoverability.",
)
async def get_recovery_status():
    """Return live audit of missing audio recordings and recovery potential."""
    from src.dataset.audio_recovery_service import get_audio_recovery_service
    service = get_audio_recovery_service()
    audit = service.get_audit()
    return RecoveryStatusResponse(**audit)


@router.post(
    "/recovery/run",
    response_model=RecoveryRunResponse,
    summary="Execute Controlled Missing Audio Recovery",
    description="Recover missing audio recordings from local E: drive (FSD50K) and official API (Freesound) with non-destructive integrity preservation.",
)
async def run_missing_audio_recovery(payload: RecoveryRunRequest = RecoveryRunRequest()):
    """Run non-destructive recovery and triage on missing audio candidates."""
    from src.dataset.audio_recovery_service import get_audio_recovery_service
    service = get_audio_recovery_service()
    res = service.recover_missing_audio(batch_size=payload.batch_size)
    return RecoveryRunResponse(**res)


@router.post(
    "/recovery/cancel",
    summary="Cancel Ongoing Audio Recovery",
    description="Gracefully stop an in-progress audio recovery workflow.",
)
async def cancel_missing_audio_recovery():
    """Request early termination of ongoing recovery."""
    from src.dataset.audio_recovery_service import get_audio_recovery_service
    service = get_audio_recovery_service()
    service.request_cancel()
    return {"message": "Recovery cancellation requested. Current item will finish safely."}


# =====================================================================
# Stage 8.9.3 — Human-Verified False-Positive Analysis Endpoints
# =====================================================================

@router.get(
    "/evaluation/report",
    response_model=EvaluationReportResponse,
    summary="Get Human-Verified False-Positive Evaluation Report",
    description="Calculate and return comprehensive confusion matrix, performance metrics, and error recordings evaluated against verified human ground truth.",
)
async def get_human_evaluation_report():
    """Compute and return live evaluation report based on human review decisions."""
    from src.dataset.false_positive_analyzer import get_false_positive_analyzer
    analyzer = get_false_positive_analyzer()
    report = analyzer.compute_evaluation_report()
    return EvaluationReportResponse(**report)


@router.post(
    "/evaluation/run",
    response_model=RunInferenceResponse,
    summary="Run Frozen Model Inference on Reviewed Recordings",
    description="Execute resumable frozen model evaluation across reviewed recordings with usable audio, updating model scores without changing human decisions.",
)
async def run_human_evaluation_inference(payload: RunInferenceRequest = RunInferenceRequest()):
    """Run inference on reviewed candidates and return execution summary."""
    from src.dataset.false_positive_analyzer import get_false_positive_analyzer
    analyzer = get_false_positive_analyzer()
    res = analyzer.run_inference_on_reviewed(force_reevaluate=payload.force_reevaluate)
    return RunInferenceResponse(**res)


@router.get(
    "/evaluation/export.csv",
    summary="Export Human-Verified Evaluation Dataset as CSV",
    description="Download complete human-verified evaluation results, including human labels, model scores, threshold, predictions, and error categories.",
)
async def export_evaluation_csv():
    """Stream complete human-verified evaluation dataset as CSV attachment."""
    from src.dataset.false_positive_analyzer import get_false_positive_analyzer
    analyzer = get_false_positive_analyzer()
    return StreamingResponse(
        analyzer.generate_evaluation_csv_stream(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=human_verified_evaluation_report.csv",
            "Cache-Control": "no-cache",
        },
    )


