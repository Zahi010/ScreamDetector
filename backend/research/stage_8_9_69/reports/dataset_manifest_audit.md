# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.69 — DATASET MANIFEST AUDIT & DATA INDEPENDENCE REPORT

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.
Non-certified experimental acoustic research system. Not for emergency detection, autonomous dispatch, or critical security deployment.

---

## 1. Executive Summary & Exposure Classification

This audit certifies the data separation, source-group disjointness, and evaluation exposure status across all acoustic dataset partitions utilized in the Festival Scream Detector research project.

### Critical Audit Findings
1. **Validation Set Exposure:** The Stage 54 Validation cohort ($N=311$, 138 source groups) is officially designated as:
   $$\mathbf{EXPOSED\_DEVELOPMENT\_COHORT}$$
   *Rationale:* This partition has undergone repeated candidate evaluation, threshold calibration ($\theta \in [0.480, 0.520]$), and veto rule refinement across Stages 8.9.65 through 8.9.69. While model weights were not trained with gradient descent on this partition, hyperparameters and calibration rules have been tuned against its error distributions. Consequently, validation metrics must not be interpreted as unbiased generalization evidence.
2. **Sealed Cohort Quarantined:** The Stage 60 Sealed Evaluation Cohort ($N=700$, 453 source groups) remains **quarantined, uninspected, and unevaluated**. Its manifest hash has been independently verified as bit-for-bit identical to its frozen state:
   - Manifest Path: `backend/research/stage_8_9_60/future_evaluation_manifest.json`
   - Verified SHA-256: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
3. **Strict Source-Group Independence:** All dataset partitions maintain strict pairwise disjointness with **zero source-group overlap**.

---

## 2. Partition Architecture & Provenance Matrix

| Partition Name | Provenance Stage | Recording Count ($N$) | Unique Source Groups | Exposure Classification | Role in Stage 8.9.69 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `expansion_train` | Stage 8.9.54 | 1,055 | 415 | `TRAINING_COHORT` | Primary neural training split (C5 + vocal features) |
| `expansion_val` | Stage 8.9.54 | 311 | 138 | `EXPOSED_DEVELOPMENT_COHORT` | Hyperparameter selection, ablation tournament, threshold tuning |
| `expansion_reserved_test`| Stage 8.9.54 | 366 | 140 | `HELD_OUT_BENCHMARK` | Independent post-development test split (strictly disjoint) |
| `held_out_short_screams` | Stage 8.9.67 | 268 | 7 | `HELD_OUT_BENCHMARK` | Dedicated short-duration acoustic benchmark ($d < 1.0$s) |
| `sealed_evaluation_cohort`| Stage 8.9.60 | 700 | 453 | `SEALED_QUARANTINE_COHORT` | **QUARANTINED & LOCKED** — SHA-256 verified |

---

## 3. Source-Group Disjointness Verification

To guarantee that acoustic leakage does not occur via identical recording sessions, microphone environments, or voice actors, pairwise source-group intersections were computed across all partitions:

$$\begin{aligned}
\text{train} \cap \text{val} &= \emptyset \quad (|415 \cap 138| = 0) \\
\text{train} \cap \text{reserved\_test} &= \emptyset \quad (|415 \cap 140| = 0) \\
\text{val} \cap \text{reserved\_test} &= \emptyset \quad (|138 \cap 140| = 0) \\
\text{sealed\_cohort} \cap (\text{train} \cup \text{val} \cup \text{reserved\_test}) &= \emptyset \quad (|453 \cap 693| = 0)
\end{aligned}$$

No audio clip shares an original session ID, Freesound author identifier, or synthetic noise profile across split boundaries.

---

## 4. Held-Out Short-Scream Benchmark Evaluation ($N=268$)

In Stage 8.9.67, an independent benchmark of 268 short screams ($d < 1.0$s) from disjoint recording sources was compiled to measure how candidate models generalize to short, high-stress vocalizations without exposure during threshold tuning:

| Candidate Architecture | Calibrated Threshold | Stage 54 Val Short Recall ($N=39$) | Held-Out Short Recall ($N=268$) | Generalization Delta |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate 65-F (Reference)** | 0.480 | 97.44% (38/39) | 98.13% (263/268) | $+0.69\%$ |
| **Candidate 67-D (Historical Champion)** | 0.520 | 92.31% (36/39) | 54.48% (146/268) | $-37.83\%$ |
| **Candidate 68-D (Historical Candidate)** | 0.490 | 92.31% (36/39) | 58.58% (157/268) | $-33.73\%$ |
| **Candidate 69-A (HFCR Rescue)** | 0.490 | 92.31% (36/39) | 58.58% (157/268) | $-33.73\%$ |
| **Candidate 69-B (SNR-Adaptive)** | 0.490 | 92.31% (36/39) | 58.58% (157/268) | $-33.73\%$ |
| **Candidate 69-C (Noise-Robust Bypass)** | 0.490 | 92.31% (36/39) | 58.96% (158/268) | $-33.35\%$ |
| **Candidate 69-D (Champion)** | 0.492 | 92.31% (36/39) | 58.21% (156/268) | $-34.10\%$ |

### Audit Interpretation of Generalization Delta
- While Candidate 65-F achieved 98.13% recall on held-out short screams, it incurred an intolerable 48.86% shouted-speech FPR and 59.68% hard-negative FPR, rendering it non-viable for practical deployment.
- Candidate 67-D, 68-D, and 69-D successfully reduced shouted-speech FPR from 48.86% down to 13.64% by incorporating non-linear acoustic vetoes.
- However, on held-out short screams without high SNR or clear vocal fold chaotic roughness, the short scream recall drops to ~58.21%. This confirms that acoustic feature representations of short screams in low SNR conditions remain an open research problem requiring advanced temporal aggregation or self-supervised representations.

---

## 5. Certification of Sealed Cohort Integrity

The sealed cohort `backend/research/stage_8_9_60/future_evaluation_manifest.json` has NOT been loaded into memory during any evaluation in Stage 8.9.69.
- Expected SHA-256: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- Computed SHA-256: `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- Status: **SEALED — UNTOUCHED — VERIFIED IDENTICAL**

