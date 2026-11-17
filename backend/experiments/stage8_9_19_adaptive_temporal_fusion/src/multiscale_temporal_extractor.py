"""Multi-Scale Temporal Feature Extractor and Context Uncertainty Modeller (Stage 8.9.19).

Extracts multi-scale acoustic representations across short, medium, and long temporal windows
with explicit missing-context masks and confidence-aware uncertainty estimation.

Scales:
- Short-scale (frames 0..16, ~16-512ms): Rapid onset attack, peak burst RMS, crest factor,
  high-frequency turbulence ratio (>6 kHz), onset spectral flux.
- Medium-scale (frames 0..32, ~512-1024ms): Syllabic cadence, closure gap count,
  energy modulation depth, voicing stability.
- Long-scale (frames 0..70, ~1024-2240ms): Continuous phonation duration, sustained turbulence,
  long-term trajectory consistency, repeated speech-like cadence.

Uncertainty Handling:
- Prevents false-negative shout classifications on brief screams (<0.75s) by outputting
  context availability indicators and branch uncertainty rather than treating missing
  context as evidence of non-screaming.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger("multiscale_extractor")


class MultiScaleTemporalExtractor:
    """Extracts multi-scale temporal features, context masks, and uncertainty indicators."""

    def __init__(self, frame_hop_ms: float = 32.0):
        self.frame_hop_ms = frame_hop_ms

    def extract_from_sequence(
        self,
        seq_70_16: np.ndarray,
        duration_sec: float,
    ) -> Dict[str, np.ndarray]:
        """Extract multi-scale feature vectors from a (70, 16) time-frequency sequence.

        Args:
            seq_70_16: Shape (70, 16) array of frame features.
            duration_sec: Total duration of the recording in seconds.

        Returns:
            Dictionary containing:
            - 'feat_short': 10-dim short-scale vector (onset, attack, turbulence)
            - 'feat_med': 10-dim medium-scale vector (modulation, closures, cadence)
            - 'feat_long': 10-dim long-scale vector (sustained voicing, consistency)
            - 'context_vector': 12-dim context and uncertainty state
            - 'branch_confidences': [c_short, c_med, c_long]
            - 'missing_masks': [m_short, m_med, m_long]
        """
        # Feature indices in seq_70_16:
        # 0: rms, 1: centroid, 2: bandwidth, 3: flatness, 4: r_low, 5: r_mid,
        # 6: r_high, 7: r_turb, 8: zcr, 9: v_peak, 10: flux, 11: d_centroid,
        # 12: d_rms, 13: d_high, 14: crest, 15: high_to_low_log_ratio

        # Effective frame count based on duration
        n_frames_actual = min(70, max(1, int(duration_sec * 1000.0 / self.frame_hop_ms)))

        # 1. Context Confidence and Missing-Context Masks
        c_short = float(np.clip(duration_sec / 0.35, 0.0, 1.0))
        c_med = float(np.clip((duration_sec - 0.30) / 0.50, 0.0, 1.0))
        c_long = float(np.clip((duration_sec - 0.75) / 0.75, 0.0, 1.0))

        u_short = 1.0 - c_short
        u_med = 1.0 - c_med
        u_long = 1.0 - c_long

        m_short = 1.0 if c_short >= 0.5 else 0.0
        m_med = 1.0 if c_med >= 0.5 else 0.0
        m_long = 1.0 if c_long >= 0.5 else 0.0

        # Slice sequence bounds
        idx_short_end = max(1, min(16, n_frames_actual))
        idx_med_end = max(1, min(32, n_frames_actual))
        idx_long_end = max(1, min(70, n_frames_actual))

        seq_short = seq_70_16[:idx_short_end]
        seq_med = seq_70_16[:idx_med_end]
        seq_long = seq_70_16[:idx_long_end]

        # ---------------------------------------------------------------------
        # A. Short-Scale Branch (10 dims: Onset, Attack, High-Freq Turbulence)
        # ---------------------------------------------------------------------
        rms_short = seq_short[:, 0]
        peak_rms_short = float(np.max(rms_short)) if len(rms_short) > 0 else 0.0
        mean_rms_short = float(np.mean(rms_short)) if len(rms_short) > 0 else 0.0
        turb_short = float(np.mean(seq_short[:, 7]))  # r_turb (>6 kHz)
        high_short = float(np.mean(seq_short[:, 6]))  # r_high (2.5-6 kHz)
        h2l_short = float(np.mean(seq_short[:, 15]))  # high_to_low_log_ratio
        crest_short = float(np.max(seq_short[:, 14]))  # max temporal crest
        flux_short = float(np.max(seq_short[:, 10]))   # peak onset flux
        d_rms_short = float(np.max(seq_short[:, 12]))  # peak energy rise
        zcr_short = float(np.mean(seq_short[:, 8]))    # zero-crossing rate
        flat_short = float(np.mean(seq_short[:, 3]))   # spectral flatness

        feat_short = np.array([
            peak_rms_short, mean_rms_short, turb_short, high_short,
            h2l_short, crest_short, flux_short, d_rms_short, zcr_short, flat_short,
        ], dtype=np.float32)

        # ---------------------------------------------------------------------
        # B. Medium-Scale Branch (10 dims: Syllabic Cadence, Closures, Modulation)
        # ---------------------------------------------------------------------
        rms_med = seq_med[:, 0]
        v_peak_med = seq_med[:, 9]
        # Voicing closures in medium window: frames where energy or voicing drops
        closure_frames_med = np.sum((rms_med < 0.15 * (np.max(rms_med) + 1e-6)) | (v_peak_med < 0.40))
        closure_ratio_med = float(closure_frames_med / len(rms_med))
        mod_depth_med = float((np.max(rms_med) - np.min(rms_med)) / (np.mean(rms_med) + 1e-6))
        v_peak_mean_med = float(np.mean(v_peak_med))
        v_peak_std_med = float(np.std(v_peak_med))
        cent_std_med = float(np.std(seq_med[:, 1]))
        bw_mean_med = float(np.mean(seq_med[:, 2]))
        turb_mean_med = float(np.mean(seq_med[:, 7]))
        high_mean_med = float(np.mean(seq_med[:, 6]))
        flux_mean_med = float(np.mean(seq_med[:, 10]))

        feat_med = np.array([
            closure_ratio_med, mod_depth_med, v_peak_mean_med, v_peak_std_med,
            cent_std_med, bw_mean_med, turb_mean_med, high_mean_med, flux_mean_med,
            float(np.mean(rms_med)),
        ], dtype=np.float32)

        # ---------------------------------------------------------------------
        # C. Long-Scale Branch (10 dims: Sustained Phonation, Cadence, Consistency)
        # ---------------------------------------------------------------------
        rms_long = seq_long[:, 0]
        v_peak_long = seq_long[:, 9]
        # Longest continuous voiced run in long window
        voiced_mask_long = (v_peak_long >= 0.45) & (rms_long >= 0.10 * (np.max(rms_long) + 1e-6))
        max_run = 0
        curr_run = 0
        for v in voiced_mask_long:
            if v:
                curr_run += 1
                if curr_run > max_run:
                    max_run = curr_run
            else:
                curr_run = 0
        max_cont_sec = float(max_run * (self.frame_hop_ms / 1000.0))
        voiced_ratio_long = float(np.mean(voiced_mask_long))

        # Syllabic oscillation frequency estimation via zero-crossings of mean-centered RMS
        rms_detrend = rms_long - np.mean(rms_long)
        zc_rms = np.sum(np.diff(np.sign(rms_detrend + 1e-9)) != 0)
        osc_freq_hz = float(zc_rms / (2.0 * max(0.1, duration_sec)))

        turb_long = float(np.mean(seq_long[:, 7]))
        high_long = float(np.mean(seq_long[:, 6]))
        cent_mean_long = float(np.mean(seq_long[:, 1]))
        cent_velocity_long = float(np.mean(np.abs(seq_long[:, 11])))
        bw_long = float(np.mean(seq_long[:, 2]))
        mod_long = float((np.max(rms_long) - np.min(rms_long)) / (np.mean(rms_long) + 1e-6))

        feat_long = np.array([
            max_cont_sec, voiced_ratio_long, osc_freq_hz, turb_long, high_long,
            cent_mean_long, cent_velocity_long, bw_long, mod_long, float(np.mean(rms_long)),
        ], dtype=np.float32)

        # ---------------------------------------------------------------------
        # D. Context & Uncertainty Vector (12 dims)
        # ---------------------------------------------------------------------
        context_vec = np.array([
            float(duration_sec),
            c_short, c_med, c_long,
            u_short, u_med, u_long,
            m_short, m_med, m_long,
            turb_short,
            closure_ratio_med,
        ], dtype=np.float32)

        return {
            "feat_short": feat_short,
            "feat_med": feat_med,
            "feat_long": feat_long,
            "context_vector": context_vec,
            "branch_confidences": np.array([c_short, c_med, c_long], dtype=np.float32),
            "missing_masks": np.array([m_short, m_med, m_long], dtype=np.float32),
        }

    def batch_extract(
        self,
        features_seq_16: np.ndarray,
        durations: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """Extract multi-scale representations for an entire dataset batch."""
        n_samples = len(durations)
        feats_short = np.zeros((n_samples, 10), dtype=np.float32)
        feats_med = np.zeros((n_samples, 10), dtype=np.float32)
        feats_long = np.zeros((n_samples, 10), dtype=np.float32)
        context_vectors = np.zeros((n_samples, 12), dtype=np.float32)
        confidences = np.zeros((n_samples, 3), dtype=np.float32)
        masks = np.zeros((n_samples, 3), dtype=np.float32)

        for i in range(n_samples):
            res = self.extract_from_sequence(features_seq_16[i], float(durations[i]))
            feats_short[i] = res["feat_short"]
            feats_med[i] = res["feat_med"]
            feats_long[i] = res["feat_long"]
            context_vectors[i] = res["context_vector"]
            confidences[i] = res["branch_confidences"]
            masks[i] = res["missing_masks"]

        return {
            "feats_short": feats_short,
            "feats_med": feats_med,
            "feats_long": feats_long,
            "context_vectors": context_vectors,
            "confidences": confidences,
            "masks": masks,
        }
