# STAGE 8.9.30.2 — SOURCE OVERLAP & COHORT INDEPENDENCE REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.30.2  
**Investigation:** Historical Cohort Identity of the Six Missed Short Screams  
**Date:** November 2, 2026  

---

## 1. EXECUTIVE SUMMARY

A critical question formulated in Stage 8.9.30.2 is whether the six short screams that failed detection in Stage 8.9.30 were:
1. Re-tested historical recordings that previously passed earlier models.
2. Different excerpts of known historical recordings.
3. Genuinely new, previously un-evaluated independent recordings.

Forensic hashing, provenance tracing, and census cross-referencing confirm that **all six recordings are 100% genuinely new, independent empirical scream recordings**.

Zero overlap exists between these six recordings and:
- Stage 5 held-out test predictions (`backend/reports/test_predictions.csv`).
- Stage 8.9.27 independent baseline manifest (`independent_dataset_manifest.csv`).
- Historical workspace census (`workspace_audio_census.csv`).
- Stage 8.9.25 / 8.9.26 development test splits.

---

## 2. DETAILED IDENTITY MATRIX

| Recording ID | Original Source ID | Uploader | Duration | SHA-256 Checksum | Historical Overlap Status |
|---|---|---|---:|---|---|
| `S8930_FS_686340` | `686340` | `trim8361` | 0.395s | `0b7dfc89f5ce8c80...` | **GENUINELY NEW (Zero Overlap)** |
| `S8930_FS_222582` | `222582` | `qubodup` | 0.719s | `839fc415950d8b58...` | **GENUINELY NEW (Zero Overlap)** |
| `S8930_FS_382990` | `382990` | `JúliaLN` | 0.421s | `eebf23028fb0fb31...` | **GENUINELY NEW (Zero Overlap)** |
| `S8930_FS_547188` | `547188` | `MrFossy` | 0.766s | `078c6b75ee396ba2...` | **GENUINELY NEW (Zero Overlap)** |
| `S8930_FS_788867` | `788867` | `riippumattog`| 0.650s | `4a046c8e390c1598...` | **GENUINELY NEW (Zero Overlap)** |
| `S8930_NIGENS_HUMAN-SCREAM_GEN-HDF-15246` | `GEN-HDF-15246` | `nigens_zenodo`| 0.499s | `327a3c30707bfdd0...` | **GENUINELY NEW (Zero Overlap)** |

---

## 3. SCIENTIFIC RECONCILIATION: WHY DID PREVIOUS SHORT SCREAMS PASS?

The fact that these six recordings are genuinely new resolves a key paradox:
- Earlier stages reported $86.4\%$ to $90.9\%$ recall on short screams ($< 0.8\text{ s}$) because those evaluations tested **different historical recordings** (e.g. `REC_SCR_0114`, `REC_SCR_0249`, `REC_SCR_0318` from Stage 8.9.25's held-out test split) using **offline clip-level zero-padding**.
- Stage 8.9.30 tested a **newly acquired cohort** of six previously unseen empirical recordings using a **streaming ring-buffer harness** that dropped unpadded chunks $< 0.975\text{ s}$.
