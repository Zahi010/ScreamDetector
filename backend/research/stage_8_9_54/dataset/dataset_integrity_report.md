# Dataset & Source-Group Reconciliation Report — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Source-Group Discrepancy Investigation & Resolution

### Root Cause Analysis
In Stage 8.9.52, the dataset curator drafted the source-group partitioning summary table in `source_group_audit.md` using theoretical proportional calculations from an estimated 705 source groups:
- Claimed Train: $705 \times 0.60 = 423$
- Claimed Val: $705 \times 0.20 = 141$
- Claimed Test: $705 \times 0.20 = 141$
- Claimed Total: $423 + 141 + 141 = 705$

However, physical inspection of `expansion_manifest.csv` and `build_expansion_dataset.py` reveals the actual deduplicated unique source groups totaled **693**:
- Deterministic random shuffle split:
  - `expansion_train`: `int(0.60 * 693)` = **415 unique source groups** (1,055 clips).
  - `expansion_val`: `int(0.20 * 693)` = **138 unique source groups** (311 clips).
  - `expansion_reserved_test`: $693 - 415 - 138$ = **140 unique source groups** (366 clips).
  - Actual Total: $415 + 138 + 140 = 693$.

### Discrepancy Classification:
**The discrepancy is definitively resolved as a clerical typographical reporting error in Stage 8.9.52 text.**
- Zero recordings were excluded or deleted.
- Zero source groups were dropped or modified.
- The manifest has remained completely unchanged.
- All 366 recordings in `expansion_reserved_test` originate from exactly 140 independent source groups.

---

## 2. Partition Summary Table

| Partition | Total Clips | Positive Clips | Negative Clips | Unique Source Groups | Mean Clips/SG | Partition Governance |
|---|---|---|---|---|---|---|
| **`expansion_train`** | 1,055 | 371 | 684 | **415** | 2.54 | Model Retraining & Ablations |
| **`expansion_val`** | 311 | 108 | 203 | **138** | 2.25 | Early Stopping & Threshold Selection |
| **`expansion_reserved_test`** | 366 | 102 | 264 | **140** | 2.61 | **Evaluated Historical Test Set (Quarantined)** |
| **Total** | **1,732** | **581** | **1,151** | **693** | 2.50 | 100% Permissive Commercial-Intent |

> [!IMPORTANT]
> The 366-recording `expansion_reserved_test` cohort was evaluated in Stage 8.9.53 and is strictly marked as a historical evaluation set. It will NOT be used for training, validation, early stopping, threshold selection, or model tuning in Stage 8.9.54.

---

## 3. Strict Source-Group Disjointness Verification
$$\mathcal{SG}_{\text{train}} \cap \mathcal{SG}_{\text{val}} = \emptyset \quad (0 \text{ overlapping SGs})$$
$$\mathcal{SG}_{\text{train}} \cap \mathcal{SG}_{\text{test}} = \emptyset \quad (0 \text{ overlapping SGs})$$
$$\mathcal{SG}_{\text{val}} \cap \mathcal{SG}_{\text{test}} = \emptyset \quad (0 \text{ overlapping SGs})$$

Zero leakage exists across any partition boundary.
