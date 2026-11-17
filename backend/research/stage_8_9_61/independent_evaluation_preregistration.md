# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recordings and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Independent Evaluation Preregistration: Stage 8.9.61 Track B

**Preregistration Timestamp:** 2026-11-11 20:33:00 UTC  
**Phase:** TRACK B INDEPENDENT BENCHMARK PREREGISTRATION  
**Governing Standard:** Antigravity High-Integrity Scientific Protocol  

---

## 1. Research Objectives & Hypotheses

The primary research questions for Track B independent evaluation on the sealed 700-recording evaluation cohort are:
1. **Hypothesis 1 (Generalization of Candidate E1 with C5 DSP):** Does frozen Candidate E1 operating with C5 Combined DSP achieve higher scream recall and lower hard-negative FPR than Candidate B reference on the unexposed 700-recording cohort?
2. **Hypothesis 2 (Temporal Aggregation Efficacy):** Does the experimental rolling-window configuration (`E1_ROLLING_C5_STRATEGY_D`) improve sustained-scream detection ($\ge 1.0$s duration) compared to static 1.0s inference, while maintaining acceptable false positive rates on continuous hard-negative audio?
3. **Hypothesis 3 (Original Acceptance Gates):** Do Candidate E1 configurations satisfy the five mandatory project acceptance gates on the sealed independent cohort?

---

## 2. Sealed Cohort & Candidate Cryptographic Digests

| Evaluation Asset | File Path | Expected SHA-256 Digest |
| :--- | :--- | :--- |
| **Sealed Evaluation Manifest** | `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` |
| **Track A Candidate Freeze** | `backend/research/stage_8_9_61/rolling_window_candidate_freeze.json` | `a56982b014e12697982d927c917f1039de35c72b1dc20a1c9ac61dc74e2275df` |
| **Candidate E1 Checkpoint** | `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` |
| **Candidate B Checkpoint** | `backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` |
| **Intervention D Code** | `backend/research/stage_8_9_49/scripts/whistle_discriminator.py` | `3d98aa7496c6ba89066cfa345a6d0c1ee3605c30821f869a049001c4ad4a8bd2` |
| **C5 Combined DSP Code** | `backend/research/stage_8_9_57/dsp_implementations/c5_combined.py` | `d73cd3bf4d3d1debbaa75b9e57c82d113c3abc500d7ab9b5868b14aa608a9d58` |

---

## 3. Evaluated Candidates & Operational Thresholds

Four frozen candidate configurations will be benchmarked on identical audio:

1. **Candidate 1: `Candidate_E1_Static_C5`**
   - DSP: C5 Combined Filterbank & Phonation.
   - Windowing: Static 1.0s center window (16,000 samples).
   - Decision Threshold: $\theta = 0.6800$ (Frozen historical threshold).
2. **Candidate 2: `Candidate_B_Baseline`**
   - Architecture: DualEncoderAcousticModel (`config_b_mask.pt`).
   - DSP: Original Phase 44 mask-v6 filterbank.
   - Windowing: Static 1.0s center window.
   - Decision Threshold: $\theta = 0.8000$ (Frozen reference threshold).
3. **Candidate 3: `Candidate_B_Intervention_D`**
   - Same as Candidate 2, cascaded with Intervention D referee whistle discriminator.
4. **Candidate 4: `Candidate_E1_Rolling_C5_EMA` (Track A Frozen Experimental Candidate)**
   - DSP: C5 Combined Filterbank & Phonation.
   - Windowing: Rolling 1.0s window with 500 ms hop (50% overlap).
   - Aggregation: Exponential Moving Average ($\alpha = 0.50$).
   - Decision Threshold: $\theta_{EMA} = 0.6000$ (Frozen Track A parameter).

---

## 4. Evaluation Metrics & Statistical Analysis Plan

### Primary Evaluation Metrics:
- **Overall Scream Recall:** $\frac{\text{TP}}{\text{Total Authentic Screams}}$ ($N_{pos} = 200$).
- **Hard-Negative False Positive Rate (FPR):** $\frac{\text{FP}}{\text{Total Hard Negatives}}$ ($N_{neg} = 500$).
- **Shouted-Speech FPR:** $\frac{\text{FP}_{shout}}{N_{shout}}$ ($N_{shout} = 135$).
- **Short-Scream Recall:** $\frac{\text{TP}_{short}}{N_{short}}$ (Duration $< 1.0$s).
- **Sustained-Scream Recall:** $\frac{\text{TP}_{sustained}}{N_{sustained}}$ (Duration $\ge 1.0$s, $N_{sustained} = 169$).
- **Precision and F1-Score.**

### Subgroup Reporting Invariants:
- All 8 acoustic categories will be reported with exact numerators and denominators.
- Subgroups with small sample sizes:
  - **Crowd-Masked Screams ($N=4$):** Explicitly designated as *INSUFFICIENT SAMPLE SIZE FOR GENERALIZATION CLAIMS*.
  - **Low-Intensity Screams ($N=27$):** Reported with full binomial confidence intervals.
  - No subgroup denominators will be obscured behind percentages.

### Statistical Significance Methodology:
- **Confidence Intervals:** 95% Wilson score intervals for binomial proportions.
- **Clustered Bootstrap:** 2,000 bootstrap iterations clustered by `source_group_id` (453 unique source groups) to compute design-effect-corrected confidence bounds for metric deltas.
- **Paired Statistical Tests:** Exact McNemar's test for paired classification comparisons between Candidate E1 and Candidate B.
- **Multiple Comparisons:** Benjamini-Hochberg FDR correction applied at $q = 0.05$.

---

## 5. Execution Command & Anti-Tampering Protocol

- **Execution Command:**
  ```powershell
  python festival-scream-detector/backend/research/stage_8_9_61/scripts/run_preregistered_evaluation.py
  ```
- **One-Shot Evaluation Rule:** The evaluation cohort may only be evaluated once under this frozen preregistration.
- **Strict Prohibition Against Post-Hoc Rerunning:** If a candidate fails an acceptance gate, results must be reported honestly. No threshold tuning, hyperparameter adjustments, or model retraining is permitted after observing unsealed results.
