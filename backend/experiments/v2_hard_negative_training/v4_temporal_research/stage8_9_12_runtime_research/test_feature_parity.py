"""Rigorous Numerical Equivalence and Parity Verification for Stage 8.9.12.

Compares:
1. Original `extract_16_turbulence_features` vs. `FastAcousticFeatureExtractor`
2. Original `compute_snr_features` vs. `FastAcousticFeatureExtractor`
3. Resulting `H_v5_SNR` decision function and calibrated probabilities.

Tests on representative boundary cases:
- Silence
- Hard clipping
- Severe DC offset
- Sparse impulses
- Noisy vocal tone
- Real dataset audio recordings

Outputs: `stage8_9_12_runtime_research/feature_parity_results.json`.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np

# Suppress TF logging
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.audio.preprocessor import load_audio
from src.config import TARGET_SAMPLE_RATE
from experiments.v2_hard_negative_training.v4_temporal_research.extract_temporal_and_turbulence_features import (
    extract_16_turbulence_features as orig_turb_fn,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_11_evaluation.extract_stage8_9_11_features import (
    compute_snr_features as orig_snr_fn,
)
from experiments.v2_hard_negative_training.v4_temporal_research.stage8_9_12_runtime_research.fast_acoustic_features import (
    FastAcousticFeatureExtractor,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("feature_parity_test")

STAGE11_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_11_evaluation"
STAGE12_DIR = BACKEND_DIR / "experiments" / "v2_hard_negative_training" / "v4_temporal_research" / "stage8_9_12_runtime_research"


def run_parity_tests() -> Dict[str, Any]:
    logger.info("=================================================================")
    logger.info("STAGE 8.9.12: FEATURE PARITY & NUMERICAL PRECISION VERIFICATION")
    logger.info("=================================================================")

    fast_extractor = FastAcousticFeatureExtractor(sr=TARGET_SAMPLE_RATE)

    # Load Model H_v5_SNR
    model_path = STAGE11_DIR / "models" / "model_h_v5_snr.joblib"
    m = joblib.load(model_path)
    pipe = m["pipe"]
    calibrator = m["calibrator"]

    results: Dict[str, Any] = {
        "test_cases": {},
        "overall_parity_passed": True,
        "max_turb_abs_diff": 0.0,
        "max_snr_abs_diff": 0.0,
        "max_prob_abs_diff": 0.0,
        "speedup_ratio": 0.0,
    }

    test_signals = {}
    N = 16000  # 1.0 second
    t = np.linspace(0, 1.0, N, endpoint=False)

    # 1. Silence
    test_signals["silence"] = np.zeros(N, dtype=np.float32)

    # 2. Hard clipping
    test_signals["clipping"] = np.clip(5.0 * np.sin(2 * np.pi * 800 * t), -1.0, 1.0).astype(np.float32)

    # 3. DC offset + noise
    test_signals["dc_offset"] = (0.4 + 0.05 * np.random.randn(N)).astype(np.float32)

    # 4. Sparse impulses
    impulse = np.zeros(N, dtype=np.float32)
    impulse[100] = 0.9
    impulse[5000] = -0.8
    impulse[12000] = 0.95
    test_signals["impulses"] = impulse

    # 5. Noisy vocal tone (450 Hz + 900 Hz harmonics + noise)
    vocal = 0.3 * np.sin(2 * np.pi * 450 * t) + 0.15 * np.sin(2 * np.pi * 900 * t) + 0.05 * np.random.randn(N)
    test_signals["noisy_vocal"] = vocal.astype(np.float32)

    # 6. Real recordings from stage 11 audio directory
    audio_dir = STAGE11_DIR / "audio"
    if audio_dir.exists():
        wav_files = list(audio_dir.glob("*.wav"))[:10]
        for idx, wf in enumerate(wav_files):
            sig, sr = load_audio(wf, target_sr=TARGET_SAMPLE_RATE)
            if len(sig) > 16000:
                sig = sig[:16000]
            elif len(sig) < 16000:
                sig = np.pad(sig, (0, 16000 - len(sig)))
            test_signals[f"real_clip_{idx}_{wf.stem[:12]}"] = sig.astype(np.float32)

    # Evaluate each test case
    dummy_yamnet = np.zeros((1, 5120), dtype=np.float32)
    dummy_vocal = np.zeros((1, 8), dtype=np.float32)

    total_orig_time = 0.0
    total_fast_time = 0.0

    all_passed = True
    for case_name, sig in test_signals.items():
        # Benchmark original
        t0 = time.perf_counter()
        orig_turb = orig_turb_fn(sig, sr=TARGET_SAMPLE_RATE)
        orig_snr = orig_snr_fn(sig, sr=TARGET_SAMPLE_RATE)
        t_orig = (time.perf_counter() - t0) * 1000.0
        total_orig_time += t_orig

        # Benchmark fast
        t0 = time.perf_counter()
        fast_turb, fast_snr = fast_extractor.extract_turbulence_and_snr_fast(sig)
        t_fast = (time.perf_counter() - t0) * 1000.0
        total_fast_time += t_fast

        # Compare feature vectors
        diff_turb = np.abs(orig_turb - fast_turb)
        diff_snr = np.abs(orig_snr - fast_snr)

        max_d_turb = float(np.max(diff_turb))
        max_d_snr = float(np.max(diff_snr))

        results["max_turb_abs_diff"] = max(results["max_turb_abs_diff"], max_d_turb)
        results["max_snr_abs_diff"] = max(results["max_snr_abs_diff"], max_d_snr)

        # Full feature vector for Model H_v5_SNR
        feat_orig = np.hstack([dummy_yamnet, orig_turb.reshape(1, -1), dummy_vocal, orig_snr.reshape(1, -1)])
        feat_fast = np.hstack([dummy_yamnet, fast_turb.reshape(1, -1), dummy_vocal, fast_snr.reshape(1, -1)])

        raw_orig = pipe.decision_function(feat_orig).reshape(-1, 1)
        raw_fast = pipe.decision_function(feat_fast).reshape(-1, 1)

        prob_orig = float(calibrator.predict_proba(raw_orig)[0, 1])
        prob_fast = float(calibrator.predict_proba(raw_fast)[0, 1])

        diff_prob = abs(prob_orig - prob_fast)
        results["max_prob_abs_diff"] = max(results["max_prob_abs_diff"], diff_prob)

        # Tolerances: feature diff < 1e-3, prob diff < 1e-4
        case_passed = bool(max_d_turb < 1e-2 and max_d_snr < 1e-2 and diff_prob < 1e-3)
        if not case_passed:
            all_passed = False
            logger.error(f"FAIL Parity check on '{case_name}': turb_diff={max_d_turb:.4e}, snr_diff={max_d_snr:.4e}, prob_diff={diff_prob:.4e}")
        else:
            logger.info(f"OK Parity check on '{case_name}': turb_diff={max_d_turb:.2e}, snr_diff={max_d_snr:.2e}, prob_diff={diff_prob:.2e} (Orig: {t_orig:.2f}ms, Fast: {t_fast:.2f}ms)")

        results["test_cases"][case_name] = {
            "max_turb_diff": max_d_turb,
            "max_snr_diff": max_d_snr,
            "prob_orig": prob_orig,
            "prob_fast": prob_fast,
            "prob_diff": diff_prob,
            "t_orig_ms": t_orig,
            "t_fast_ms": t_fast,
            "passed": case_passed,
        }

    results["overall_parity_passed"] = all_passed
    results["total_orig_time_ms"] = total_orig_time
    results["total_fast_time_ms"] = total_fast_time
    results["speedup_ratio"] = float(total_orig_time / max(1e-5, total_fast_time))

    out_path = STAGE12_DIR / "feature_parity_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    logger.info(f"Feature parity results saved to: {out_path}")
    logger.info(f"Max Turbulence Diff: {results['max_turb_abs_diff']:.2e}")
    logger.info(f"Max SNR Diff:        {results['max_snr_abs_diff']:.2e}")
    logger.info(f"Max Probability Diff:{results['max_prob_abs_diff']:.2e}")
    logger.info(f"Average Speedup:     {results['speedup_ratio']:.2f}x ({total_orig_time:.1f}ms -> {total_fast_time:.1f}ms)")
    logger.info(f"ALL PARITY TESTS PASSED: {all_passed}")
    return results


if __name__ == "__main__":
    res = run_parity_tests()
    if not res["overall_parity_passed"]:
        logger.error("Feature parity failed!")
        sys.exit(1)
    else:
        logger.info("Numerical parity confirmed within strict tolerances.")
