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

# Future Sealed Evaluation Cohort Report: Construction, Stratification & Cryptographic Seal

## 1. Executive Summary & Design Protocol

In accordance with Stage 8.9.60 research governance, an independent, source-isolated evaluation cohort was constructed and cryptographically sealed. This cohort is designated exclusively for **blind, future candidate evaluation** (e.g., evaluating Candidate E1 with optimized C5 DSP, rolling-window architectures, or future retrained models).

The evaluation cohort is strictly quarantined:
- **No model training:** Zero training or fine-tuning may utilize these recordings.
- **No threshold calibration:** Decision thresholds may not be swept, tuned, or optimized against this cohort.
- **No feature adaptation:** Preprocessing parameters or DSP filters may not be fitted to this data.

---

## 2. Sealed Cohort Composition & Stratification

The Sealed Evaluation Cohort comprises exactly **700 recordings** selected via stratified sampling from the Stage 8.9.60 acquisition pool:
- **Positive Screams:** 200 recordings (28.57%)
- **Hard Negatives:** 500 recordings (71.43%)
- **Unique Source Groups:** 453 independent source groups (requirement: $\ge 370$; achieved: 453, a surplus of +83 source groups).
- **Independent Creator Accounts:** 58 distinct uploaders.
- **Average Clips per Source Group:** 1.55 (ensuring high acoustic heterogeneity).

### Granular Subtype Breakdown

| Class | Acoustic Subtype | Recording Count | Share of Class | Share of Cohort |
| :--- | :--- | :---: | :---: | :---: |
| **Positive Class** | Sustained Screams ($\ge 1.0$s) | 169 | 84.5% | 24.14% |
| **Positive Class** | Low-Intensity & Muffled Screams | 27 | 13.5% | 3.86% |
| **Positive Class** | Crowd-Masked Screams (SNR < 10 dB) | 4 | 2.0% | 0.57% |
| **SUBTOTAL SCREAMS** | **All Positive Vocalizations** | **200** | **100.0%** | **28.57%** |
| **Negative Class** | Diverse Shouted Speech | 135 | 27.0% | 19.29% |
| **Negative Class** | Cheering & Crowd Chanting | 51 | 10.2% | 7.29% |
| **Negative Class** | Referee Whistles & Squeaks | 50 | 10.0% | 7.14% |
| **Negative Class** | Infant Crying | 19 | 3.8% | 2.71% |
| **Negative Class** | Environmental Noise & Sirens | 245 | 49.0% | 35.00% |
| **SUBTOTAL NEGATIVES** | **All Hard Negatives** | **500** | **100.0%** | **71.43%** |
| **TOTAL COHORT** | **Sealed Future Evaluation Set** | **700** | — | **100.00%** |

---

## 3. Cryptographic Sealing and Manifest Integrity

The sealed cohort was serialized to JSON and sealed with an immutable SHA-256 cryptographic digest.

- **Manifest File:** `backend/research/stage_8_9_60/future_evaluation_manifest.json`
- **Seal File:** `backend/research/stage_8_9_60/future_evaluation_manifest.sha256`
- **Canonical SHA-256 Digest:**
  ```
  9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd
  ```

Any modification, addition, deletion, or re-ordering of entries in `future_evaluation_manifest.json` alters this digest and invalidates future audit verification.

---

## 4. Source Independence Verification

A cross-manifest audit verified that the 700 recordings in the Sealed Cohort have:
- **0 source group overlap** with `expansion_train`, `expansion_val`, and `expansion_reserved_test`.
- **0 file SHA-256 hash overlap** with any historical partition.
- **0 PCM payload hash overlap** with any historical partition.
- **0 collisions** with the 2,213-entry `historical_exclusion_registry.csv`.

Pytest verification tests `test_26_sealed_cohort_independence`, `test_27_sealed_manifest_hash_verification`, and `test_28_sealed_label_access_restrictions` pass with 100% compliance.

