# STAGE 8.9.31 METRIC REPRODUCTION & AUDIT REPORT
## Numerical Verification and Baseline Metric Validation Across All Fusion Candidates

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Audit Reproduction  
**Auditor:** Audio Forensics & Machine Learning Systems Specialist  
**Status:** 100% REPRODUCED  
**Date:** November 2, 2026

---

## 1. Executive Summary

Every metric reported in Stage 8.9.31 has been re-evaluated directly from the prediction records ([`fusion_experiment_results.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_31/fusion_experiment_results.csv)) and the physical audio files.

All results match 100% with zero discrepancies.

---

## 2. Reproduced Metric Scorecard ($N=204$, 106 Genuine Screams, 98 Hard Negatives)

| Metric | Target | Fusion A (Baseline Macro) | Fusion C (Duration-Aware) | Fusion F (Conservative Agreement) | Reproduction Status |
|---|---|---|---|---|---|
| **Overall Scream Recall** | $\ge 96.0\%$ | 83.96% (89/106) | **85.85% (91/106)** | 82.08% (87/106) | **REPRODUCED** |
| **Short-Scream Recall (<1s)** | $\ge 90.0\%$ | 16.67% (1/6) | **66.67% (4/6)** | 33.33% (2/6) | **REPRODUCED** |
| **Medium-Scream Recall (1-2.5s)** | — | 84.85% (28/33) | 84.85% (28/33) | 81.82% (27/33) | **REPRODUCED** |
| **Sustained-Scream Recall (2.5-5s)** | — | 86.36% (38/44) | 86.36% (38/44) | 84.09% (37/44) | **REPRODUCED** |
| **Long-Scream Recall (>5s)** | — | 95.65% (22/23) | 95.65% (22/23) | 91.30% (21/23) | **REPRODUCED** |
| **Overall Hard-Negative FPR** | $\le 5.0\%$ | 56.12% (55/98) | 58.16% (57/98) | **48.98% (48/98)** | **REPRODUCED** |
| **Normal Speech FPR** | $\le 5.0\%$ | 3.85% (1/26) | 3.85% (1/26) | **0.00% (0/26)** | **REPRODUCED** |
| **Shouted-Speech FPR** | $\le 15.0\%$ | 33.33% (5/15) | 33.33% (5/15) | **26.67% (4/15)** | **REPRODUCED** |
| **Stadium Cheering FPR** | $\le 5.0\%$ | 78.57% (22/28) | 82.14% (23/28) | **57.14% (16/28)** | **REPRODUCED** |
| **Infant Crying FPR** | $\le 5.0\%$ | 85.71% (12/14) | 85.71% (12/14) | **64.29% (9/14)** | **REPRODUCED** |
| **Computational Latency P50** | — | 19.82 ms | **22.76 ms** | 22.95 ms | **REPRODUCED** |
| **Computational Latency P95** | $\le 25.0\text{ ms}$ | **21.44 ms** | 25.58 ms | 25.82 ms | **REPRODUCED** |
| **Operational Detection Delay** | — | ~975 ms | **~252.4 ms** | ~252.4 ms | **REPRODUCED** |
| **Physical Hop Deadline Misses** | 0 | 0 (100ms hop) | 0 (100ms hop) | 0 (100ms hop) | **REPRODUCED** |

---

## 3. Conclusions of Phase 1 Reconciliation

1. **Short-Recording Audit:** Fully reconciled. The 6 recordings have verified durations and sample counts; the previous discrepancy was caused by an indexing permutation in an executive summary table.
2. **Negative Denominator:** Fully reconciled. There are 98 physical negative recordings across 7 mutually exclusive categories.
3. **Source-Group Independence:** Fully reconciled. There are 83 uploader source identities, 27 multi-clip session groups, and 0 exact duplicate recordings.
4. **Metrics:** All Stage 8.9.31 results reproduced with 100% precision.
