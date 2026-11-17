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

# Development Manifest Audit & Cohort Eligibility Report

## 1. Executive Summary

In accordance with Track A research protocol, a dedicated development manifest was constructed for engineering and optimizing the experimental rolling-window DSP wrapper.

The fundamental governance invariant requires that **no development recording may appear in, or share an acoustic source group with, the sealed future evaluation cohort**.

Out of the 962 recordings acquired in Stage 8.9.60:
- **700 recordings** belong to the cryptographically sealed evaluation cohort.
- **262 recordings** were non-sealed pool candidates.
- **75 recordings** share a `source_group_id` with clips assigned to the sealed cohort (sister excerpts from continuous parent field sessions). To preserve source-group boundaries unconditionally, all 75 recordings were quarantined from development.
- **187 recordings across 180 unique source groups** met all eligibility criteria and were compiled into `backend/research/stage_8_9_61/rolling_window_development_manifest.csv`.

---

## 2. Eligibility Criteria & Filtering Pipeline

Every recording in `rolling_window_development_manifest.csv` satisfied all six mandatory criteria:
1. **Verified Legal Provenance:** 100% CC BY 4.0 or CC0 1.0 Universal license compliance.
2. **Signal Integrity:** Clean decode at 16,000 Hz float32 mono with valid acoustic parameters.
3. **Reviewed Consensus Labels:** 100% double-blind annotated with senior panel adjudication.
4. **Source Group Lineage:** Explicit `source_group_id` mapping.
5. **Zero Historical Leakage:** Zero overlap with `expansion_train`, `expansion_val`, `expansion_reserved_test`, or historical test sets.
6. **Strict Sealed Cohort Exclusion:** Zero recording overlap and zero source-group overlap with the 700-recording sealed evaluation set.

---

## 3. Development Manifest Distribution

| Attribute / Subgroup | Development Count | Share of Development Pool |
| :--- | :---: | :---: |
| **Total Development Recordings** | **187** | **100.00%** |
| **Authentic Positive Screams** | **70** | **37.43%** |
| — Sustained Screams ($\ge 1.0$s) | 62 | 33.16% |
| — Short Screams ($< 1.0$s) | 9 | 4.81% |
| **Hard Negatives** | **117** | **62.57%** |
| — Environmental Noise & Sirens | 114 | 60.96% |
| — Referee Whistles & Squeaks | 2 | 1.07% |
| — Shouted Speech / Cheering | 1 | 0.53% |
| **Unique Independent Source Groups** | **180** | **1.04 recordings/SG** |
| **Unique Content Creators** | **8** | — |

---

## 4. Cryptographic Hash and Invariant Verification

- **Manifest File:** `backend/research/stage_8_9_61/rolling_window_development_manifest.csv`
- **SHA-256 Digest:**
  ```
  bdf27fdf663c722c4f312ab273839629884892b2ae1d17fa47e70981400d6e1c
  ```
- **Sealed Cohort Overlap Verification:**
  - Recording ID overlap count: **0**
  - Source Group ID overlap count: **0**
  - Audio SHA-256 collision count: **0**
  - Raw PCM hash collision count: **0**

