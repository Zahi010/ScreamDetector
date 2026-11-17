# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Audio Quality Screening & Acoustic Signal Validation Report

## 1. Quality Screening Standards & Verification Pipeline

All 962 candidate audio recordings acquired during Stage 8.9.60 were subjected to automated acoustic screening via `backend/research/stage_8_9_60/scripts/validate_audio_quality.py`. The screening pipeline verifies that audio files decode cleanly without corrupt headers, conform to digital signal processing standards, and do not introduce severe distortion artifacts that would compromise feature extraction.

The validation pipeline calculates five standardized acoustic metrics for each audio clip:
1. **Decodability and Header Validity:** Verification that audio streams decode cleanly into uncompressed float32 PCM at 16,000 Hz mono.
2. **Root Mean Square (RMS) Energy:** Mean power level across the recording duration.
3. **Peak Amplitude (dBFS):** Maximum absolute sample amplitude relative to digital full scale.
4. **Clipping Ratio (%):** Percentage of audio samples with absolute magnitude $\ge 0.999$, indicating digital clipping or pre-amp saturation.
5. **Silence Ratio (%):** Percentage of duration where instantaneous energy falls below -45 dBFS threshold.

---

## 2. Acoustic Screening Results Summary

| Quality Screening Category | Acceptance Criterion | Observed In-Spec Count | Flagged Count | Spec Compliance % |
| :--- | :--- | :---: | :---: | :---: |
| **Decoding & Stream Integrity** | 100% clean decode, 0 errors | 962 / 962 | 0 | **100.0%** |
| **Clipping Distortion** | Clipping ratio $< 0.5\%$ | 956 / 962 | 6 | **99.38%** |
| **Silence Duration** | Silence ratio $< 50.0\%$ | 957 / 962 | 5 | **99.48%** |
| **Signal Power Level** | RMS energy $\ge 0.005$ | 952 / 962 | 10 | **98.96%** |
| **Nominal Clean Acoustic Signals** | All criteria simultaneously met | **941 / 962** | **21** | **97.82%** |

In total, **941 recordings (97.82%)** met every nominal acoustic quality threshold. The remaining 21 flagged recordings were inspected and categorized as legitimate acoustic phenomena rather than data corruption.

---

## 3. Forensic Analysis of Flagged Recordings

The 21 non-nominal recordings fall into three distinct acoustic categories:

### A. Low-Amplitude Audio (10 Recordings)
- **Observed Behavior:** Mean RMS energy between 0.0018 and 0.0048 (-38 dBFS to -32 dBFS).
- **Inspection Outcome:** These 10 recordings belong to the **Priority 1 (Low-Intensity & Muffled Screams)** acquisition cohort. They represent distance-attenuated screams recorded 30–50 meters from the microphone. They were deliberately approved and preserved to benchmark detector sensitivity at low signal power.

### B. High Silence Ratio (5 Recordings)
- **Observed Behavior:** Silence ratio between 51.2% and 62.4%.
- **Inspection Outcome:** These recordings contain long lead-in ambient silence followed by an explosive shout or scream. Active vocalization onset and offset timestamps were verified to ensure feature extraction windows encapsulate the vocal event.

### C. Minor Analog Saturation / Clipping (6 Recordings)
- **Observed Behavior:** Clipping ratio between 0.52% and 1.84%.
- **Inspection Outcome:** Close-proximity referee whistles and emergency sirens exhibiting analog pre-amplifier saturation. The harmonic distortion does not obscure the fundamental tone, and the clips were retained as realistic field confusers.

---

## 4. Signal Standardization Protocol

All acquired recordings are standardized to:
- Sample rate: 16,000 Hz.
- Channels: Mono (channel averaging applied to stereo sources).
- Bit depth: 16-bit equivalent float32 normalized to $[-1.0, +1.0]$.
- Complete recording-level metrics are permanently archived in `backend/research/stage_8_9_60/audio_quality_metrics.csv`.

Pytest tests `test_18_recording_duration_validation` and `test_19_audio_decoding_validation` confirm that zero decoding failures exist in the repository.

