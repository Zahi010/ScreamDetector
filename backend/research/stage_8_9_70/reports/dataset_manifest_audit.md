# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Dataset Manifest & Cohort Quarantine Audit

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.70  
**Audit Scope:** Complete Dataset Manifest Hierarchy & Cohort Quarantine Verification  
**Evaluation Status:** Strict Source-Group Isolation Certified  

---

## 1. Executive Summary

This audit establishes the formal classification, partition isolation, and quarantine status of all acoustic evaluation cohorts utilized in Stage 8.9.70.

To maintain scientific integrity and prevent over-optimistic generalization claims:
1. **Stage 54 Validation Cohort ($N=311$):** Permanently designated as **`EXPOSED_DEVELOPMENT_COHORT`**. Because iterative candidate tuning (Candidates 65-F through 70-D) occurred against this partition, it serves strictly as a development verification benchmark and cannot be cited as unseen out-of-sample evidence.
2. **Stage 60 Sealed Cohort ($N=700$):** Strictly **quarantined, uninspected, and unevaluated**. The manifest SHA-256 integrity hash is verified bit-for-bit.
3. **Stage 64 Held-Out Short-Scream Cohort ($N=268$):** Serves as a source-group-isolated held-out benchmark for short vocal bursts ($< 1.0$s).

---

## 2. Cohort Classification & Quarantine Registry

| Cohort Name | Sample Count ($N$) | Formal Status / Designation | Purpose & Permitted Use | Quarantine Check |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 54 Training** | 1,055 | `TRAINING_PARTITION` | Representation learning and neural feature projection | Clean (Source-grouped) |
| **Stage 54 Validation** | 311 | `EXPOSED_DEVELOPMENT_COHORT` | Development benchmarking, hyperparameter ablation, veto calibration | Exposed (Tuned against) |
| **Stage 54 Reserved Test** | 445 | `SEALED_HISTORICAL_TEST` | Reserved benchmark for final cross-validation | Unmodified |
| **Stage 64 Short Screams** | 268 | `HELD_OUT_BENCHMARK` | Generalization audit for transient screams ($< 1.0$s) across 7 source groups | Clean (0 overlap with S54/S60) |
| **Stage 60 Future Evaluation** | 700 | `QUARANTINED_SEALED_COHORT` | Final independent acceptance evaluation. **STRICTLY LOCKED** | **PASSED (Hash Verified)** |

---

## 3. Quarantined Sealed Cohort Verification (Stage 60)

The Stage 60 sealed evaluation manifest contains $N=700$ previously unexposed recordings reserved for final independent validation.

- **Manifest Path:** `backend/research/stage_8_9_60/future_evaluation_manifest.json`
- **Expected SHA-256 Hash:** `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Actual SHA-256 Hash:** `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd`
- **Verification Status:** **MATCH CONFIRMED — BIT-FOR-BIT IDENTICAL**
- **Quarantine Enforcement:** Zero recordings from this manifest have been read, featurized, evaluated, or inspected during Stage 8.9.70.

---

## 4. Cross-Partition Overlap & Leakage Check

To confirm absence of data contamination, SHA-256 audio PCM hashes were cross-checked across all partitions:

| Partition A | Partition B | Overlapping Hashes | Leakage Status |
| :--- | :--- | :--- | :--- |
| Stage 54 Training ($N=1,055$) | Stage 54 Validation ($N=311$) | 0 | **CLEAN** |
| Stage 54 Training ($N=1,055$) | Stage 64 Held-Out Short ($N=268$) | 0 | **CLEAN** |
| Stage 54 Validation ($N=311$) | Stage 64 Held-Out Short ($N=268$) | 0 | **CLEAN** |
| Stage 60 Sealed ($N=700$) | All Stage 70 Datasets | 0 | **CLEAN (QUARANTINED)** |

---

## 5. Source-Group Independence

Source-group identifiers were verified to ensure that no recording artist, acoustic venue, or recording session is split across training and validation partitions. Every source group is strictly assigned to one and only one partition, ensuring that evaluations test generalization across acoustic capture environments rather than memorization of specific background noise signatures.

