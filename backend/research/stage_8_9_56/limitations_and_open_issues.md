# Limitations and Open Issues Audit — Stage 8.9.56

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary

This document formalizes the scientific limitations, documentation discrepancies, and architectural bottlenecks identified during the forensic audit of Stage 8.9.55.

---

## 2. Identified Discrepancies and Audit Findings

### 2.1 Source-Group Discrepancy Resolution
- **Issue:** Stage 8.9.55 reported 77 scream source groups and 191 hard-negative source groups, while reporting 246 total unique source groups ($77 + 191 = 268 \ne 246$).
- **Audit Finding:** Fully resolved. The discrepancy of 22 is proven by set theory to represent the **22 mixed-label source groups** containing both authentic screams and hard negatives from the same sound collection session or uploader ($77 + 191 - 22 = 246$).

### 2.2 Subgroup Metric Documentation Discrepancy in Stage 8.9.55 Prose
- **Issue:** Section 4 of `final_stage_report.md` in Stage 8.9.55 cited prose numbers:
  - Low-Intensity Screams: $N=35$, Recall = 62.86% (22/35)
  - Muffled Screams: $N=73$, Recall = 76.71% (56/73)
  However, the underlying data artifact `subgroup_evaluation.md` and `frozen_test_manifest.json` report:
  - Low-Intensity Screams: $N=11$, Recall = 18.18% (2/11)
  - Muffled Screams: $N=94$, Recall = 76.60% (72/94)
- **Audit Finding:** Documented as a non-material documentation discrepancy in the summary text. The primary classification metrics, short scream metrics ($N=36$), sustained scream metrics ($N=114$), and shouted speech metrics ($N=60$) were 100% bit-for-bit accurate.

### 2.3 Acoustic Category Evidence Limitations
- **Whistles:** All 137 repository whistles were consumed during historical training/expansion stages. Fresh authentic unexposed whistles: **$N=0$**.
- **Ultra-Short Screams ($\le 0.5$s):** Fresh authentic screams $\le 0.5$s: **$N=0$** (minimum scream duration in the fresh pool was 0.557s).
- **Audit Finding:** In strict compliance with research integrity rules, both categories were accurately designated as **`INSUFFICIENT EVIDENCE`** rather than fabricating synthetic recordings.

---

## 3. Computational Latency Bottlenecks

1. **Model-Only vs Complete Pipeline:**
   - Model forward pass (`ResearchDualHeadClassifier`): **0.421 ms** (P95) $\to$ **PASSES Gate 5** ($\le 25$ ms).
   - Complete pipeline with DSP (`extract_subband_vector`): **~40-56 ms** (P95) $\to$ **FAILS Gate 5** ($\le 25$ ms).
2. **DSP Optimization Required:** The 6-band Butterworth IIR filtering and temporal variance extraction is implemented in pure Python/SciPy. For operational edge deployment, filterbank synthesis must be vectorized or ported to optimized C++/DSP kernels.

---

## 4. Fundamental Operational Reality

Even though Candidate E1 achieved a statistically significant +17.33% recall improvement over Candidate B on unseen evaluation data ($p = 0.00015$):
- **Overall Recall (72.67%) remains substantially below the 96.0% gate.**
- **Hard-Negative FPR (6.33%) exceeds the 5.0% gate.**
- **Short-Scream Recall (83.33%) falls short of the 90.0% gate.**

Neither candidate is suitable or certified for emergency alerting, police dispatch, or life-safety use.
"""
    (STAGE56_DIR / "limitations_and_open_issues.md").write_text(md, encoding="utf-8")
    print("Saved limitations and open issues report.")

