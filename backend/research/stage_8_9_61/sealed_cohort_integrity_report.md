# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recordings and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Sealed Evaluation Cohort Integrity & Access Control Report

## 1. Executive Summary & Audit Mandate

The Sealed Evaluation Cohort assembled in Stage 8.9.60 represents an irreplaceable independent benchmark resource. To ensure that evaluation metrics obtained in Track B remain completely unbiased:
1. The sealed manifest must match its recorded cryptographic digest bit-for-bit.
2. The cohort must remain completely quarantined from Track A development, feature tuning, threshold calibration, and candidate selection.
3. Access controls must be audited and verified before any engineering or evaluation code executes.

---

## 2. Cryptographic Manifest Verification

The audit script `backend/research/stage_8_9_61/scripts/verify_sealed_manifest.py` inspected both the JSON manifest and the accompanying SHA-256 seal file:

| Verification Parameter | Specification / Expected Value | Observed Result | Status |
| :--- | :--- | :--- | :---: |
| **Manifest File Path** | `backend/research/stage_8_9_60/future_evaluation_manifest.json` | File present on disk | **PASS** |
| **Seal File Path** | `backend/research/stage_8_9_60/future_evaluation_manifest.sha256` | File present on disk | **PASS** |
| **Expected SHA-256** | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **MATCH (100%)** |
| **Seal Content Match** | Contains canonical SHA-256 string | Matches exact string | **PASS** |
| **Total Cohort Size** | Exactly 700 recordings | 700 entries | **PASS** |
| **Positive Class Size** | Exactly 200 recordings | 200 entries | **PASS** |
| **Negative Class Size** | Exactly 500 recordings | 500 entries | **PASS** |
| **Unique Source Groups** | Exactly 453 source groups | 453 unique IDs | **PASS** |
| **Unique Creators** | Exactly 58 creator accounts | 58 unique IDs | **PASS** |

---

## 3. Access Control Invariants & Quarantine Protocol

The following programmatic access rules are strictly enforced during Stage 8.9.61 Track A:
- **Zero Evaluation Reading:** No Track A script or function (`rolling_window_inference.py`, `compare_temporal_aggregation.py`, `run_development_benchmarks.py`) may load or reference `future_evaluation_manifest.json`.
- **Zero Label Visibility:** Ground-truth labels from the sealed cohort remain quarantined until Phase B3 formal unsealing.
- **Zero Threshold Sweeping:** Thresholds evaluated in Track A are tuned exclusively against `rolling_window_development_manifest.csv`.
- **Pre-Registration Gate:** Phase B3 unsealing is programmatically blocked until Track A candidate freeze and Track B pre-registration are signed and hashed.

