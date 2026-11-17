# Stage 8.9.37 — Per-Model Threshold Optimization, Calibration Audit & Dataset Expansion Final Report

**Project:** Festival Scream Detector  
**Stage:** 8.9.37  
**Author:** Principal Acoustic AI Research Scientist & Independent ML Validation Auditor  
**Date:** November 2026  
**Status:** Completed  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE

---

## 1. Executive Summary

Stage 8.9.37 executed a rigorous forensic, mathematical, and experimental audit of the Festival Scream Detector research candidates, evaluating whether per-model threshold tuning or probability calibration could bridge the performance gap to the five research acceptance gates, and laying the foundation for empirical dataset expansion.

### What Was Completed:
1. **Production Freeze Verification:** Verified all four production artifact SHA-256 hashes before and after research execution; production classifier and threshold (0.3500) remain 100% frozen.
2. **Unified Prediction Auditing:** Extracted, aligned, and validated prediction outputs across all four eligible model architectures on both the validation ($N=293$) and untouched test ($N=293$) cohorts.
3. **Per-Model Threshold Sweeps:** Evaluated thresholds from $\theta = 0.05$ to $0.95$ in $0.01$ increments on validation data only, computing all classification metrics, subgroup false-positive rates, and diagnostic curves.
4. **Multi-Operating-Point Selection:** Derived four distinct validation-selected operating points per model (Point A: Max F1, Point B: Recall-Oriented, Point C: False-Alarm-Oriented, Point D: Balanced Operational Point).
5. **Matched-Operating-Point Comparison:** Evaluated candidate trade-offs under matched validation operating conditions ($\text{HN-FPR} \approx 5\%$ and $\text{Recall} \approx 80\%$).
6. **Probability Calibration Audit:** Fitted Platt scaling and Isotonic regression strictly on validation data; evaluated Brier score, Expected Calibration Error (ECE), reliability diagrams, and category score distributions.
7. **Single Frozen Test Evaluation:** Evaluated frozen validation-selected thresholds once on the untouched independent test cohort ($N=293$: 102 screams, 191 hard negatives), computing 95% Wilson confidence intervals, exact sample fractions, and P95 latency.
8. **Short-Scream Power Analysis:** Formally analyzed statistical evidence limitations of the current test set ($N=5$).
9. **Dataset Expansion Manifests:** Acquired candidate manifests for 85 short screams (42 source groups, 35 reserved for test) and 165 multi-talker hard negatives (54 source groups).
10. **License & Duplicate Audits:** Enforced commercial-intent policy (175 CC-BY, 54 CC0, 21 CC-NC quarantined); verified 0 exact SHA-256 duplicates and zero source-group partition leakage.
11. **Blinded Label Adjudication:** Executed a two-reviewer blinded protocol on two suspected label anomalies (`gasp-oooh` and `another-surprised-oooh`), adjudicating both as non-scream while preserving test cohort integrity.
12. **Automated Test Suite:** Created and passed 11 comprehensive automated tests verifying all stage constraints.

### What Was NOT Completed / Out of Scope:
- **No Model Retraining:** Retraining of neural architectures was strictly forbidden in this stage.
- **No Production Promotion:** None of the research models were deployed to production.
- **Physical Dataset Integration:** Audio files were cataloged and verified in manifests; model training on new clips awaits subsequent training stages.

### Did Threshold Optimization Improve Any Candidate?
**Yes, moderately, but with critical caveats.** 
- For Configuration D (MP-FS-DualEncoder), adjusting the threshold from baseline $0.35$ to validation-optimal $\theta^* = 0.43$ reduced hard-negative FPR from $14.66\%$ down to $9.95\%$ (a 32% relative reduction in false alarms) while maintaining high test recall ($89.22\%$, 91/102).
- For Configuration B (Dual-Encoder), moving to $\theta^* = 0.44$ reduced HN-FPR to $6.28\%$ (12/191) at $81.37\%$ recall.
- **However, threshold optimization did NOT allow any candidate to satisfy all five research gates.**

### Did Calibration Help?
**Calibration significantly improved probability interpretability and reduced ECE (-67% on Dual-Encoder), but did NOT alter classification discrimination.** Because Platt scaling and Isotonic regression are monotonic transformations, ROC-AUC and PR-AUC remain unchanged. Platt scaling did, however, allow setting canonical thresholds ($\theta = 0.50$) with equivalent optimal operating behavior.

### Were Dataset Expansion Targets Achieved?
**Yes, 100% achieved:**
- Short screams: 85 acquired (target: $\ge 80$).
- Hard negatives: 165 acquired (target: $\ge 150$).
- Reserved short-scream test groups: 35 reserved (target: $\ge 35$).

### Did Any Candidate Pass All Five Research Gates?
**NO.** No candidate passed all five research acceptance gates simultaneously on the independent test cohort.

---

## 2. Frozen Test Set Candidate Comparison

The table below displays the single frozen evaluation on the independent test cohort ($N=293$: 102 screams, 191 hard negatives, 48 shouted speech, 5 short screams). Every threshold was frozen strictly on validation data prior to test evaluation.

| Model Candidate | Validation Threshold $\theta^*$ | Calibration | Test Recall ($k/n$) | Test HN-FPR ($k/n$) | Test Shout-FPR ($k/n$) | Short-Scream Recall ($k/n$) | P95 Latency (ms) | All 5 Gates Passed? |
|---|---|---|---|---|---|---|---|---|
| **Config A (YAMNet-Only)** | 0.38 (Point A: Max F1) | Uncalibrated | 70.59% (72/102) | 9.95% (19/191) | 18.75% (9/48) | 80.00% (4/5) | 19.44 ms | **FAIL** (Gates 1, 3, 4) |
| | 0.34 (Point D: Balanced) | Uncalibrated | 87.25% (89/102) | 16.75% (32/191) | 25.00% (12/48) | 80.00% (4/5) | 19.44 ms | **FAIL** (Gates 1, 2, 3, 4) |
| | 0.35 (Frozen Prod Thresh) | Uncalibrated | 78.43% (80/102) | 12.04% (23/191) | 22.92% (11/48) | 80.00% (4/5) | 19.44 ms | **FAIL** (Gates 1, 2, 3, 4) |
| **Config B (Dual-Encoder)** | 0.44 (Point A: Max F1) | Uncalibrated | 81.37% (83/102) | 6.28% (12/191) | **8.33% (4/48)** | 80.00% (4/5) | 19.52 ms | **FAIL** (Gates 1, 2, 4) |
| | 0.15 (Point D: Balanced) | Uncalibrated | 87.25% (89/102) | 13.09% (25/191) | **10.42% (5/48)** | 80.00% (4/5) | 19.52 ms | **FAIL** (Gates 1, 2, 4) |
| | 0.50 (Point A: Platt Calib) | Platt Scaling | 81.37% (83/102) | 6.28% (12/191) | **8.33% (4/48)** | 80.00% (4/5) | 19.52 ms | **FAIL** (Gates 1, 2, 4) |
| | 0.35 (Frozen Prod Thresh) | Uncalibrated | 84.31% (86/102) | 7.85% (15/191) | **8.33% (4/48)** | 80.00% (4/5) | 19.52 ms | **FAIL** (Gates 1, 2, 4) |
| **Config C (YAMNet+Subband)**| 0.30 (Point A: Max F1) | Uncalibrated | 78.43% (80/102) | 10.47% (20/191) | 20.83% (10/48) | 80.00% (4/5) | 20.32 ms | **FAIL** (Gates 1, 2, 3, 4) |
| | 0.27 (Point D: Balanced) | Uncalibrated | 91.18% (93/102) | 15.18% (29/191) | 25.00% (12/48) | **100.0% (5/5)** | 20.32 ms | **FAIL** (Gates 1, 2, 3) |
| | 0.35 (Frozen Prod Thresh) | Uncalibrated | 70.59% (72/102) | 7.85% (15/191) | 16.67% (8/48) | 60.00% (3/5) | 20.32 ms | **FAIL** (Gates 1, 2, 3, 4) |
| **Config D (MP-FS-DualEnc)** | 0.43 (Point A: Max F1) | Uncalibrated | **89.22% (91/102)** | 9.95% (19/191) | **14.58% (7/48)** | **100.0% (5/5)** | 19.46 ms | **FAIL** (Gates 1, 2) |
| | 0.43 (Point D: Balanced) | Uncalibrated | **89.22% (91/102)** | 9.95% (19/191) | **14.58% (7/48)** | **100.0% (5/5)** | 19.46 ms | **FAIL** (Gates 1, 2) |
| | 0.50 (Point A: Platt Calib) | Platt Scaling | **89.22% (91/102)** | 9.95% (19/191) | **14.58% (7/48)** | **100.0% (5/5)** | 19.46 ms | **FAIL** (Gates 1, 2) |
| | 0.35 (Frozen Prod Thresh) | Uncalibrated | 91.18% (93/102) | 14.66% (28/191) | 16.67% (8/48) | **100.0% (5/5)** | 19.46 ms | **FAIL** (Gates 1, 2, 3) |

---

## 3. Threshold Optimization Analysis

### 3.1 Model-Specific Threshold Preferences
- **Config A (YAMNet-Only):** Benefits from a slightly higher threshold ($\theta^* = 0.38$ vs. $0.35$). At $0.35$, it suffers excessive false alarms ($12.04\%$ HN-FPR). Raising to $0.38$ drops HN-FPR to $9.95\%$, but recall falls to $70.59\%$.
- **Config B (Dual-Encoder):** Benefits from a higher threshold ($\theta^* = 0.44$ vs. $0.35$). Raising the threshold suppresses hard negatives to $6.28\%$ and shouted speech to $8.33\%$ (satisfying Gate 3), but leaves recall at $81.37\%$.
- **Config C (YAMNet + Subband):** Needs a lower threshold ($\theta^* = 0.30$ or $0.27$) because its subband features depress raw scores. However, lowering the threshold results in catastrophic shout false positives ($25.00\%$).
- **Config D (MP-FS-DualEncoder):** Benefits substantially from $\theta^* = 0.43$ over $0.35$. At $0.43$, it satisfies Gate 3 (Shout-FPR = $14.58\% \le 15\%$), achieves $100\%$ short-scream test recall ($5/5$), and achieves the highest overall recall of any model at $<10\%$ HN-FPR ($89.22\%$, 91/102).

### 3.2 Constraint Feasibility
- Can any candidate satisfy Gate 1 (Recall $\ge 96\%$) and Gate 2 (HN-FPR $\le 5\%$) simultaneously?
  - **NO.** When constrained to $\text{HN-FPR} \le 5\%$, all four models experience a severe recall drop (YAMNet drops to $58.23\%$, Dual-Encoder to $48.10\%$, MP-FS to $55.70\%$).
- Test results **closely confirmed validation expectations**: the validation optimal F1 threshold ($\theta^* = 0.43$) for MP-FS-DualEncoder also proved optimal on the test cohort, maintaining an F1 of $0.8626$.

---

## 4. Probability Calibration Analysis

- **Are raw scores calibrated?** No. Raw neural outputs suffer from ECE up to $0.1902$ and substantial overconfidence in intermediate bins.
- **Does Platt scaling help?** Yes. Platt scaling reduced ECE from $0.1217$ to $0.0401$ on Dual-Encoder and to $0.0597$ on MP-FS-DualEncoder. Test Brier score improved from $0.1004$ to $0.0945$.
- **Does calibration improve classification decisions?** No. Calibration rescales scores monotonically; it does not change sample rankings or separate overlapping distributions. Its value lies in transparent risk reporting and standardizing decision thresholds to $0.50$.

---

## 5. Dataset Status & Adjudication

| Dataset Component | Target Metric | Achieved Value | Status |
|---|---|---|---|
| Short-scream recordings | $\ge 80$ recordings | **85 recordings** ($0.22\text{--}0.88\text{ s}$) | **Achieved** |
| Hard-negative recordings | $\ge 150$ recordings | **165 recordings** (10 fine-grained categories) | **Achieved** |
| Reserved test source groups | $\ge 35$ groups | **35 source groups** (70 clips reserved) | **Achieved** |
| Total expansion source groups | Independent | **96 source groups** | **Achieved** |
| Commercial License Clear | Permissive policy | **229 eligible** (175 CC-BY, 54 CC0) | **Achieved** |
| License Quarantine | Commercial protection | **21 quarantined** (CC BY-NC isolated) | **Achieved** |
| Duplicate SHA-256 Collisions | Zero duplicate risk | **0 collisions** against historical & internal | **Verified** |
| Partition Leakage | Zero source group leak | **0 leaked source groups** | **Verified** |
| Suspected Positive Anomaly | Blinded review | **2/2 unanimous non-scream** (retained in test) | **Completed** |

---

## 6. Limitations & Evidence Quality

1. **Short-Scream Sample Size Deficit:** The current test set contains only $N=5$ short screams. Although MP-FS-DualEncoder detected $5/5$ ($100\%$), the 95% Wilson confidence interval is $[56.6\%, 100.0\%]$ (width = $43.4\%$). This is **INSUFFICIENT EVIDENCE** to certify real-world short-scream generalization.
2. **Acoustic Overlap in High-F0 Non-Screams:** Distant screaming and excited crowd shouting share fundamental vocal frequency bands ($F_0 > 600\text{ Hz}$). Without temporal sequence modeling or contextual attention, stationary spectral features cannot achieve $<5\%$ HN-FPR at $>90\%$ recall.
3. **Statistical Power for Future Gating:** While reserving 35 short-scream test groups will narrow the CI width from $43.4\%$ to $\sim 14\%$, verifying Gate 4 with lower confidence bound $\ge 90\%$ will require scaling the short-scream test cohort to $N \ge 120$.

---

## 7. Production Integrity Verification

All four production artifacts were verified before and after execution:

| Artifact | Expected SHA-256 | Measured SHA-256 | Match |
|---|---|---|---|
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **YES** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **YES** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **YES** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **YES** |

- **Production Decision Threshold:** 0.3500 (STRICTLY PRESERVED).
- **Production Classifier:** Stage 5 Logistic Regression (STRICTLY PRESERVED).
- **Production Inference Pipeline:** UNCHANGED.

---

## 8. Final Stage Decision

**THRESHOLD AUDIT COMPLETE — DATASET EXPANSION CONTINUES**

*Rationale:* The threshold sweep and calibration audits are 100% complete, proving that individual operating points improve performance (MP-FS-DualEncoder reaches 89.22% recall, 9.95% HN-FPR, 14.58% Shout-FPR at $\theta^* = 0.43$) and Platt calibration improves probability interpretability. However, mathematical optimization alone cannot overcome acoustic feature overlap to meet all five gates. The dataset expansion candidate cohort (85 short screams, 165 hard negatives, 35 reserved test groups, 0 leakage) has been fully cataloged and audited, clearing the path for retraining and larger-scale empirical validation in future stages.
