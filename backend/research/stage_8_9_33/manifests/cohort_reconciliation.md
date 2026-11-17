# EVALUATION COHORT RECONCILIATION & CATEGORY CROSSWALK
## Forensic Reconciliation of Historical Evaluation Manifests (Stages 8.9.27 - 8.9.32)

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Phase Zero  
**Status:** 100% RECONCILED  
**Date:** November 2, 2026  

---

## 1. Executive Summary: Resolving All Apparent Inconsistencies

Prior stage reports referenced different sample counts that appeared inconsistent in conversational summaries:
- **Stadium Cheering: 28 vs 42**
- **Infant Crying: 14 vs 15**
- **Shouted Speech: 2 vs 48**
- **Hard-Negative Total: 98 vs 191**

### The Forensic Audit Finding:
These figures represent **two distinct, disjoint evaluation cohorts**, not conflicting counts of the same dataset:

1. **Audited Cohort ($N=204$):** Evaluated in Stages 8.9.30.1 and 8.9.31.
   - 106 genuine screams + 98 hard negatives.
   - Categories: Cheering ($28$), Speech ($26$), Crying ($14$), Control ($14$), Siren ($13$), Shouting ($2$), Noise ($1$). Sum = **98**.

2. **Independent Test Split ($N=293$):** Established in Stage 8.9.32 from the 1,325-sample multi-source dataset.
   - 102 genuine screams + 191 hard negatives across 142 isolated source groups.
   - Categories: Cheering ($42$), Crying ($15$), Shouting ($48$), Sirens/Fireworks ($28$), Whistles ($32$), Environmental ($26$). Sum = **191**.

3. **Cross-Cohort Overlap:** There is **0 file overlap** between the 204-recording audited cohort and the 293-recording independent test partition. They are completely disjoint.

---

## 2. Frozen Evaluation Cohort Policy for Stage 8.9.33
To ensure scientific integrity and eliminate any possibility of cohort mixing:
- **Primary Acceptance Benchmark:** Every candidate model evaluated for the 5 acceptance gates must be evaluated on the **exact same $N=293$ independent test partition**.
- **Diagnostic Forensic Benchmark:** The 6 short-scream recordings and the $N=204$ audited cohort are reported separately as diagnostic benchmarks.
- **No Threshold Tuning on Test:** Decision thresholds must be tuned on the validation partition ($N=293$) and strictly frozen before running test inference.
