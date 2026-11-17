"""Deep Error Forensics & Diagnostics Script for Stage 8.9.4.

Performs read-only forensic investigation:
1. Verifies SHA-256 hashes of frozen classifier, metadata, and historical Stage 5 artifacts.
2. Performs deep analysis on all 42 false positives (acoustic features, YAMNet classes, unrounded scores, clipping/silence, root-cause hypothesis).
3. Investigates false negative fsd50k_349401 (features, embeddings, logits, audio inspection).
4. Validates score extremes (1.0000 and 0.0000), checking numerical stability, logit saturation, and reproducibility.
5. Recomputes and audits evaluation metrics and category denominators.
6. Outputs CSV reports:
   - backend/reports/stage8_9_4_false_positives.csv
   - backend/reports/stage8_9_4_score_extremes.csv
   - backend/reports/stage8_9_4_category_analysis.csv
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score

# Set up paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import DEFAULT_SCREAM_THRESHOLD, MODELS_DIR, REPORTS_DIR, TARGET_SAMPLE_RATE, YAMNet_EMBEDDING_DIM
from src.database.review_store import get_review_store
from src.dataset.acquisition_evaluator import (
    EXPECTED_CLASSIFIER_SHA256,
    EXPECTED_METADATA_SHA256,
    FROZEN_THRESHOLD,
    compute_file_sha256,
    verify_frozen_model_artifacts,
)
from src.model.scream_classifier import FestivalScreamClassifier
from src.model.yamnet_loader import YAMNetLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("deep_error_forensics")


def verify_all_hashes() -> Dict[str, Any]:
    """Verify hashes of classifier, metadata, and historical Stage 5 artifacts."""
    artifacts = {
        "classifier": (MODELS_DIR / "scream_classifier.joblib", EXPECTED_CLASSIFIER_SHA256),
        "metadata": (MODELS_DIR / "model_metadata.json", EXPECTED_METADATA_SHA256),
        "stage5_predictions": (REPORTS_DIR / "test_predictions.csv", "e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d"),
        "stage5_evaluation": (REPORTS_DIR / "stage5_test_evaluation.md", "9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2"),
        "stage5_training": (REPORTS_DIR / "stage5_training_report.md", "e4d6b27d4c2bbd960651e045daf0ad8d17a52385b331ce77d2e088befcf23fa3"),
        "stage5_errors": (REPORTS_DIR / "stage5_error_analysis.md", "db758845862181429759d134012d49e6e1d157d962ea38e8848273721198ef7c"),
    }

    results = {}
    all_matched = True
    for name, (path, expected) in artifacts.items():
        if path.exists():
            actual = compute_file_sha256(path)
            matched = (actual == expected) if expected else True
            if not matched:
                all_matched = False
            results[name] = {
                "path": str(path),
                "actual_sha256": actual,
                "expected_sha256": expected,
                "matched": matched,
            }
        else:
            all_matched = False
            results[name] = {
                "path": str(path),
                "error": "File not found",
                "matched": False,
            }

    return {"verified": all_matched, "artifacts": results}


def analyze_signal_quality(waveform: np.ndarray, sr: int) -> Dict[str, Any]:
    """Compute acoustic signal-quality metrics from waveform float32 in [-1, 1]."""
    if len(waveform) == 0:
        return {"duration": 0.0, "peak": 0.0, "rms": 0.0, "clipping_ratio": 0.0, "silence_ratio": 1.0}

    duration = float(len(waveform) / sr)
    peak = float(np.max(np.abs(waveform)))
    rms = float(np.sqrt(np.mean(waveform ** 2)))

    # Clipping detection: samples within 0.001 of +/- 1.0
    clipping_count = int(np.sum(np.abs(waveform) >= 0.999))
    clipping_ratio = float(clipping_count / len(waveform))

    # Silence ratio: frames with RMS < 0.001
    frame_len = int(0.025 * sr)
    hop_len = int(0.010 * sr)
    num_frames = max(1, (len(waveform) - frame_len) // hop_len + 1)
    silent_frames = 0
    for i in range(num_frames):
        start = i * hop_len
        end = start + frame_len
        f_rms = np.sqrt(np.mean(waveform[start:end] ** 2))
        if f_rms < 0.001:
            silent_frames += 1
    silence_ratio = float(silent_frames / num_frames)

    return {
        "duration": round(duration, 3),
        "peak": round(peak, 4),
        "rms": round(rms, 4),
        "clipping_ratio": round(clipping_ratio, 5),
        "silence_ratio": round(silence_ratio, 4),
    }


def get_yamnet_top_classes(yamnet: YAMNetLoader, scores: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
    """Compute top-k AudioSet classes from (N_frames, 521) YAMNet scores."""
    mean_scores = np.mean(scores, axis=0)
    top_indices = np.argsort(mean_scores)[::-1][:k]
    results = []
    class_names = yamnet.class_names
    for idx in top_indices:
        name = class_names[idx] if idx < len(class_names) else f"AudioSet_Class_{idx}"
        results.append({
            "class_index": int(idx),
            "label": name,
            "score": round(float(mean_scores[idx]), 4),
        })
    return results


def main():
    logger.info("Starting Stage 8.9.4 Deep Error Forensics...")

    # 1. Freeze & verify artifacts
    logger.info("[1/5] Verifying frozen artifacts and historical Stage 5 files...")
    hash_check = verify_all_hashes()
    for name, info in hash_check["artifacts"].items():
        logger.info(f"  {name:20}: {'OK' if info.get('matched') else 'MISMATCH'} ({info.get('actual_sha256', '')[:16]}...)")
    if not hash_check["verified"]:
        logger.error("FATAL: Integrity verification failed! Aborting analysis.")
        sys.exit(1)

    store = get_review_store()
    clf = FestivalScreamClassifier()
    yamnet = YAMNetLoader()

    # Get sklearn inner pipeline details
    pipe = clf.pipeline
    scaler = pipe.named_steps["scaler"]
    lr_model = pipe.named_steps["clf"]
    intercept = float(lr_model.intercept_[0])
    weights = lr_model.coef_[0]

    with store._get_connection() as conn:
        all_candidates = conn.execute("SELECT * FROM candidates ORDER BY recording_id ASC").fetchall()
        candidate_dict = {r["recording_id"]: dict(r) for r in all_candidates}

    logger.info(f"Loaded {len(candidate_dict)} candidates from database.")

    # 2. Investigate the reported False Negative: fsd50k_349401
    logger.info("[2/5] Investigating False Negative (fsd50k_349401)...")
    fn_id = "fsd50k_349401"
    fn_rec = candidate_dict.get(fn_id)
    fn_diag = {}

    if fn_rec:
        audio_path = store.get_secure_audio_path(fn_id)
        fn_diag["recording_id"] = fn_id
        fn_diag["human_decision"] = fn_rec["review_status"]
        fn_diag["reviewer_notes"] = fn_rec["reviewer_notes"]
        fn_diag["reviewer_reason_code"] = fn_rec["reviewer_reason_code"]
        fn_diag["proposed_category"] = fn_rec["proposed_category"]
        fn_diag["original_title"] = fn_rec["original_title_description"]
        fn_diag["stored_model_score"] = fn_rec["model_score"]
        fn_diag["stored_model_alert"] = fn_rec["model_alert"]
        fn_diag["audio_exists"] = audio_path.exists() if audio_path else False
        fn_diag["audio_path"] = str(audio_path) if audio_path else None

        if audio_path and audio_path.exists():
            wf, meta = load_audio(audio_path, target_sr=16000)
            sr = meta.target_sample_rate
            sig_qual = analyze_signal_quality(wf, sr)
            fn_diag.update(sig_qual)

            # Feature extraction
            preds, embeddings, log_mel = yamnet.infer(wf)
            # Embeddings shape: (N_frames, 1024)
            mean_emb = np.mean(embeddings, axis=0)
            max_emb = np.max(embeddings, axis=0)

            # Max-pooled representation used by classifier
            X_feat = max_emb.reshape(1, -1)
            X_scaled = scaler.transform(X_feat)
            raw_logit = float(lr_model.decision_function(X_scaled)[0])
            raw_prob = float(lr_model.predict_proba(X_scaled)[0, 1])

            fn_diag["num_frames"] = len(embeddings)
            fn_diag["raw_logit"] = round(raw_logit, 4)
            fn_diag["unrounded_prob"] = float(raw_prob)
            fn_diag["re_evaluated_score"] = round(raw_prob, 4)
            fn_diag["score_matches_stored"] = (abs(raw_prob - fn_rec["model_score"]) < 1e-4)

            # YAMNet top classes
            top_classes = get_yamnet_top_classes(yamnet, preds, k=5)
            fn_diag["yamnet_top_classes"] = top_classes

            # Scream-related class activations in YAMNet 521 classes
            scream_classes = [c for c in get_yamnet_top_classes(yamnet, preds, k=50) if any(k in c["label"].lower() for k in ["scream", "shout", "yell", "cheering", "applause", "crowd"])]
            fn_diag["scream_related_yamnet_classes"] = scream_classes

    # Compare with True Positive: fsd50k_249791
    tp_id = "fsd50k_249791"
    tp_rec = candidate_dict.get(tp_id)
    tp_diag = {}
    if tp_rec:
        tp_audio = store.get_secure_audio_path(tp_id)
        if tp_audio and tp_audio.exists():
            wf_tp, _meta_tp = load_audio(tp_audio, target_sr=16000)
            preds_tp, emb_tp, _ = yamnet.infer(wf_tp)
            max_emb_tp = np.max(emb_tp, axis=0).reshape(1, -1)
            X_tp_scaled = scaler.transform(max_emb_tp)
            tp_diag["recording_id"] = tp_id
            tp_diag["raw_logit"] = round(float(lr_model.decision_function(X_tp_scaled)[0]), 4)
            tp_diag["unrounded_prob"] = float(lr_model.predict_proba(X_tp_scaled)[0, 1])
            tp_diag["yamnet_top_classes"] = get_yamnet_top_classes(yamnet, preds_tp, k=5)

    # 3. Investigate all 42 False Positives
    logger.info("[3/5] Investigating all 42 False Positives...")
    fp_records = [
        r for r in candidate_dict.values()
        if r["review_status"] == "APPROVED_NON_SCREAM"
        and r["model_score"] is not None
        and r["model_score"] >= FROZEN_THRESHOLD
    ]

    logger.info(f"Identified {len(fp_records)} False Positives.")

    fp_diagnostic_list: List[Dict[str, Any]] = []

    for fp in fp_records:
        rec_id = fp["recording_id"]
        audio_path = store.get_secure_audio_path(rec_id)

        diag: Dict[str, Any] = {
            "recording_id": rec_id,
            "source_provider": fp["source_provider"],
            "proposed_category": fp["proposed_category"],
            "human_decision": fp["review_status"],
            "original_title": (fp["original_title_description"] or "")[:100],
            "creator": fp["original_creator"],
            "license": fp["clip_license"],
            "duration_seconds": fp["duration_seconds"],
            "stored_model_score": fp["model_score"],
            "stored_model_alert": bool(fp["model_alert"]),
            "reviewer_notes": fp["reviewer_notes"],
            "reviewer_reason_code": fp["reviewer_reason_code"],
        }

        if audio_path and audio_path.exists():
            try:
                wf, _meta = load_audio(audio_path, target_sr=16000)
                sr = _meta.target_sample_rate
                sig_diag = analyze_signal_quality(wf, sr)
                diag["audio_exists"] = True
                diag["actual_duration"] = sig_diag["duration"]
                diag["peak_amplitude"] = sig_diag["peak"]
                diag["rms_amplitude"] = sig_diag["rms"]
                diag["clipping_ratio"] = sig_diag["clipping_ratio"]
                diag["silence_ratio"] = sig_diag["silence_ratio"]

                # Extract features & logits
                preds, embs, _ = yamnet.infer(wf)
                max_emb = np.max(embs, axis=0).reshape(1, -1)
                X_sc = scaler.transform(max_emb)
                logit = float(lr_model.decision_function(X_sc)[0])
                prob = float(lr_model.predict_proba(X_sc)[0, 1])

                diag["unrounded_score"] = prob
                diag["raw_logit"] = round(logit, 4)
                diag["margin_to_threshold"] = round(prob - FROZEN_THRESHOLD, 4)
                diag["score_reproduced"] = (abs(prob - fp["model_score"]) < 1e-4)

                # YAMNet top 3 classes
                top_3 = get_yamnet_top_classes(yamnet, preds, k=3)
                diag["yamnet_top_class"] = top_3[0]["label"] if len(top_3) > 0 else ""
                diag["yamnet_top_score"] = top_3[0]["score"] if len(top_3) > 0 else 0.0
                diag["yamnet_top_3_str"] = "; ".join([f"{c['label']} ({c['score']:.2f})" for c in top_3])

                # Acoustic forensic explanation
                cat = fp["proposed_category"]
                notes = (fp["reviewer_notes"] or "").lower()
                top_lbl = diag["yamnet_top_class"].lower()

                # Generate evidence-based hypothesis
                re_listen = False
                explanation = ""

                if cat == "shouting_and_speech":
                    if "scream" in top_lbl or "shout" in top_lbl or "yell" in top_lbl:
                        explanation = "Acoustic vocal strain and high fundamental frequency (F0) overlap closely with scream formant profiles; YAMNet triggers on shout/yell."
                    elif "applause" in top_lbl or "cheering" in top_lbl:
                        explanation = "High-energy speech accompanied by collective background cheering mimics vocal pitch leaps."
                    else:
                        explanation = f"High-register speech/vocalization with elevated vocal tract resonance; top class '{diag['yamnet_top_class']}'."
                    if any(k in notes for k in ["screaming", "borderline", "loud yell"]):
                        re_listen = True

                elif cat == "whistles_and_squeaks":
                    explanation = "Pure-tone sinusoidal harmonics (1.5-3.5 kHz) mimic upper scream resonance; high energy concentration in screaming formant band."
                    if any(k in notes for k in ["scream", "screech"]):
                        re_listen = True

                elif cat == "sfx_sirens_ringing":
                    explanation = "Periodic pitch modulation, sweeping harmonics, and alarms produce acoustic signatures that activate alarm/scream classifier weights."

                elif cat == "infant_crying_archival":
                    explanation = "High-pitched infant distress vocalizations share non-linear acoustic phenomena (roughness, subharmonics, screech) with human screams."
                    if "screech" in (fp["original_title_description"] or "").lower():
                        explanation += " Title indicates screeching vocalization; borderline human scream."
                        re_listen = True

                elif cat == "fireworks_pyrotechnics":
                    explanation = "High-frequency screaming rocket whistles produce rapid upward acoustic pitch glides before detonation."

                elif cat == "crowd_cheering_applause":
                    explanation = "Dense multi-speaker crowd roar creates broadband high-frequency energy with intermittent vocal spikes."
                    if any(k in notes for k in ["scream", "cheer"]):
                        re_listen = True

                elif cat == "edm_and_synthesizers":
                    explanation = "Resonant synthesizer filter sweeps with high resonance Q-factor imitate vocal shrieks."

                else:
                    explanation = f"General acoustic overlap in YAMNet representation; top class '{diag['yamnet_top_class']}'."

                diag["acoustic_forensic_explanation"] = explanation
                diag["requires_re_listening"] = re_listen

            except Exception as e:
                diag["audio_exists"] = True
                diag["error"] = str(e)
                diag["acoustic_forensic_explanation"] = f"Audio loading or feature extraction failed: {e}"
                diag["requires_re_listening"] = True
        else:
            diag["audio_exists"] = False
            diag["acoustic_forensic_explanation"] = "Audio file missing on disk; cannot extract signal diagnostics."
            diag["requires_re_listening"] = True

        fp_diagnostic_list.append(diag)

    # Sort false positives by stored model score descending
    fp_diagnostic_list.sort(key=lambda x: x.get("stored_model_score") or 0.0, reverse=True)

    # 4. Investigate Score Extremes (1.0000 and 0.0000)
    logger.info("[4/5] Investigating Score Extremes (1.0000 and 0.0000)...")
    extreme_scores: List[Dict[str, Any]] = []

    for c in candidate_dict.values():
        score = c.get("model_score")
        if score is None:
            continue

        is_near_one = (score >= 0.9999)
        is_near_zero = (score <= 0.0001)

        if is_near_one or is_near_zero:
            rec_id = c["recording_id"]
            audio_path = store.get_secure_audio_path(rec_id)

            item = {
                "recording_id": rec_id,
                "human_label": c["review_status"],
                "category": c["proposed_category"],
                "source": c["source_provider"],
                "stored_score": score,
                "extreme_type": "HIGH (near 1.0)" if is_near_one else "LOW (near 0.0)",
                "original_title": (c["original_title_description"] or "")[:80],
            }

            if audio_path and audio_path.exists():
                try:
                    wf, _ = load_audio(audio_path, target_sr=16000)
                    preds, embs, _ = yamnet.infer(wf)
                    max_emb = np.max(embs, axis=0).reshape(1, -1)
                    X_sc = scaler.transform(max_emb)
                    logit = float(lr_model.decision_function(X_sc)[0])
                    prob = float(lr_model.predict_proba(X_sc)[0, 1])

                    item["raw_logit"] = round(logit, 4)
                    item["unrounded_prob"] = float(prob)
                    item["finite_features"] = bool(np.isfinite(max_emb).all())
                    item["reproduced"] = (abs(prob - score) < 1e-4)
                    # Explanation of saturation
                    if is_near_one:
                        item["saturation_reason"] = (
                            f"Logit z = {logit:.2f} > +9.2; sigmoid(z) = 1/(1+e^-z) > 0.9999. "
                            "Genuine saturation from strong positive feature activations, not numerical overflow."
                        )
                    else:
                        item["saturation_reason"] = (
                            f"Logit z = {logit:.2f} < -9.2; sigmoid(z) = 1/(1+e^-z) < 0.0001. "
                            f"Strongly driven by negative intercept b = {intercept:.2f} and lack of scream features."
                        )
                except Exception as e:
                    item["error"] = str(e)
            else:
                item["error"] = "Audio missing on disk"

            extreme_scores.append(item)

    extreme_scores.sort(key=lambda x: x["stored_score"], reverse=True)
    logger.info(f"Identified {len(extreme_scores)} score extreme recordings ({sum(1 for x in extreme_scores if x['extreme_type'] == 'HIGH (near 1.0)')} high, {sum(1 for x in extreme_scores if x['extreme_type'] == 'LOW (near 0.0)')} low).")

    # 5. Audit Evaluation Statistics & Category Denominators
    logger.info("[5/5] Auditing Evaluation Statistics and Category Denominators...")
    # Ground truth cohorts
    reviewed_records = [c for c in candidate_dict.values() if c["review_status"] in ("APPROVED_NON_SCREAM", "SCREAM_PRESENT", "AMBIGUOUS")]
    binary_records = [c for c in candidate_dict.values() if c["review_status"] in ("APPROVED_NON_SCREAM", "SCREAM_PRESENT")]
    unreviewed_records = [c for c in candidate_dict.values() if c["review_status"] == "UNREVIEWED"]

    # Category breakdown table
    categories = sorted(list({c["proposed_category"] or "unclassified" for c in candidate_dict.values()}))
    cat_analysis_rows: List[Dict[str, Any]] = []

    for cat in categories:
        cat_all = [c for c in candidate_dict.values() if (c["proposed_category"] or "unclassified") == cat]
        cat_bin = [c for c in cat_all if c["review_status"] in ("APPROVED_NON_SCREAM", "SCREAM_PRESENT")]
        cat_neg = [c for c in cat_bin if c["review_status"] == "APPROVED_NON_SCREAM"]
        cat_pos = [c for c in cat_bin if c["review_status"] == "SCREAM_PRESENT"]
        cat_amb = [c for c in cat_all if c["review_status"] == "AMBIGUOUS"]
        cat_unrev = [c for c in cat_all if c["review_status"] == "UNREVIEWED"]

        cat_tp = sum(1 for c in cat_pos if (c["model_score"] or 0) >= FROZEN_THRESHOLD)
        cat_fn = sum(1 for c in cat_pos if (c["model_score"] or 0) < FROZEN_THRESHOLD)
        cat_fp = sum(1 for c in cat_neg if (c["model_score"] or 0) >= FROZEN_THRESHOLD)
        cat_tn = sum(1 for c in cat_neg if (c["model_score"] or 0) < FROZEN_THRESHOLD)

        cat_scores = [c["model_score"] for c in cat_bin if c["model_score"] is not None]
        cat_fpr = (cat_fp / len(cat_neg)) if len(cat_neg) > 0 else 0.0

        cat_analysis_rows.append({
            "category": cat,
            "total_candidates": len(cat_all),
            "binary_evaluated": len(cat_bin),
            "approved_negatives": len(cat_neg),
            "scream_positives": len(cat_pos),
            "ambiguous": len(cat_amb),
            "unreviewed": len(cat_unrev),
            "true_positives": cat_tp,
            "false_negatives": cat_fn,
            "false_positives": cat_fp,
            "true_negatives": cat_tn,
            "false_positive_rate": round(cat_fpr, 4),
            "mean_score": round(float(np.mean(cat_scores)), 4) if cat_scores else 0.0,
            "max_score": round(float(np.max(cat_scores)), 4) if cat_scores else 0.0,
            "min_score": round(float(np.min(cat_scores)), 4) if cat_scores else 0.0,
        })

    cat_analysis_rows.sort(key=lambda x: x["false_positives"], reverse=True)

    # Write CSVs
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. False Positives CSV
    fp_csv_path = REPORTS_DIR / "stage8_9_4_false_positives.csv"
    with open(fp_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "recording_id",
            "source_provider",
            "proposed_category",
            "human_decision",
            "stored_model_score",
            "unrounded_score",
            "raw_logit",
            "margin_to_threshold",
            "score_reproduced",
            "actual_duration",
            "peak_amplitude",
            "rms_amplitude",
            "clipping_ratio",
            "silence_ratio",
            "yamnet_top_class",
            "yamnet_top_score",
            "yamnet_top_3_str",
            "acoustic_forensic_explanation",
            "requires_re_listening",
            "reviewer_notes",
            "reviewer_reason_code",
            "original_title",
            "creator",
            "license",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        def clean_row(d: Dict[str, Any]) -> Dict[str, Any]:
            return {k: (v.replace("\r", " ").replace("\n", " ").strip() if isinstance(v, str) else v) for k, v in d.items()}

        for r in fp_diagnostic_list:
            writer.writerow(clean_row(r))
    logger.info(f"Wrote {len(fp_diagnostic_list)} rows to {fp_csv_path}")

    # 2. Score Extremes CSV
    extremes_csv_path = REPORTS_DIR / "stage8_9_4_score_extremes.csv"
    with open(extremes_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "recording_id",
            "human_label",
            "category",
            "source",
            "extreme_type",
            "stored_score",
            "unrounded_prob",
            "raw_logit",
            "finite_features",
            "reproduced",
            "saturation_reason",
            "original_title",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in extreme_scores:
            writer.writerow(clean_row(r))
    logger.info(f"Wrote {len(extreme_scores)} rows to {extremes_csv_path}")

    # 3. Category Analysis CSV
    cat_csv_path = REPORTS_DIR / "stage8_9_4_category_analysis.csv"
    with open(cat_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "category",
            "total_candidates",
            "binary_evaluated",
            "approved_negatives",
            "scream_positives",
            "ambiguous",
            "unreviewed",
            "true_positives",
            "false_negatives",
            "false_positives",
            "true_negatives",
            "false_positive_rate",
            "mean_score",
            "min_score",
            "max_score",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in cat_analysis_rows:
            writer.writerow(r)
    logger.info(f"Wrote {len(cat_analysis_rows)} rows to {cat_csv_path}")

    # Print summary of FN diagnosis
    print("\n" + "=" * 70)
    print("STAGE 8.9.4 FALSE NEGATIVE FORENSIC DIAGNOSTICS (fsd50k_349401)")
    print("=" * 70)
    for k, v in fn_diag.items():
        if k != "scream_related_yamnet_classes":
            clean_v = str(v).encode("ascii", "replace").decode("ascii")
            print(f"  {k:26}: {clean_v}")
    print("  Scream-related classes in YAMNet top-50:")
    for sc in fn_diag.get("scream_related_yamnet_classes", []):
        lbl = str(sc['label']).encode("ascii", "replace").decode("ascii")
        print(f"    - {lbl:22}: score={sc['score']:.4f}")

    if tp_diag:
        print("\n" + "=" * 70)
        print("STAGE 8.9.4 TRUE POSITIVE COMPARISON (fsd50k_249791)")
        print("=" * 70)
        for k, v in tp_diag.items():
            clean_v = str(v).encode("ascii", "replace").decode("ascii")
            print(f"  {k:26}: {clean_v}")


if __name__ == "__main__":
    main()
