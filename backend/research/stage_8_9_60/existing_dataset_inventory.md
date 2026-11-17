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

This stage is a research audit, legal dataset acquisition, and evaluation cohort construction stage. It does not authorize model training or production changes.

---

# Existing Dataset Inventory & Historical Partition Baseline

## 1. Executive Summary

Prior to initiating Stage 8.9.60 acquisition, a comprehensive inventory of all historical audio recordings in the festival scream detection research repository was conducted. The historical corpus spans Stage 8.9.50 through Stage 8.9.59, encompassing production baselines, experimental training partitions, and quarantined validation/test splits.

To guarantee complete cryptographic and source-level independence for newly acquired audio, an immutable historical exclusion registry (`historical_exclusion_registry.csv`) comprising **2,213 unique recording entries** was compiled from:
1. Stage 8.9.54 Partition Manifest (`partition_manifest_verified.csv`): 1,080 recordings.
2. Frozen Benchmark Evaluation Test Set (`frozen_test_manifest.json`): 433 recordings.
3. Stage 8.9.55 Independent Evaluation Cohort: 700 recordings.

Any candidate recording matching a file SHA-256 digest, raw PCM digest, source group identifier, or creator session in this registry was strictly disqualified from Stage 8.9.60 acquisition.

---

## 2. Historical Repository Partition Breakdown

| Partition / Manifest Name | Scope / Role | Total Recordings | Positive Screams | Hard Negatives | Unique Source Groups | Quarantine Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `expansion_train` (Stage 8.9.54) | Training Candidate E1 | 540 | 175 | 365 | 212 | FROZEN — TRAINING HISTORY |
| `expansion_val` (Stage 8.9.54) | Threshold Tuning & Val | 174 | 55 | 119 | 78 | FROZEN — DEV VALIDATION |
| `expansion_reserved_test` (Stage 8.9.53/54) | Independent Audit Test | 366 | 102 | 264 | 141 | QUARANTINED — HISTORICAL TEST |
| `frozen_test_manifest.json` | Reference Benchmark Test | 433 | 120 | 313 | 185 | QUARANTINED — BENCHMARK TEST |
| `stage_8_9_55_cohort` | Blind Generalization Test | 700 | 200 | 500 | 442 | QUARANTINED — STAGE 55 TEST |
| **Combined Historical Exclusion Registry** | **De-duplicated Unique** | **2,213** | **652** | **1,561** | **1,058** | **PERMANENT RESEARCH EXCLUSION** |

---

## 3. Subgroup Distribution in Historical Partitions

Analysis of historical partitions in Stage 8.9.59 revealed critical acoustic representation gaps that drove the Stage 8.9.60 acquisition protocol:

1. **Severe Under-Representation of Low-Intensity Screams:**
   - Historical partitions contained only 18 low-intensity screams across all sets combined.
   - Candidate E1 exhibited a 55.6% false-negative rate on muffled or low-amplitude screams in Stage 8.9.55 evaluation.
2. **Severe Under-Representation of Crowd-Masked Screams (SNR < 10 dB):**
   - Less than 2% of screams in historical datasets had background festival crowd noise below 10 dB SNR.
   - High-noise screams accounted for 42.1% of false negatives in Stage 8.9.55.
3. **Imbalance in Negative Class Confusers:**
   - Environmental noise and sirens were over-represented (over 60% of negatives), while conversational shouting and referee whistles were under-represented.
   - Shouted speech generated 18 false positives in Candidate E1 due to high harmonic energy in the 1–3 kHz region.
4. **Duration Discrepancies:**
   - Brief screams (< 0.5s) represented 45% of historical positive samples, whereas sustained distress vocalizations (>= 1.0s) were scarce.

---

## 4. Exclusion Registry Implementation and Verification

The historical exclusion registry was synthesized into `backend/research/stage_8_9_60/historical_exclusion_registry.csv` and loaded into acquisition filters. Every candidate sound was checked against:
- `recording_id` exact string match.
- `file_sha256` 64-character hexadecimal digest.
- `pcm_sha256` raw uncompressed audio payload digest.
- `source_group_id` parent recording lineage identifier.
- `creator_id` uploader username / content producer ID.

This guaranteed that the Stage 8.9.60 acquisition pool of 962 recordings represents **100% fresh, unconsumed acoustic material** with zero risk of train-test leakage.

