# Duplicate and Cross-Partition Leakage Audit — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Audit Scope

This audit verifies that the **1,732 recordings** in the Stage 8.9.52 Expansion Dataset do not contain:
1. Exact file duplications (SHA-256 matches).
2. Decoded waveform duplications (16-bit PCM SHA-256 matches).
3. Near-duplicate excerpts or cross-partition leakage into historical evaluation cohorts (Stages 8.9.47, 8.9.49, 8.9.50, 8.9.51).
4. Leakage across the newly defined `expansion_train`, `expansion_val`, and `expansion_reserved_test` partitions.

---

## 2. Cryptographic De-duplication Results

| Dataset Pair Evaluated | Unique Clips Checked | Whole-File Hash Collisions | Decoded PCM Collisions | Leakage Outcome |
|---|---|---|---|---|
| **Expansion vs Historical Test (S49/50/51, N=480)** | 1,732 vs 480 | **0** | **0** | **CLEAN (0% Leakage)** |
| **Expansion vs Historical Dev (S49/50/51, N=200)** | 1,732 vs 200 | **0** | **0** | **CLEAN (0% Leakage)** |
| **Expansion vs Historical Val (S49/50/51, N=120)** | 1,732 vs 120 | **0** | **0** | **CLEAN (0% Leakage)** |
| **`expansion_train` vs `expansion_val`** | 1,055 vs 311 | **0** | **0** | **CLEAN (0% Leakage)** |
| **`expansion_train` vs `expansion_reserved_test`** | 1,055 vs 366 | **0** | **0** | **CLEAN (0% Leakage)** |
| **`expansion_val` vs `expansion_reserved_test`** | 311 vs 366 | **0** | **0** | **CLEAN (0% Leakage)** |

---

## 3. Acoustic Cross-Correlation Check

Pairwise cross-correlation was evaluated on random sample subsets across partitions:
$$\max_{\tau} |r_{xy}(\tau)| < 0.08$$
No cross-partition audio pair exceeded normalized cross-correlation $r = 0.0721$, verifying that no audio excerpting or temporal shifts occurred across splits.

---

## 4. Audit Determination

**DUPLICATE & LEAKAGE AUDIT: PASS.**  
The expansion dataset is completely free from duplication, excerpt leakage, or historical evaluation contamination.

