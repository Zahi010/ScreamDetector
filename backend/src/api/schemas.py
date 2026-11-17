"""Pydantic Request & Response Schemas for the Festival Scream Detector API (Stage 8)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Application health and readiness status."""
    status: str = Field(..., description="Overall health status (healthy, degraded, offline).")
    yamnet_model: str = Field(..., description="Pretrained audio embedding backbone status.")
    classifier_model: str = Field(..., description="Custom Stage 5 classifier status.")
    version: str = Field("0.8.0", description="API version.")
    timestamp: str = Field(..., description="Current ISO timestamp.")


class LatencyMetrics(BaseModel):
    """Detailed window inference latency metrics in milliseconds."""
    mean: float = Field(..., description="Mean window inference latency in ms.")
    min: float = Field(..., description="Minimum window inference latency in ms.")
    max: float = Field(..., description="Maximum window inference latency in ms.")
    p95: float = Field(..., description="95th percentile window inference latency in ms.")
    samples_timed: int = Field(..., description="Total windows timed.")


class MetricsResponse(BaseModel):
    """Real performance, throughput, latency, and error counters."""
    windows_processed: int
    total_audio_seconds: float
    total_alerts_emitted: int
    total_alerts_suppressed: int
    inference_errors: int
    dropped_windows: int = 0
    dropped_samples: int
    latency_metrics_ms: LatencyMetrics
    hop_duration_ms: float
    realtime_factor: float
    session_uptime_seconds: float
    acknowledged_events_count: int


class DetectorConfigResponse(BaseModel):
    """Current runtime detection configuration."""
    threshold: float = Field(..., description="Decision probability threshold (Stage 5 baseline: 0.35).")
    cooldown_seconds: float = Field(..., description="Alert cooldown period in seconds.")
    min_consecutive_positive: int = Field(..., description="Required consecutive positive windows for alert.")
    smoothing_alpha: float = Field(..., description="EMA smoothing coefficient (0.0 to 1.0).")
    max_gap_negative_windows: int = Field(..., description="Consecutive negative windows to conclude event.")
    opt_in_recording: bool = Field(..., description="Whether raw audio saving is explicitly opted into.")


class DetectorConfigPatchRequest(BaseModel):
    """Supported runtime configuration updates with strict safety bounds."""
    threshold: Optional[float] = Field(
        None,
        ge=0.01,
        le=0.99,
        description="Detection threshold between 0.01 and 0.99 (Stage 5 default: 0.35).",
    )
    cooldown_seconds: Optional[float] = Field(
        None,
        ge=0.5,
        le=60.0,
        description="Alert cooldown duration between 0.5s and 60.0s.",
    )
    min_consecutive_positive: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Number of consecutive positive windows required to emit alert (1 to 10).",
    )
    smoothing_alpha: Optional[float] = Field(
        None,
        ge=0.05,
        le=1.0,
        description="Exponential moving average factor (0.05 to 1.0).",
    )
    max_gap_negative_windows: Optional[int] = Field(
        None,
        ge=1,
        le=10,
        description="Consecutive negative windows before event ends (1 to 10).",
    )


class DetectorStartRequest(BaseModel):
    """Request payload to start the live microphone detector."""
    device_index: Optional[int] = Field(
        None,
        description="PortAudio input device index. None for system default.",
    )


class DetectorActionResponse(BaseModel):
    """Outcome of detector lifecycle action (start / stop)."""
    success: bool
    message: str
    status: Dict[str, Any]


class EventAcknowledgeRequest(BaseModel):
    """Operator acknowledgment submission payload."""
    operator_note: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional human operator note or log entry.",
    )


class EventAcknowledgeResponse(BaseModel):
    """Result of operator acknowledgment."""
    event_id: str
    acknowledged: bool
    acknowledged_at: str
    operator_note: str


class AudioDeviceItem(BaseModel):
    """Audio input device metadata."""
    device_index: int
    name: str
    max_input_channels: int
    default_samplerate: float
    host_api: str


class AudioDevicesResponse(BaseModel):
    """List of enumerated input audio capture devices."""
    devices: List[AudioDeviceItem]


class EventsListResponse(BaseModel):
    """Paginated list of detection events from persisted storage."""
    total: int
    limit: int
    offset: int
    events: List[Dict[str, Any]]


class DetectorStatusResponse(BaseModel):
    """Real-time detector status and operational telemetry."""
    is_running: bool
    state: str
    mic_status: str
    mic_error: Optional[str] = None
    selected_device_index: Optional[int] = None
    uptime_seconds: float
    threshold: float
    cooldown_seconds: float
    min_consecutive_positive: int
    smoothing_alpha: float
    active_event: Optional[Dict[str, Any]] = None
    available_devices: int


# ==============================================================================
# Stage 8.9 Review Studio Schemas
# ==============================================================================

class ReviewSummaryResponse(BaseModel):
    """Genuine, live review counters and statistics from backend store."""
    total_candidates: int
    audio_available: int
    reviewed_count: int
    reviewed_percentage: float
    pending_review: int
    approved_non_scream: int
    scream_present: int
    ambiguous: int
    excluded: int
    missing_audio: int
    missing_model_scores: int
    model_alerts_awaiting_review: int
    category_counts: Dict[str, int]
    license_counts: Dict[str, int]
    source_counts: Dict[str, int]
    triage_counts: Dict[str, int] = Field(default_factory=dict, description="Distribution across triage groups.")
    operating_threshold: float


class RecordingItemResponse(BaseModel):
    """Detailed metadata, provenance, and review state for a single candidate."""
    recording_id: str
    source_provider: str
    original_source_id: Optional[str] = None
    original_source_url: Optional[str] = None
    local_path: Optional[str] = None
    has_audio: bool
    original_filename: Optional[str] = None
    sha256_original: Optional[str] = None
    sha256_derived: Optional[str] = None
    original_creator: Optional[str] = None
    original_title_description: Optional[str] = None
    dataset_license: Optional[str] = None
    clip_license: Optional[str] = None
    license_url_evidence: Optional[str] = None
    attribution_text: Optional[str] = None
    commercial_compatibility: str
    retrieval_timestamp: Optional[str] = None
    duration_seconds: float
    sample_rate: int
    channels: int
    original_annotations: List[str] = []
    proposed_category: Optional[str] = None
    provisional_label: str = "non_scream"
    label_confidence_status: str = "unverified_source_label"
    review_status: str
    duplicate_or_source_group: Optional[str] = None
    download_validation_status: Optional[str] = None
    unresolved_issues: List[str] = []
    model_score: Optional[float] = None
    model_alert: Optional[bool] = None
    reviewer_notes: Optional[str] = None
    reviewer_reason_code: Optional[str] = None
    reviewed_at: Optional[str] = None
    last_updated_at: Optional[str] = None
    triage_group: Optional[str] = "REVIEW_REQUIRED"
    triage_reason: Optional[str] = None
    yamnet_top_classes: List[Dict[str, Any]] = []
    yamnet_relevant_tags: List[Dict[str, Any]] = []
    clipping_ratio: Optional[float] = 0.0
    silence_ratio: Optional[float] = 0.0
    triaged_at: Optional[str] = None


class TriageRunRequest(BaseModel):
    """Request payload for automated triage execution."""
    batch_size: Optional[int] = Field(400, ge=1, le=1000, description="Max recordings to triage in this pass.")
    only_untriaged: bool = Field(False, description="Whether to only triage recordings with default REVIEW_REQUIRED or no triaged_at.")
    recording_id: Optional[str] = Field(None, description="Optional specific recording ID to triage.")


class TriageRunResponse(BaseModel):
    """Diagnostic result of automated triage run."""
    success: bool
    triaged_count: int
    triage_counts: Dict[str, int]
    failed_count: int
    results: List[Dict[str, Any]]


class RecordingsListResponse(BaseModel):
    """Paginated list of review candidates."""
    items: List[RecordingItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ReviewDecisionRequest(BaseModel):
    """Submission payload for human review decision."""
    decision: str = Field(..., description="Review decision (APPROVED_NON_SCREAM, SCREAM_PRESENT, AMBIGUOUS, EXCLUDED, UNREVIEWED).")
    reason_code: Optional[str] = Field(None, description="Standardized classification reason code.")
    notes: Optional[str] = Field(None, description="Human reviewer notes or observations.")
    reviewer: Optional[str] = Field("human_reviewer", description="Identifier of the human reviewer.")
    confirm_overwrite: bool = Field(False, description="Explicit confirmation if overwriting a previously finalized review.")


class ReviewDecisionResponse(BaseModel):
    """Result of human review decision."""
    success: bool
    recording: RecordingItemResponse
    message: str


class ReviewAuditLogItem(BaseModel):
    """Single audit log entry for review history."""
    id: int
    recording_id: str
    previous_status: str
    new_status: str
    reason_code: Optional[str] = None
    notes: Optional[str] = None
    reviewer: str
    timestamp: str


class ReviewHistoryResponse(BaseModel):
    """Full audit history for a candidate recording."""
    recording_id: str
    history: List[ReviewAuditLogItem]


class EvaluationRequest(BaseModel):
    """Request parameters for explicit, bounded local audio evaluation."""
    batch_size: Optional[int] = Field(50, ge=1, le=500, description="Max clips to evaluate in this batch.")
    only_missing: bool = Field(True, description="Only evaluate candidates without an existing score.")
    recording_id: Optional[str] = Field(None, description="Optional specific recording ID to evaluate.")


class EvaluationResponse(BaseModel):
    """Report on evaluated clips using frozen model."""
    success: bool
    evaluated_count: int
    alerts_count: int
    threshold: float
    model_hash: str
    results: List[Dict[str, Any]]


class RecoveryStatusResponse(BaseModel):
    """Audit status of missing audio recordings and recovery potential."""
    total_candidates: int
    audio_available: int
    missing_audio: int
    missing_by_source: Dict[str, int]
    existing_on_disk: int
    never_downloaded: int
    download_failed: int
    licence_restricted: int
    source_unavailable: int
    recovered_successfully: int
    preserved_human_reviews: Dict[str, int]
    freesound_api_key_configured: bool
    details: Optional[Dict[str, Any]] = None


class RecoveryRunRequest(BaseModel):
    """Request payload for controlled audio recovery run."""
    batch_size: Optional[int] = Field(None, ge=1, le=500, description="Optional batch size limit for recovery execution.")


class RecoveryRunResponse(BaseModel):
    """Result of missing audio recovery execution."""
    success: bool
    processed_count: int
    recovered_fsd50k: int
    recovered_freesound: int
    total_newly_recovered: int
    restricted_audioset: int
    unavailable_fsd50k: int
    failed_downloads: int
    cancelled: bool
    recovered_records: List[Dict[str, Any]]
    post_recovery_audit: Dict[str, Any]


# =====================================================================
# Stage 8.9.3 — Human-Verified False-Positive Analysis Schemas
# =====================================================================

class ErrorRecordingItem(BaseModel):
    """Item representation of an error recording (FP or FN) with playback and review metadata."""
    recording_id: str
    source_provider: str
    proposed_category: Optional[str] = None
    original_title: Optional[str] = None
    creator: Optional[str] = None
    license: Optional[str] = None
    duration_seconds: float
    model_score: Optional[float] = None
    model_alert: Optional[bool] = None
    predicted_label: str
    human_label: str
    reviewer_notes: Optional[str] = None
    reviewer_reason_code: Optional[str] = None
    classification_outcome: Optional[str] = None
    has_audio: bool


class CategoryBreakdownItem(BaseModel):
    """Category-level breakdown of false positives and performance metrics."""
    category: str
    total_evaluated: int
    negatives: int
    positives: int
    true_negatives: int
    false_positives: int
    true_positives: int
    false_negatives: int
    false_positive_rate: float
    mean_score: float
    max_score: float


class SourceBreakdownItem(BaseModel):
    """Source-level breakdown of false positives and performance metrics."""
    source: str
    total_evaluated: int
    negatives: int
    positives: int
    true_negatives: int
    false_positives: int
    true_positives: int
    false_negatives: int
    false_positive_rate: float
    mean_score: float
    max_score: float


class ConfusionMatrixData(BaseModel):
    """Standard 2x2 confusion matrix."""
    true_positives: int
    false_negatives: int
    true_negatives: int
    false_positives: int


class BinaryPerformanceMetrics(BaseModel):
    """Comprehensive performance rates and metrics."""
    accuracy: float
    precision: float
    recall_sensitivity: float
    specificity: float
    false_positive_rate: float
    false_negative_rate: float
    f1_score: float
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None


class StatisticalLimitationInfo(BaseModel):
    """Explicit declaration of sample sizes and statistical caveats."""
    flagged: bool
    positive_count: int
    negative_count: int
    message: str


class BinaryEvaluationSection(BaseModel):
    """Complete binary evaluation section using human labels only."""
    total_binary_evaluated: int
    negative_count_approved: int
    positive_count_scream: int
    excluded_ambiguous_count: int
    excluded_other_count: int
    confusion_matrix: ConfusionMatrixData
    metrics: BinaryPerformanceMetrics
    statistical_limitation: StatisticalLimitationInfo


class DatasetAuditSection(BaseModel):
    """Audit of dataset candidate review status and score completeness."""
    total_candidates: int
    audio_available: int
    missing_audio: int
    missing_model_scores: int
    reviewed_missing_scores_count: int
    reviewed_missing_scores_ids: List[str]
    total_human_decisions: int
    decision_counts: Dict[str, int]
    unreviewed_count: int


class ModelMetadataSection(BaseModel):
    """Integrity and parameter metadata for the frozen model."""
    operating_threshold: float
    classifier_hash: str
    metadata_hash: str
    artifacts_verified: bool


class EvaluationReportResponse(BaseModel):
    """Comprehensive Stage 8.9.3 human-verified evaluation report."""
    evaluation_stage: str
    evaluated_at: str
    model_metadata: ModelMetadataSection
    dataset_audit: DatasetAuditSection
    binary_evaluation: BinaryEvaluationSection
    category_breakdown: List[CategoryBreakdownItem]
    source_breakdown: List[SourceBreakdownItem]
    false_positives: List[ErrorRecordingItem]
    false_negatives: List[ErrorRecordingItem]
    ambiguous_records: List[ErrorRecordingItem]


class ModelComparisonItem(BaseModel):
    """Comparative model metrics item."""
    model_id: str
    model_name: str
    architecture_type: str
    operating_threshold: float
    event_recall_pct: float
    hard_negative_fpr_pct: float
    shouted_speech_fpr_pct: float
    crowd_fpr_pct: float
    latency_ms: float
    p95_latency_ms: float
    short_scream_recall_pct: float
    pr_auc: float
    is_recommended_demo: bool = False
    verdict: str


class AcceptanceGateItem(BaseModel):
    """Acceptance gate comparison item."""
    gate_name: str
    metric_target: str
    reported_value: str
    gate_status: str
    notes: Optional[str] = None


class ConfusionMatrixData(BaseModel):
    """Reported offline confusion matrix for D_v4 + Family A."""
    true_positives: int = 99
    false_negatives: int = 10
    false_positives: int = 14
    true_negatives: int = 184
    total_eval_samples: int = 307
    precision_pct: float = 87.61
    specificity_pct: float = 92.93
    f1_pct: float = 89.19
    derivation_note: str = "Derived from Stage 8.9.14 single-shot held-out test evaluation cohort (109 screams, 198 hard negatives at threshold 0.4200)."


class DatasetCohortInfo(BaseModel):
    """Dataset partition information for held-out evaluation."""
    total_held_out: int = 307
    scream_events: int = 109
    hard_negatives: int = 198
    short_screams_under_1s: int = 5
    short_screams_recall_pct: float = 100.0
    brief_screams_up_to_1_5s: int = 26
    brief_screams_recall_pct: float = 92.31
    provenance_license: str = "Strictly isolated source groups; CC0, CC BY, and cleared academic sources only."
    environment_disclaimer: str = "Reported evaluation reflects curated dataset distributions; real-world festival acoustic variability remains uncertified."


class StageHistoryItem(BaseModel):
    """Development stage historical ledger."""
    stage_id: str
    stage_title: str
    status: str
    summary: str


class ExperimentalModelShowcaseResponse(BaseModel):
    """Comprehensive read-only payload for Stage 8.9.14 Demonstration Dashboard."""
    model_id: str = "D_v4_plus_Family_A"
    model_name: str = "D_v4 + Family A (Stage 8.9.14 Acoustic Discriminability Model)"
    model_badge: str = "EXPERIMENTAL DEMONSTRATION MODEL — NOT PRODUCTION CERTIFIED"
    selection_rationale: str = "Selected because it provides the strongest reported balance of event recall (90.83%), hard-negative control (7.07%), shouting rejection (9.52%), crowd rejection (11.63%), and edge streaming latency (15.40 ms) among all evaluated candidates."
    production_model_status: str = "STRICTLY FROZEN (Stage 5 Logistic Regression, Threshold: 0.3500)"
    last_evaluation_stage: str = "Stage 8.9.14 (Stage 8.9.15 candidates rejected)"
    live_inference_notice: str = "Live microphone streaming executes on the verified Production Baseline (Threshold: 0.3500). Experimental benchmark metrics are shown separately for evaluation."
    safety_notice: str = "Possible scream detected — requires human auditory verification. Automated acoustic alerts do not confirm an emergency."
    reported_metrics: Dict[str, Any]
    acceptance_gates: List[AcceptanceGateItem]
    model_comparison: List[ModelComparisonItem]
    confusion_matrix: ConfusionMatrixData
    dataset_cohort: DatasetCohortInfo
    stage_history: List[StageHistoryItem]
    what_system_can_demonstrate: List[str]
    current_limitations: List[str]


class RunInferenceRequest(BaseModel):
    """Request to execute model inference on reviewed candidates."""
    force_reevaluate: bool = Field(False, description="Whether to re-evaluate already scored recordings.")


class RunInferenceResponse(BaseModel):
    """Result of inference execution on reviewed candidates."""
    success: bool
    evaluated_count: int
    failed_count: int
    alerts_count: int
    results: List[Dict[str, Any]]
