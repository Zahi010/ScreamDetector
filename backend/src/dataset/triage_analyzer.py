"""Stage 8.9.1 Automated Hard-Negative Triage Engine for Festival Scream Detector.

Performs multi-signal acoustic analysis:
1. Signal quality checks (duration, clipping ratio, silence ratio).
2. Frozen custom scream classifier inference at threshold 0.35.
3. Pretrained YAMNet 521 AudioSet class inference for top priors.
4. Target indicator extraction (baby cry, crying, screaming, shouting, siren, whistle, cheer, applause, electronic music, squeak, speech).
5. Transparent triage classification into 4 explicit groups:
   - LIKELY_NON_SCREAM: strong evidence of alternative sound event, weak scream evidence.
   - POSSIBLE_SCREAM: scream classifier score is high and supporting evidence is consistent.
   - AMBIGUOUS: conflicting or borderline evidence (e.g. baby crying, siren/whistle trigger, score near 0.35).
   - REVIEW_REQUIRED: missing audio, analysis error, or poor audio quality.

CRITICAL SAFETY RULES:
- Triage groups are recommendations for review prioritization only.
- They NEVER automatically approve, reject, or label any clip as ground truth.
- Unreviewed clips are NEVER counted as confirmed false positives.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.audio.preprocessor import load_audio
from src.config import DEFAULT_SCREAM_THRESHOLD, TARGET_SAMPLE_RATE
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    verify_frozen_model_artifacts,
)
from src.model.scream_classifier import FestivalScreamClassifier
from src.model.yamnet_loader import YAMNetLoader

logger = logging.getLogger("triage_analyzer")


class TriageGroup(str, Enum):
    """Transparent review prioritization categories."""
    LIKELY_NON_SCREAM = "LIKELY_NON_SCREAM"
    POSSIBLE_SCREAM = "POSSIBLE_SCREAM"
    AMBIGUOUS = "AMBIGUOUS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


# Relevant AudioSet keywords according to Stage 8.9.1 specifications
SCREAM_SHOUT_KEYWORDS = {"screaming", "screaming, shouting", "yell", "shout", "children shouting"}
CRYING_KEYWORDS = {"crying, sobbing", "baby cry, infant cry"}
WHISTLE_KEYWORDS = {"whistle", "whistling", "train whistle", "steam whistle", "slide whistle"}
CROWD_KEYWORDS = {"cheering", "applause", "crowd", "chant"}
SIREN_KEYWORDS = {"siren", "police car (siren)", "ambulance (siren)", "fire engine, fire truck (siren)", "civil defense siren", "alarm"}
MUSIC_KEYWORDS = {"electronic music", "electronic dance music", "electronica", "synthesizer", "techno", "music"}
SQUEAK_KEYWORDS = {"squeak"}
SPEECH_KEYWORDS = {"speech", "child speech, kid speaking", "conversation", "speech synthesizer", "hubbub, speech noise, speech babble"}


@dataclass
class TriageAnalysisResult:
    """Complete diagnostic output for an analyzed audio candidate."""
    recording_id: str
    triage_group: str
    triage_reason: str
    classifier_score: Optional[float]
    is_classifier_alert: Optional[bool]
    threshold: float = FROZEN_THRESHOLD
    duration_seconds: float = 0.0
    clipping_ratio: float = 0.0
    silence_ratio: float = 0.0
    yamnet_top_classes: List[Dict[str, Any]] = field(default_factory=list)
    relevant_tags: List[Dict[str, Any]] = field(default_factory=list)
    has_audio: bool = False
    status: str = "COMPLETED"
    analyzed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutomatedTriageEngine:
    """Orchestrates acoustic signal checks, frozen classifier inference, and YAMNet label profiling."""

    def __init__(
        self,
        classifier: Optional[FestivalScreamClassifier] = None,
        yamnet_loader: Optional[YAMNetLoader] = None,
        threshold: float = FROZEN_THRESHOLD,
    ):
        self.threshold = threshold

        # Verify frozen model integrity
        verified, audit = verify_frozen_model_artifacts()
        if not verified:
            raise RuntimeError(f"Frozen model artifact verification failed: {audit}")

        self.classifier = classifier or FestivalScreamClassifier()
        self.yamnet_loader = yamnet_loader or YAMNetLoader()
        if not self.yamnet_loader.is_loaded:
            self.yamnet_loader.load()

    def analyze_waveform(
        self,
        waveform: np.ndarray,
        recording_id: str,
    ) -> TriageAnalysisResult:
        """Analyze preprocessed 16 kHz float32 waveform and compute triage assignment."""
        duration = len(waveform) / float(TARGET_SAMPLE_RATE)

        # Quality checks
        clipping_ratio = float(np.mean(np.abs(waveform) >= 0.995)) if len(waveform) > 0 else 0.0
        silence_ratio = float(np.mean(np.abs(waveform) < 0.005)) if len(waveform) > 0 else 1.0

        if duration < 0.2:
            return TriageAnalysisResult(
                recording_id=recording_id,
                triage_group=TriageGroup.REVIEW_REQUIRED.value,
                triage_reason="Audio file too short (< 0.2s) for reliable acoustic analysis.",
                classifier_score=None,
                is_classifier_alert=None,
                duration_seconds=duration,
                clipping_ratio=clipping_ratio,
                silence_ratio=silence_ratio,
                has_audio=True,
                status="POOR_QUALITY",
            )

        if clipping_ratio > 0.20:
            return TriageAnalysisResult(
                recording_id=recording_id,
                triage_group=TriageGroup.REVIEW_REQUIRED.value,
                triage_reason=f"Severe digital clipping detected ({clipping_ratio:.1%} clipped samples). Manual review required.",
                classifier_score=None,
                is_classifier_alert=None,
                duration_seconds=duration,
                clipping_ratio=clipping_ratio,
                silence_ratio=silence_ratio,
                has_audio=True,
                status="POOR_QUALITY",
            )

        if silence_ratio > 0.92:
            return TriageAnalysisResult(
                recording_id=recording_id,
                triage_group=TriageGroup.REVIEW_REQUIRED.value,
                triage_reason=f"Near-silence detected ({silence_ratio:.1%} silent samples). Manual review required.",
                classifier_score=None,
                is_classifier_alert=None,
                duration_seconds=duration,
                clipping_ratio=clipping_ratio,
                silence_ratio=silence_ratio,
                has_audio=True,
                status="POOR_QUALITY",
            )

        # 1. YAMNet Inference
        scores, embeddings, _ = self.yamnet_loader.infer(waveform)
        mean_scores = np.mean(scores, axis=0)
        max_scores = np.max(scores, axis=0)
        class_names = self.yamnet_loader.class_names

        # Top 5 classes overall
        top_indices = np.argsort(mean_scores)[::-1][:5]
        top_classes = [
            {
                "class_name": class_names[idx] if idx < len(class_names) else f"Class_{idx}",
                "mean_score": round(float(mean_scores[idx]), 4),
                "max_score": round(float(max_scores[idx]), 4),
            }
            for idx in top_indices
        ]

        # Scan for target indicators
        relevant_tags: List[Dict[str, Any]] = []
        for idx, name in enumerate(class_names):
            name_lower = name.lower()
            mean_sc = float(mean_scores[idx])
            max_sc = float(max_scores[idx])

            # Filter relevant labels with meaningful activation
            if max_sc >= 0.08 or mean_sc >= 0.04:
                cat = None
                if any(k in name_lower for k in SCREAM_SHOUT_KEYWORDS):
                    cat = "scream_shout"
                elif any(k in name_lower for k in CRYING_KEYWORDS):
                    cat = "crying"
                elif any(k in name_lower for k in WHISTLE_KEYWORDS):
                    cat = "whistle"
                elif any(k in name_lower for k in CROWD_KEYWORDS):
                    cat = "crowd"
                elif any(k in name_lower for k in SIREN_KEYWORDS):
                    cat = "siren"
                elif any(k in name_lower for k in MUSIC_KEYWORDS):
                    cat = "music"
                elif any(k in name_lower for k in SQUEAK_KEYWORDS):
                    cat = "squeak"
                elif any(k in name_lower for k in SPEECH_KEYWORDS):
                    cat = "speech"

                if cat:
                    relevant_tags.append({
                        "class_name": name,
                        "category": cat,
                        "mean_score": round(mean_sc, 4),
                        "max_score": round(max_sc, 4),
                    })

        relevant_tags.sort(key=lambda x: x["max_score"], reverse=True)

        # 2. Frozen Scream Classifier Inference on pooled embeddings
        pooled = self.classifier.pool_frame_embeddings(embeddings)
        pred = self.classifier.predict_features(pooled, custom_threshold=self.threshold)
        scream_prob = float(pred["scream_probability"])
        is_alert = bool(pred["is_scream"])

        # 3. Transparent Triage Logic
        triage_group, triage_reason = self._compute_triage(
            scream_prob=scream_prob,
            is_alert=is_alert,
            relevant_tags=relevant_tags,
            top_classes=top_classes,
        )

        return TriageAnalysisResult(
            recording_id=recording_id,
            triage_group=triage_group.value,
            triage_reason=triage_reason,
            classifier_score=round(scream_prob, 4),
            is_classifier_alert=is_alert,
            threshold=self.threshold,
            duration_seconds=round(duration, 2),
            clipping_ratio=round(clipping_ratio, 4),
            silence_ratio=round(silence_ratio, 4),
            yamnet_top_classes=top_classes,
            relevant_tags=relevant_tags[:8],
            has_audio=True,
            status="COMPLETED",
        )

    def _compute_triage(
        self,
        scream_prob: float,
        is_alert: bool,
        relevant_tags: List[Dict[str, Any]],
        top_classes: List[Dict[str, Any]],
    ) -> Tuple[TriageGroup, str]:
        """Apply deterministic, transparent acoustic triage rules."""
        # Check specific tag categories
        crying_tags = [t for t in relevant_tags if t["category"] == "crying"]
        scream_tags = [t for t in relevant_tags if t["category"] == "scream_shout"]
        non_scream_tags = [t for t in relevant_tags if t["category"] not in ("crying", "scream_shout")]

        max_crying_score = max([t["max_score"] for t in crying_tags], default=0.0)
        max_scream_score = max([t["max_score"] for t in scream_tags], default=0.0)
        max_alt_score = max([t["max_score"] for t in non_scream_tags], default=0.0)
        top_alt_tag = non_scream_tags[0]["class_name"] if non_scream_tags else (top_classes[0]["class_name"] if top_classes else "Unknown")

        # RULE 1: Infant Crying & Tantrums
        # Baby cries share high fundamental frequency and formant transitions with screams.
        if max_crying_score >= 0.15:
            return (
                TriageGroup.AMBIGUOUS,
                f"Infant / child crying detected (YAMNet '{crying_tags[0]['class_name']}' max: {max_crying_score:.2f}). "
                f"Classifier score is {scream_prob:.3f}. Crying acoustics frequently overlap with scream harmonics.",
            )

        # RULE 2: Possible Scream
        # Classifier probability is above threshold AND scream vocalization evidence is present or score is high
        if scream_prob >= self.threshold:
            if max_scream_score >= 0.15:
                scream_tag_name = scream_tags[0]["class_name"]
                return (
                    TriageGroup.POSSIBLE_SCREAM,
                    f"Elevated scream classifier score ({scream_prob:.3f} >= {self.threshold:.2f}) supported by YAMNet '{scream_tag_name}' (max: {max_scream_score:.2f}).",
                )
            elif scream_prob >= 0.55:
                return (
                    TriageGroup.POSSIBLE_SCREAM,
                    f"High scream classifier probability ({scream_prob:.3f} >= 0.55) indicates strong vocal distress characteristics.",
                )
            else:
                # Borderline trigger with alternative sound (Candidate false alarm vulnerability)
                return (
                    TriageGroup.AMBIGUOUS,
                    f"Threshold triggered ({scream_prob:.3f} >= {self.threshold:.2f}), but YAMNet indicates '{top_alt_tag}' (max: {max_alt_score:.2f}) without definitive scream tags. Potential false positive vulnerability.",
                )

        # RULE 3: Borderline probability (just below threshold)
        if 0.25 <= scream_prob < self.threshold:
            if max_scream_score >= 0.15:
                return (
                    TriageGroup.AMBIGUOUS,
                    f"Classifier score is borderline ({scream_prob:.3f} near {self.threshold:.2f}) with YAMNet vocalization tag '{scream_tags[0]['class_name']}' (max: {max_scream_score:.2f}).",
                )
            else:
                return (
                    TriageGroup.AMBIGUOUS,
                    f"Borderline score ({scream_prob:.3f} vs {self.threshold:.2f}). Acoustic profile presents mixed features.",
                )

        # RULE 4: Likely Non-Scream
        # Classifier score is well below threshold (< 0.25)
        if non_scream_tags and max_alt_score >= 0.15:
            return (
                TriageGroup.LIKELY_NON_SCREAM,
                f"Low scream probability ({scream_prob:.3f} < {self.threshold:.2f}) with strong alternative sound evidence: '{top_alt_tag}' (max: {max_alt_score:.2f}).",
            )

        return (
            TriageGroup.LIKELY_NON_SCREAM,
            f"Low scream probability ({scream_prob:.3f} < {self.threshold:.2f}) with top acoustic prior '{top_classes[0]['class_name'] if top_classes else 'Environment'}' (score: {top_classes[0]['mean_score'] if top_classes else 0.0:.2f}).",
        )

    def analyze_audio_file(
        self,
        audio_path: Path,
        recording_id: str,
    ) -> TriageAnalysisResult:
        """Safely load audio file from disk and perform triage analysis."""
        if not audio_path.is_file():
            return TriageAnalysisResult(
                recording_id=recording_id,
                triage_group=TriageGroup.REVIEW_REQUIRED.value,
                triage_reason="Audio file not found on local disk.",
                classifier_score=None,
                is_classifier_alert=None,
                has_audio=False,
                status="FILE_NOT_FOUND",
            )

        try:
            waveform, meta = load_audio(audio_path, target_sr=TARGET_SAMPLE_RATE)
            return self.analyze_waveform(waveform, recording_id=recording_id)
        except Exception as exc:
            logger.warning("Triage analysis failed for '%s': %s", recording_id, exc)
            return TriageAnalysisResult(
                recording_id=recording_id,
                triage_group=TriageGroup.REVIEW_REQUIRED.value,
                triage_reason=f"Audio loading or decoding error: {str(exc)[:100]}",
                classifier_score=None,
                is_classifier_alert=None,
                has_audio=True,
                status=f"ERROR: {exc}",
            )
