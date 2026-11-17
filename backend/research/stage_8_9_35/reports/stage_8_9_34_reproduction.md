# STAGE 8.9.35 — CHECKPOINT 1: STAGE 8.9.34 REPRODUCTION & BASELINE AUDIT

**Project:** Festival Scream Detector  
**Stage:** 8.9.35 — Spatial Audio Research, Frequency-Subband Discrimination & Multi-Pathway Fusion  
**Operating Mode:** Machine Learning Validation Auditor & Signal Processing Specialist  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** November 2, 2026  

---

## 1. REPRODUCTION SUMMARY & CANDIDATE BASELINE MATRIX

Checkpoint 1 requires independent verification of all Stage 8.9.34 candidate models and metrics on the authoritative held-out test cohort ($N=293$, 102 screams, 191 hard negatives across 111 source groups) at the frozen operating threshold $\theta^* = 0.3500$.

### 1.1 Verified Historical Metrics

| Candidate Model | Scream Recall | Hard-Negative FPR | Shouted-Speech FPR | P95 Latency | Audit Status | Predefined Gates Met? |
|---|---:|---:|---:|---:|---|---|
| **Dual-Encoder Baseline (8.9.33)** | **84.31%** | 7.85% | **8.33%** | **18.57 ms** | EXACT MATCH | Gates 3 & 5 PASS; Gates 1 & 2 FAIL |
| **Candidate B (Causal GRU)** | 79.41% | **6.28%** | **8.33%** | 18.72 ms | EXACT MATCH | Gates 3 & 5 PASS; Gates 1 & 2 FAIL |
| **Candidate C (Causal TCN)** | 78.43% | **6.28%** | **8.33%** | 18.84 ms | EXACT MATCH | Gates 3 & 5 PASS; Gates 1 & 2 FAIL |
| **Candidate D (Gated Aggregator)** | 80.39% | 6.81% | **8.33%** | 18.64 ms | EXACT MATCH | Gates 3 & 5 PASS; Gates 1 & 2 FAIL |
| **Combined TSA-DualEncoder (8.9.34)** | 80.39% | 6.81% | 10.42% | 20.07 ms | EXACT MATCH | Gates 3 & 5 PASS; Gates 1 & 2 FAIL |

### 1.2 Data Partition Immutability Check
- **Held-Out Test Partition:** Exactly 293 recordings (102 screams, 191 negatives).
- **Source Groups:** 111 disjoint source groups.
- **Leakage Audit:** 0 overlapping recording IDs, 0 overlapping uploader IDs, and 0 overlapping source groups between Train ($N=739$), Val ($N=293$), and Test ($N=293$).

---

## 2. CHECKPOINT 1 DETERMINATION

All Stage 8.9.34 metrics, predictions, and baseline artifacts have been reproduced with 100% precision.
**CHECKPOINT 1 OFFICIALLY APPROVED.** Safe to proceed to Checkpoint 2.
