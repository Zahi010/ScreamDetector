# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.71 — Dataset Manifest, Governance & Cohort Quarantine Audit

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.71  
**Audit Scope:** Complete Dataset Manifest Hierarchy, Cluster Verification & Cohort Quarantine Status  
**Governance Status:** Strict Source-Group Independence & Quarantine Compliance Certified  

---

## 1. Executive Summary

This audit establishes the formal data classification, cohort isolation, and quarantine governance for Stage 8.9.71.

To maintain absolute scientific rigor and avoid over-optimistic generalization claims:
1. **Stage 54 Validation Partition ($N=311$):** Formally designated and permanently restricted as **`EXPOSED_DEVELOPMENT_COHORT`**. Because Candidates 65-F through 71-D have been evaluated against this partition during iterative research, it serves strictly as a development verification benchmark and cannot be cited as unseen out-of-sample evidence.
2. **Stage 64 Held-Out Short-Scream Partition ($N=268$):** Formally classified as **`DIAGNOSTIC_EVALUATION_BENCHMARK`**. Lineage auditing proves it contains 7 source groups with heavy clustering (over 61% of clips originate from `sg_short_s49`). It must not be cited as 268 independent statistical degrees of freedom.
3. **Stage 60 Sealed Cohort ($N=700$):** Strictly **quarantined, uninspected, unread, and unevaluated**. Its manifest SHA-256 integrity hash is verified bit-for-bit.

---

## 2. Cohort Registry & Exposure Classification

| Cohort Name | Sample Count ($N$) | Source Group Count | Formal Governance Classification | Purpose & Usage Boundary | Quarantine Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 54 Training** | 1,055 | 68 | `TRAINING_PARTITION` | Representation learning and neural feature projection | Active training pool |
| **Stage 54 Validation** | 311 | 24 | `EXPOSED_DEVELOPMENT_COHORT` | Development benchmarking, hyperparameter ablation, veto calibration | Exposed (Iteratively tuned against) |
| **Stage 54 Reserved Test** | 445 | 32 | `SEALED_HISTORICAL_TEST` | Reserved benchmark for prospective final cross-validation | Unmodified & preserved |
| **Stage 64 Short Screams** | 268 | 7 | `DIAGNOSTIC_EVALUATION_BENCHMARK` | Generalization audit for transient screams ($< 1.0$s) across 7 source groups | Clustered diagnostic set |
| **Stage 60 Future Evaluation** | 700 | 453 | `QUARANTINED_SEALED_COHORT` | Final independent acceptance evaluation. **STRICTLY LOCKED** | **PASSED (Hash Verified: 9dfa4ced...)** |

---

## 3. Stage 60 Quarantined Sealed Cohort Verification

The Stage 60 sealed evaluation manifest contains $N=700$ recordings reserved for independent validation across 453 source groups.

- **Manifest Path:** `backend/research/stage_8_9_60/future_evaluation_manifest.json`
- **Expected SHA-256 Hash:** `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Actual SHA-256 Hash:** `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Verification Status:** **CONFIRMED BIT-FOR-BIT IDENTICAL**
- **Quarantine Protocol Enforcement:** Zero recordings, ground-truth annotations, or predictions from this cohort were accessed, featurized, or evaluated in Stage 8.9.71.

---

## 4. Cross-Partition Overlap & Leakage Check

To ensure that no audio data contaminated the evaluation splits, SHA-256 audio PCM hashes were cross-checked across all partitions:

| Partition A | Partition B | Overlapping Hashes | Leakage Status |
| :--- | :--- | :--- | :--- |
| Stage 54 Training ($N=1,055$) | Stage 54 Validation ($N=311$) | 0 | **CLEAN (0.0% Overlap)** |
| Stage 54 Training ($N=1,055$) | Stage 64 Held-Out Short ($N=268$) | 0 | **CLEAN (0.0% Overlap)** |
| Stage 54 Validation ($N=311$) | Stage 64 Held-Out Short ($N=268$) | 0 | **CLEAN (0.0% Overlap)** |
| Stage 60 Sealed ($N=700$) | All Stage 71 Datasets | 0 | **CLEAN (QUARANTINED)** |

---

## 5. Parent-Recording & Clustering Audit

In the 268-clip held-out short-scream collection:
- `sg_short_s49` (164 clips) originates from 12 distinct parent festival recording sessions.
- `sg_short_supp` (34 clips) originates from 4 distinct environmental noise recordings.
- `sg_short_s43` (37 clips) originates from 3 amphitheater recording sessions.

Because temporal slices from the same parent recording share identical recording devices, frequency responses, and ambient background noise, performance is clustered. Stage 8.9.71 mandates the use of **cluster-aware bootstrap confidence intervals** to prevent false claims of narrow confidence intervals.

