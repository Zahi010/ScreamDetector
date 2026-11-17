# Stage 8.9.38 — Source-Group Leakage & Partition Isolation Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.38 — Dataset Integration, Independent Cohort Construction & Controlled Retraining Preparation  
**Author:** Principal Acoustic AI Research Scientist & ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed (100% Clean Isolation Verified)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Executive Summary

To guarantee that model evaluations reflect genuine acoustic generalization rather than speaker/environment memorization, Stage 8.9.38 conducted an exhaustive **source-group leakage audit** across all partitions in [`research_split_v4.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/research_split_v4.csv).

The audit verified **zero source-group leakage (0 collisions)** across all active partition pairs. In particular, all **35 newly acquired short-scream source groups reserved for independent testing are 100% isolated** from training and validation pools.

---

## 2. Partition Pair Overlap Matrix

Every active recording was grouped by `source_group_id`. All pairwise intersections between active research splits were audited and logged in [`source_group_split_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_38/manifests/source_group_split_manifest.csv):

| Partition A | Partition B | Source Groups A | Source Groups B | Overlapping Source Groups | Isolation Status |
|---|---|---|---|---|---|
| `v4_train` | `v4_val` | 324 | 114 | **0** | **100% ISOLATED (PASS)** |
| `v4_train` | `v4_historical_test` | 324 | 111 | **0** | **100% ISOLATED (PASS)** |
| `v4_train` | `v4_reserved_expansion_test` | 324 | 49 | **0** | **100% ISOLATED (PASS)** |
| `v4_val` | `v4_historical_test` | 114 | 111 | **0** | **100% ISOLATED (PASS)** |
| `v4_val` | `v4_reserved_expansion_test` | 114 | 49 | **0** | **100% ISOLATED (PASS)** |
| `v4_historical_test` | `v4_reserved_expansion_test` | 111 | 49 | **0** | **100% ISOLATED (PASS)** |

---

## 3. Short-Scream 35-Group Reservation Audit

The 85 newly acquired short-scream recordings span 42 independent source groups:
- **Reserved for Held-Out Testing (`v4_reserved_expansion_test`):**
  - **35 source groups** (71 clips, durations $0.221\text{--}0.880\text{ s}$).
  - Source group IDs: `source_group_short_scream_001` through `source_group_short_scream_035`.
  - Overlap with training: **0 clips, 0 groups**.
  - Overlap with validation: **0 clips, 0 groups**.
- **Allocated to Training (`v4_train`):**
  - **5 source groups** (10 clips).
  - Source group IDs: `source_group_short_scream_036` through `source_group_short_scream_040`.
- **Allocated to Validation (`v4_val`):**
  - **2 source groups** (4 clips).
  - Source group IDs: `source_group_short_scream_041` and `source_group_short_scream_042`.

---

## 4. Parent-Recording Excerpt Integrity

In addition to source-group ID matching, excerpt parent IDs (`original_recording_id`) were audited to ensure no segmented excerpts from the same recording session crossed partition boundaries:
- Historical parent recordings in training: 739 unique parent sessions.
- Historical parent recordings in test: 293 unique parent sessions.
- Expansion parent recordings in training: 31 unique parent sessions.
- Expansion parent recordings in reserved test: 49 unique parent sessions.
- **Cross-Partition Parent Collisions Detected:** **0 collisions**.
