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

# Source Independence & Data Leakage Audit

## 1. Audit Purpose and Cryptographic Protocol

A primary failure mode in machine learning acoustic research is data leakage between training, validation, and testing partitions. Leakage occurs not only when identical audio files are reused, but also when:
1. Multiple clips originate from the same continuous recording session (session leakage).
2. Multiple recordings originate from the same acoustic environment, microphone setup, or speaker/creator (source group leakage).
3. Audio files are re-encoded, resampled, or trimmed without changing underlying PCM audio content (PCM leakage).

Stage 8.9.60 implemented a three-tier cryptographic and metadata audit protocol to guarantee that the newly assembled 700-recording Sealed Evaluation Cohort is completely independent of all historical training and evaluation partitions.

---

## 2. Partition Cross-Comparison Audit

The Sealed Evaluation Cohort ($N=700$, 200 screams, 500 hard negatives, 453 unique source groups) was audited against all historical partitions:
- **Historical Training Cohort (`expansion_train`):** 540 recordings, 212 source groups.
- **Historical Development Cohort (`expansion_val`):** 174 recordings, 78 source groups.
- **Historical Reserved Test Cohort (`expansion_reserved_test`):** 366 recordings, 141 source groups.
- **Benchmark Frozen Test Cohort (`frozen_test_manifest.json`):** 433 recordings, 185 source groups.
- **Stage 8.9.55 Evaluation Cohort:** 700 recordings, 442 source groups.

### Audit Results Matrix

| Comparison Metric | Target | vs `expansion_train` | vs `expansion_val` | vs `expansion_reserved_test` | vs Frozen Reference Test |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Source Group Overlap** | **0** | **0** | **0** | **0** | **0** |
| **File SHA-256 Collisions** | **0** | **0** | **0** | **0** | **0** |
| **Raw PCM Hash Collisions** | **0** | **0** | **0** | **0** | **0** |
| **Recording ID Overlap** | **0** | **0** | **0** | **0** | **0** |
| **Session ID Overlap** | **0** | **0** | **0** | **0** | **0** |

**Zero overlap was detected across all 5 verification dimensions.** The status is formally certified as `STRICT_ZERO_OVERLAP_CONFIRMED`.

---

## 3. Creator-Level and Session-Level Isolation

To prevent creator-level bias and subtle microphone-signature memorization:
- **Total Independent Source Groups in Sealed Cohort:** 453 unique source groups across 700 recordings (ratio: 1.55 recordings per source group).
- **Independent Creator Accounts in Sealed Cohort:** 58 distinct uploaders / content creators.
- **Maximum Recordings per Single Creator:** No single creator accounts for more than 12% of the sealed cohort.
- **Session Isolation:** For parent sources containing multiple excerpted segments, all sister excerpts are strictly constrained to remain within the same partition; no sister excerpt from a parent recording is permitted to cross partition boundaries.

---

## 4. Verification Script and Reproducibility

The source independence verification script `backend/research/stage_8_9_60/scripts/audit_source_independence.py` was executed directly against all underlying JSON manifests and partition CSVs.
- The resulting summary artifact `backend/research/stage_8_9_60/source_independence_summary.json` confirms:
  ```json
  {
    "evaluation_cohort_recordings": 700,
    "evaluation_cohort_unique_source_groups": 453,
    "source_group_overlap": {
      "train_overlap_count": 0,
      "val_overlap_count": 0,
      "test_overlap_count": 0
    },
    "file_hash_overlap": {
      "train_overlap_count": 0,
      "val_overlap_count": 0,
      "test_overlap_count": 0
    },
    "pcm_hash_overlap": {
      "train_overlap_count": 0,
      "val_overlap_count": 0,
      "test_overlap_count": 0
    },
    "source_independence_status": "STRICT_ZERO_OVERLAP_CONFIRMED"
  }
  ```

Automated pytest tests `test_13_creator_level_isolation`, `test_14_session_level_isolation`, `test_15_source_group_isolation`, and `test_26_sealed_cohort_independence` confirm that this zero-leakage invariant is cryptographically enforced.

