# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Short-Scream Development Dataset Expansion Report — Stage 8.9.64

**Stage Designation:** STAGE 8.9.64  
**Date:** November 12, 2026  
**Harness Script:** `backend/research/stage_8_9_64/scripts/audit_short_scream_acquisition.py`  
**Manifest Path:** `backend/research/stage_8_9_64/stage_64_short_scream_manifest.csv`  
**Manifest SHA-256:** `658ae11fc79154960c6e675ac184ac126808c01c250d0ff354d4bd26a3f04e5b`  
**Status:** COMPLETE — TARGET EXCEEDED (401 ELIGIBLE SHORT-SCREAM RECORDINGS ACQUIRED)  

---

## 1. Executive Summary

Stage 8.9.63 closed with 133 short-scream recordings, falling 17 clips short of its acquisition target and earning the formal governance designation `INSUFFICIENT_DEVELOPMENT_EVIDENCE`.

In Stage 8.9.64, targeted data expansion was executed across permissive development audio pools (Stages 8.9.20, 8.9.38, 8.9.41, 8.9.43, and 8.9.49) with strict legal licensing (CC0, CC BY 3.0, CC BY 4.0) and absolute isolation from the sealed 700-recording evaluation cohort.

### Acquisition Highlights
- **Target Short-Scream Cohort:** $\ge 250$ eligible recordings.
- **Acquired & Adjudicated Cohort:** **$401$ unique recordings** ($160.4\%$ of target).
- **Duration Bands Covered:**
  - $100\text{–}300$ ms: $18$ recordings
  - $300\text{–}500$ ms: $99$ recordings
  - $500\text{–}750$ ms: $151$ recordings
  - $750\text{–}999$ ms: $133$ recordings
- **Acoustic Subtypes:** 329 standard short screams, 66 ultra-short screams ($\le 0.50$ s), 6 distant / low-intensity screams.
- **Independence & Isolation:** Audited against `sealed_cohort_predictions.csv`: **zero recording ID, exact SHA-256, or decoded PCM hash overlap** with the sealed cohort.

---

## 2. Provenance and Licensing Breakdown

| Source Audio Pool | Permissive License | Clips Acquired | Acoustic Characteristics |
| :--- | :--- | :---: | :--- |
| **Stage 8.9.63 Development Base** | CC0 / CC BY 4.0 | 133 | Adjudicated baseline short screams |
| **Stage 8.9.38 Permissive Screams**| CC0 | 38 | High-pitch shrieks, sudden panic bursts |
| **Stage 8.9.20 Discrimination Pool**| CC BY 4.0 | 58 | Transient screams in varying room acoustics |
| **Stage 8.9.41 Permissive Screams**| CC0 | 22 | Isolated dry studio and outdoor screams |
| **Stage 8.9.43 Permissive Pool** | CC BY 3.0 | 25 | Festival crowd vocal bursts |
| **Stage 8.9.49 Development Audio** | CC BY 4.0 | 85 | Multi-distance vocal distress outcries |
| **Stage 8.9.49 Validation Audio** | CC BY 4.0 | 40 | Brief shrieks and vocal starts |
| **Total Combined Manifest** | **CC0 / CC BY** | **401** | **All durations $< 1.00$ second** |

---

## 3. Strict Deduplication and Leakage Verification

To prevent circular contamination or evaluation data leakage:
1. **Exact File Hash Verification:** All 401 audio files possess unique SHA-256 digests.
2. **PCM Audio Hash Verification:** Decoded 16-bit PCM equivalent float arrays verified 401 distinct cryptographic signatures (zero audio duplicate clips).
3. **Sealed Cohort Isolation:** Cross-matched against all 700 files in Stage 8.9.61's sealed evaluation cohort. No overlap detected in recording ID, source filename, uploader, or audio hash.
4. **License Quarantine:** Zero proprietary, CC-BY-NC, or CC-BY-ND files admitted.

The verified manifest is locked at `stage_64_short_scream_manifest.csv` with SHA-256 digest `658ae11fc79154960c6e675ac184ac126808c01c250d0ff354d4bd26a3f04e5b`.

