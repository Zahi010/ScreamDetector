"""Real-World Audio Evaluation & Dataset Collection Module (Stage 8.6).

Provides:
1. Schema definition and validation for real-world evaluation recordings and session manifests.
2. Content-hash computation (file SHA-256 and PCM SHA-256) and collision detection.
3. Strict ground-truth labeling workflow with audit history tracking.
4. Dataset quality controls (missing files, corruption, NaNs, clipping, silence, duplicates, leakage).
5. Metrics calculation (precision, recall, F1, specificity, accuracy, ROC-AUC, PR-AUC, confusion matrix).
6. Integration bridge for exporting reviewed non-scream clips into Stage 6 hard negatives.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from src.audio.preprocessor import load_audio
from src.config import (
    BACKEND_DIR,
    HARD_NEGATIVES_DIR,
    HARD_NEGATIVES_FALLBACK_DIR,
    MANIFESTS_DIR,
    RAW_DATASET_DIR,
    REAL_WORLD_EVAL_DIR,
    STAGE8_6_REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)

logger = logging.getLogger("real_world")

# Allowed Ground-Truth Labels
ALLOWED_GROUND_TRUTH_LABELS = {
    "unlabeled": "Newly recorded or unreviewed audio. Default state.",
    "scream": "Verified human scream or distress vocalization.",
    "non_scream": "Verified non-scream sound (speech, applause, whistle, music, sfx, environmental).",
    "ambiguous": "Acoustically ambiguous, mixed laughter/scream, or unclassifiable. Excluded from evaluation.",
    "exclude": "Corrupted, accidental recording, bystander privacy issue, or invalid capture.",
}

# Standardized Environment Categories
ENVIRONMENT_CATEGORIES = {
    "indoor_quiet": "Quiet room, home office, studio (low ambient noise)",
    "indoor_noisy": "Room with background chatter, music, TV, appliance noise",
    "outdoor": "Outdoor space with wind, traffic, nature sounds",
    "festival_simulation": "Acoustics with loud music, bass, PA spill, or synthetic crowd noise",
    "other": "Other unspecified acoustic environment",
}

# Standardized Sound Source Categories
SOUND_SOURCE_CATEGORIES = {
    "conversation": "Spoken human speech, quiet dialogue, talking",
    "laughter": "Laughter, chuckles, excited giggles",
    "cheering": "Applause, crowd cheering, celebratory shouting",
    "whistle": "Party whistles, referee whistles, mouth whistling",
    "scream_vocalization": "Genuine or simulated scream vocalizations (distress, excitement)",
    "music": "Recorded music playback, singing, synthesized instruments",
    "sfx": "Bells, alarms, horns, squeaky toys, electronic rings",
    "environmental_noise": "Wind, handling noise, footsteps, room rumble",
    "silence": "Ambient room silence, background room tone",
    "other": "Other sound source not listed above",
}

# Distance Categories
DISTANCE_CATEGORIES = {
    "close_0_5m": "Close proximity (within 0.5 meters of microphone)",
    "medium_1_2m": "Medium distance (1 to 2 meters from microphone)",
    "far_3m_plus": "Far distance (3 meters or greater from microphone)",
    "unknown": "Distance not recorded",
}

# Recording Methods
RECORDING_METHODS = {
    "laptop_internal_mic": "Built-in laptop microphone array",
    "external_usb_mic": "External USB microphone or audio interface",
    "headset_mic": "Wired or wireless headset microphone",
    "line_in": "Direct line-in audio capture",
    "other": "Other recording hardware",
}

# Consent Statuses
CONSENT_STATUSES = {
    "consented_operator": "Self-recorded by authorized operator",
    "consented_participant": "Informed consent obtained from vocal participant",
    "public_unidentifiable": "Public audio source without identifiable personal data",
    "unknown": "Consent status unverified",
}


def compute_file_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_pcm_sha256(waveform: np.ndarray) -> str:
    """Compute deterministic SHA-256 of int16-quantized PCM waveform data."""
    int16_samples = np.clip(waveform * 32767.0, -32768, 32767).astype(np.int16)
    return hashlib.sha256(int16_samples.tobytes()).hexdigest()


def load_historical_split_hashes(split_manifest_path: Optional[Path] = None) -> Set[str]:
    """Collect all SHA-256 hashes from historical Stage 4 dataset splits to prevent leakage."""
    target = split_manifest_path or (MANIFESTS_DIR / "split_manifest.json")
    hashes: Set[str] = set()
    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            for r in data.get("records", []):
                if "sha256_hash" in r:
                    hashes.add(r["sha256_hash"])
        except Exception as e:
            logger.warning(f"Failed to load historical hashes from {target}: {e}")
    return hashes


def build_recording_record(
    recording_id: str,
    session_id: str,
    relative_audio_path: str,
    duration_seconds: float,
    actual_sample_rate: int,
    channel_count: int,
    sample_format: str,
    recording_device_label: str,
    environment_category: str = "indoor_quiet",
    sound_source_category: str = "other",
    distance_category: str = "medium_1_2m",
    recording_method: str = "laptop_internal_mic",
    consent_status: str = "consented_operator",
    review_notes: str = "",
    ground_truth_label: str = "unlabeled",
    source_group_id: Optional[str] = None,
    file_sha256: str = "",
    pcm_sha256: str = "",
    audio_rms: float = 0.0,
    peak_amplitude: float = 0.0,
) -> Dict[str, Any]:
    """Construct a validated recording metadata dictionary."""
    if ground_truth_label not in ALLOWED_GROUND_TRUTH_LABELS:
        raise ValueError(
            f"Invalid ground-truth label '{ground_truth_label}'. Must be one of: {list(ALLOWED_GROUND_TRUTH_LABELS.keys())}"
        )
    if environment_category not in ENVIRONMENT_CATEGORIES:
        environment_category = "other"
    if sound_source_category not in SOUND_SOURCE_CATEGORIES:
        sound_source_category = "other"
    if distance_category not in DISTANCE_CATEGORIES:
        distance_category = "unknown"
    if recording_method not in RECORDING_METHODS:
        recording_method = "other"
    if consent_status not in CONSENT_STATUSES:
        consent_status = "unknown"

    label_status = "unreviewed" if ground_truth_label == "unlabeled" else "reviewed"

    return {
        "recording_id": str(recording_id),
        "session_id": str(session_id),
        "relative_audio_path": str(relative_audio_path).replace("\\", "/"),
        "recording_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(float(duration_seconds), 3),
        "actual_sample_rate": int(actual_sample_rate),
        "channel_count": int(channel_count),
        "sample_format": str(sample_format),
        "preprocessing_sample_rate": TARGET_SAMPLE_RATE,
        "recording_device_label": str(recording_device_label),
        "environment_category": environment_category,
        "sound_source_category": sound_source_category,
        "distance_category": distance_category,
        "recording_method": recording_method,
        "ground_truth_label": ground_truth_label,
        "label_status": label_status,
        "source_group_id": str(source_group_id or f"src_{session_id}"),
        "duplicate_group_id": "",
        "consent_status": consent_status,
        "review_notes": str(review_notes),
        "file_sha256": str(file_sha256),
        "pcm_sha256": str(pcm_sha256),
        "audio_rms": round(float(audio_rms), 6),
        "peak_amplitude": round(float(peak_amplitude), 6),
    }


def save_recording_manifests(
    records: List[Dict[str, Any]],
    output_dir: Path,
) -> Tuple[Path, Path]:
    """Save records to both recording_manifest.json and recording_manifest.csv."""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "recording_manifest.json"
    csv_path = output_dir / "recording_manifest.csv"

    # Save JSON manifest
    manifest_data = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_recordings": len(records),
        "label_counts": {k: sum(1 for r in records if r.get("ground_truth_label") == k) for k in ALLOWED_GROUND_TRUTH_LABELS},
        "records": records,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    # Save CSV manifest
    if records:
        fieldnames = list(records[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow(r)
    else:
        # Write empty CSV with standard headers
        fieldnames = [
            "recording_id", "session_id", "relative_audio_path", "recording_timestamp_utc",
            "duration_seconds", "actual_sample_rate", "channel_count", "sample_format",
            "preprocessing_sample_rate", "recording_device_label", "environment_category",
            "sound_source_category", "distance_category", "recording_method",
            "ground_truth_label", "label_status", "source_group_id", "duplicate_group_id",
            "consent_status", "review_notes", "file_sha256", "pcm_sha256", "audio_rms", "peak_amplitude"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    return json_path, csv_path


def load_recording_manifest(manifest_path: Path) -> List[Dict[str, Any]]:
    """Load recording records from JSON or CSV manifest."""
    if not manifest_path.exists():
        return []

    if manifest_path.suffix.lower() == ".json":
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("records", [])
    elif manifest_path.suffix.lower() == ".csv":
        records = []
        with open(manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Type conversions
                if "duration_seconds" in row and row["duration_seconds"] != "":
                    row["duration_seconds"] = float(row["duration_seconds"])
                if "actual_sample_rate" in row and row["actual_sample_rate"] != "":
                    row["actual_sample_rate"] = int(row["actual_sample_rate"])
                if "channel_count" in row and row["channel_count"] != "":
                    row["channel_count"] = int(row["channel_count"])
                if "preprocessing_sample_rate" in row and row["preprocessing_sample_rate"] != "":
                    row["preprocessing_sample_rate"] = int(row["preprocessing_sample_rate"])
                if "audio_rms" in row and row["audio_rms"] != "":
                    row["audio_rms"] = float(row["audio_rms"])
                if "peak_amplitude" in row and row["peak_amplitude"] != "":
                    row["peak_amplitude"] = float(row["peak_amplitude"])
                records.append(row)
        return records
    else:
        raise ValueError(f"Unsupported manifest format: {manifest_path.suffix}")


def append_label_audit(
    recording_id: str,
    old_label: str,
    new_label: str,
    reviewer_id: str,
    notes: str,
    audit_csv_path: Path,
) -> None:
    """Append a human labeling audit action to label_review_audit.csv."""
    audit_csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = audit_csv_path.exists()

    with open(audit_csv_path, "a", newline="", encoding="utf-8") as f:
        fieldnames = [
            "audit_timestamp_utc",
            "recording_id",
            "previous_label",
            "new_label",
            "reviewer_id",
            "review_notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "recording_id": str(recording_id),
            "previous_label": str(old_label),
            "new_label": str(new_label),
            "reviewer_id": str(reviewer_id),
            "review_notes": str(notes),
        })


def check_dataset_quality(
    records: List[Dict[str, Any]],
    base_dir: Path,
    historical_split_manifest: Optional[Path] = None,
) -> Dict[str, Any]:
    """Run comprehensive quality assurance checks on the real-world evaluation dataset."""
    issues: List[Dict[str, Any]] = []
    historical_hashes = load_historical_split_hashes(historical_split_manifest)

    seen_file_hashes: Dict[str, str] = {}
    seen_pcm_hashes: Dict[str, str] = {}

    missing_files = 0
    corrupted_files = 0
    zero_duration_files = 0
    silent_files = 0
    clipped_files = 0
    duplicate_files = 0
    historical_leakage_files = 0
    unreviewed_count = 0
    unlabeled_count = 0

    for r in records:
        rec_id = r.get("recording_id", "unknown")
        rel_path = r.get("relative_audio_path", "")
        file_path = base_dir / rel_path

        # 1. Existence check
        if not file_path.exists():
            missing_files += 1
            issues.append({
                "severity": "CRITICAL",
                "recording_id": rec_id,
                "type": "missing_file",
                "detail": f"Audio file does not exist on disk: {file_path}",
            })
            continue

        # 2. File size / zero duration
        file_size = file_path.stat().st_size
        if file_size < 100:
            zero_duration_files += 1
            issues.append({
                "severity": "CRITICAL",
                "recording_id": rec_id,
                "type": "zero_length_file",
                "detail": f"File is too small ({file_size} bytes)",
            })
            continue

        # 3. Audio decoding & integrity
        try:
            waveform, meta = load_audio(file_path, target_sr=TARGET_SAMPLE_RATE)
        except Exception as e:
            corrupted_files += 1
            issues.append({
                "severity": "CRITICAL",
                "recording_id": rec_id,
                "type": "corrupted_audio",
                "detail": f"Audio loader failed to decode: {e}",
            })
            continue

        if len(waveform) == 0:
            zero_duration_files += 1
            issues.append({
                "severity": "CRITICAL",
                "recording_id": rec_id,
                "type": "zero_length_audio",
                "detail": "Decoded audio waveform is empty",
            })
            continue

        if not np.isfinite(waveform).all():
            corrupted_files += 1
            issues.append({
                "severity": "CRITICAL",
                "recording_id": rec_id,
                "type": "non_finite_samples",
                "detail": "Waveform contains NaN or Inf values",
            })

        # 4. Silence & clipping
        peak = float(np.max(np.abs(waveform)))
        rms = float(np.sqrt(np.mean(waveform ** 2)))

        if peak < 0.001 or rms < 0.0001:
            silent_files += 1
            issues.append({
                "severity": "WARNING",
                "recording_id": rec_id,
                "type": "near_silent_audio",
                "detail": f"Extremely low amplitude (peak: {peak:.6f}, RMS: {rms:.6f})",
            })

        if peak >= 0.999:
            clipped_files += 1
            issues.append({
                "severity": "WARNING",
                "recording_id": rec_id,
                "type": "clipped_audio",
                "detail": f"Waveform reaches digital full scale (peak: {peak:.4f})",
            })

        # 5. Duplicate detection
        file_hash = compute_file_sha256(file_path)
        pcm_hash = compute_pcm_sha256(waveform)

        if file_hash in seen_file_hashes:
            duplicate_files += 1
            issues.append({
                "severity": "WARNING",
                "recording_id": rec_id,
                "type": "exact_file_duplicate",
                "detail": f"Exact binary file match with '{seen_file_hashes[file_hash]}'",
            })
        else:
            seen_file_hashes[file_hash] = rec_id

        if pcm_hash in seen_pcm_hashes:
            if file_hash not in seen_file_hashes:
                duplicate_files += 1
                issues.append({
                    "severity": "WARNING",
                    "recording_id": rec_id,
                    "type": "exact_pcm_duplicate",
                    "detail": f"Exact PCM content match with '{seen_pcm_hashes[pcm_hash]}'",
                })
        else:
            seen_pcm_hashes[pcm_hash] = rec_id

        # 6. Historical split leakage check
        if file_hash in historical_hashes:
            historical_leakage_files += 1
            issues.append({
                "severity": "CRITICAL",
                "recording_id": rec_id,
                "type": "historical_split_leakage",
                "detail": "Recording matches an existing clip in historical Stage 4 split_manifest.json!",
            })

        # 7. Review status tracking
        label = r.get("ground_truth_label", "unlabeled")
        if label == "unlabeled":
            unlabeled_count += 1
        if r.get("label_status") == "unreviewed":
            unreviewed_count += 1

    return {
        "total_records_checked": len(records),
        "total_issues_found": len(issues),
        "missing_files": missing_files,
        "corrupted_files": corrupted_files,
        "zero_duration_files": zero_duration_files,
        "silent_files": silent_files,
        "clipped_files": clipped_files,
        "duplicate_files": duplicate_files,
        "historical_leakage_files": historical_leakage_files,
        "unlabeled_count": unlabeled_count,
        "unreviewed_count": unreviewed_count,
        "issues": issues,
    }


def calculate_evaluation_metrics(
    predictions: List[Dict[str, Any]],
    threshold: float = 0.35,
) -> Dict[str, Any]:
    """Calculate comprehensive evaluation metrics from predicted scores vs ground-truth labels.
    
    Handles missing classes, zero denominators, and small sample sizes gracefully.
    """
    valid_preds = [p for p in predictions if p.get("ground_truth") in ("scream", "non_scream")]
    total = len(valid_preds)

    if total == 0:
        return {
            "status": "NOT_AVAILABLE",
            "reason": "Zero reviewed recordings with ground-truth labels ('scream' or 'non_scream').",
            "sample_count": 0,
            "threshold": threshold,
        }

    tp = sum(1 for p in valid_preds if p["ground_truth"] == "scream" and p["predicted_score"] >= threshold)
    fp = sum(1 for p in valid_preds if p["ground_truth"] == "non_scream" and p["predicted_score"] >= threshold)
    fn = sum(1 for p in valid_preds if p["ground_truth"] == "scream" and p["predicted_score"] < threshold)
    tn = sum(1 for p in valid_preds if p["ground_truth"] == "non_scream" and p["predicted_score"] < threshold)

    num_scream = tp + fn
    num_non_scream = tn + fp

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    specificity = round(tn / (tn + fp), 4) if (tn + fp) > 0 else 0.0
    accuracy = round((tp + tn) / total, 4) if total > 0 else 0.0
    f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    # ROC-AUC & PR-AUC calculation if both classes present
    roc_auc = None
    pr_auc = None
    auc_note = ""

    if num_scream > 0 and num_non_scream > 0:
        try:
            from sklearn.metrics import precision_recall_curve, roc_auc_score, auc
            y_true = [1 if p["ground_truth"] == "scream" else 0 for p in valid_preds]
            y_scores = [p["predicted_score"] for p in valid_preds]

            roc_auc = round(float(roc_auc_score(y_true, y_scores)), 4)
            precisions, recalls, _ = precision_recall_curve(y_true, y_scores)
            pr_auc = round(float(auc(recalls, precisions)), 4)
        except Exception as e:
            auc_note = f"AUC calculation error: {e}"
    else:
        auc_note = f"Cannot compute ROC-AUC / PR-AUC: Requires both classes (screams={num_scream}, non_screams={num_non_scream})."

    # Score distributions
    scream_scores = [p["predicted_score"] for p in valid_preds if p["ground_truth"] == "scream"]
    non_scream_scores = [p["predicted_score"] for p in valid_preds if p["ground_truth"] == "non_scream"]

    scream_stats = {
        "count": len(scream_scores),
        "mean": round(float(np.mean(scream_scores)), 4) if scream_scores else None,
        "median": round(float(np.median(scream_scores)), 4) if scream_scores else None,
        "min": round(float(np.min(scream_scores)), 4) if scream_scores else None,
        "max": round(float(np.max(scream_scores)), 4) if scream_scores else None,
    }
    non_scream_stats = {
        "count": len(non_scream_scores),
        "mean": round(float(np.mean(non_scream_scores)), 4) if non_scream_scores else None,
        "median": round(float(np.median(non_scream_scores)), 4) if non_scream_scores else None,
        "min": round(float(np.min(non_scream_scores)), 4) if non_scream_scores else None,
        "max": round(float(np.max(non_scream_scores)), 4) if non_scream_scores else None,
    }

    # Per-category error breakdown
    category_errors: Dict[str, Dict[str, int]] = {}
    for p in valid_preds:
        cat = p.get("sound_source_category", "other")
        if cat not in category_errors:
            category_errors[cat] = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
        gt = p["ground_truth"]
        pred_label = "scream" if p["predicted_score"] >= threshold else "non_scream"
        if gt == "scream" and pred_label == "scream":
            category_errors[cat]["tp"] += 1
        elif gt == "non_scream" and pred_label == "scream":
            category_errors[cat]["fp"] += 1
        elif gt == "non_scream" and pred_label == "non_scream":
            category_errors[cat]["tn"] += 1
        elif gt == "scream" and pred_label == "non_scream":
            category_errors[cat]["fn"] += 1

    return {
        "status": "SUCCESS",
        "sample_count": total,
        "threshold": threshold,
        "confusion_matrix": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
        },
        "metrics": {
            "precision": precision,
            "recall": recall,
            "specificity": specificity,
            "f1_score": f1,
            "accuracy": accuracy,
            "roc_auc": roc_auc,
            "pr_auc": pr_auc,
            "auc_note": auc_note,
        },
        "class_balance": {
            "scream_count": num_scream,
            "non_scream_count": num_non_scream,
        },
        "score_distribution": {
            "scream": scream_stats,
            "non_scream": non_scream_stats,
        },
        "category_breakdown": category_errors,
    }


def export_reviewed_to_hard_negatives(
    records: List[Dict[str, Any]],
    real_world_base_dir: Path,
    target_hn_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Export approved non_scream recordings to the Stage 6 hard-negative candidate pool.
    
    Creates WAV copy and Stage 6 companion sidecar JSON without altering training data directly.
    """
    dest_dir = target_hn_dir or HARD_NEGATIVES_FALLBACK_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    exported_count = 0
    skipped_count = 0
    exported_records: List[Dict[str, Any]] = []

    for r in records:
        if r.get("ground_truth_label") != "non_scream" or r.get("label_status") != "reviewed":
            skipped_count += 1
            continue

        rel_path = r.get("relative_audio_path", "")
        src_wav = real_world_base_dir / rel_path
        if not src_wav.exists():
            logger.warning(f"Audio file for export not found: {src_wav}")
            skipped_count += 1
            continue

        rec_id = r["recording_id"]
        dest_wav = dest_dir / f"eval_{rec_id}.wav"
        dest_sidecar = dest_dir / f"eval_{rec_id}.json"

        # Copy audio if not already in place
        if not dest_wav.exists():
            import shutil
            shutil.copy2(src_wav, dest_wav)

        # Build Stage 6 sidecar metadata
        sidecar_meta = {
            "recording_id": f"eval_{rec_id}",
            "original_real_world_id": rec_id,
            "source": "real_world_evaluation",
            "sound_category": r.get("sound_source_category", "vocal_non_scream"),
            "source_group_id": r.get("source_group_id", f"src_{rec_id}"),
            "environment": r.get("environment_category", "indoor_quiet"),
            "license": "Operator-Consented (Evaluation Cohort)",
            "is_commercial_safe": False,
            "review_status": "approved_non_scream",
            "review_notes": r.get("review_notes", "Exported from Stage 8.6 real-world evaluation"),
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(dest_sidecar, "w", encoding="utf-8") as f:
            json.dump(sidecar_meta, f, indent=2)

        exported_records.append(sidecar_meta)
        exported_count += 1

    return {
        "exported_count": exported_count,
        "skipped_count": skipped_count,
        "target_directory": str(dest_dir),
        "exported_records": exported_records,
    }
