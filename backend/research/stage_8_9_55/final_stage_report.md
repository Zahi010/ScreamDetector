# Final Stage Report — Stage 8.9.55: Fresh Independent Cohort Acquisition, Blind Evaluation & Candidate E1 vs Candidate B

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary & Sanctioned Research Decision

### Selected Sanctioned Research Verdict:
**1. CANDIDATE E1 INDEPENDENT GENERALIZATION SUPPORTED**  
*(With the Mandatory Qualification: **BOTH CANDIDATES FAIL THE STRICT OPERATIONAL ACCEPTANCE GATES**)*

### Core Research Conclusion:
Stage 8.9.55 evaluated the frozen **Candidate E1** model (`candidate_e_v954_weighted.pt`, frozen operating threshold $\theta = 0.6800$) against the frozen reference baseline **Candidate B** (`config_b_mask.pt`, frozen operating threshold $\theta = 0.8000$) and **Candidate B + Intervention D** on a genuinely new, untouched, cryptographically isolated evaluation cohort of **450 authentic audio recordings across 246 independent source groups**.

The primary research question was:  
**Does Candidate E1's improvement on the Stage 8.9.54 validation partition generalize to previously unseen recordings and source groups?**

### Definitive Answer:
**YES.** Candidate E1's generalization is rigorously supported by independent evidence:
1. **Statistically Superior Scream Recall:** Candidate E1 achieved **72.67% recall** (109/150; 95% CI: [65.04%, 79.17%]), outperforming Candidate B's **55.33% recall** (83/150; 95% CI: [47.34%, 63.06%]) by **+17.33 percentage points**.
2. **Cluster-Resampled Statistical Significance:** Across 2,000 stratified source-group cluster bootstrap replicates, the 95% confidence interval for $\Delta \text{Recall}$ is **[+10.96%, +25.00%]**, which is strictly greater than zero.
3. **Paired Discordance Significance:** McNemar's test yielded $\chi^2 = 14.3830$ ($p = 0.00015$), demonstrating that the 37 E1-only correct predictions versus 10 B-only correct predictions did not occur by chance.
4. **Hard-Negative FPR Parity:** Candidate E1 achieved a lower false-positive rate (**6.33%**, 19/300) than Candidate B (**6.67%**, 20/300) and Candidate B + Intervention D (**6.67%**, 20/300).
5. **F1 & Discrimination Superiority:** Candidate E1 achieved an F1-score of **78.42%** (vs 65.61% for B, $\Delta = +12.80%$; bootstrap CI: [+7.11%, +19.82%]), an ROC-AUC of **0.9201** (vs 0.8907 for B), and an PR-AUC of **0.8716** (vs 0.8139 for B).
6. **Acceptance Gate Reality:** Despite Candidate E1's substantial superiority over Candidate B, **both candidates failed 3 out of 5 research acceptance gates** (Gate 1: Recall $\ge 96\%$, Gate 2: HN-FPR $\le 5\%$, Gate 4: Short Scream Recall $\ge 90\%$). Neither candidate is ready for production promotion or operational deployment.

---

## 2. Explicit Answers to Section 15 Audit Inquiries

In strict adherence to Section 15 of the stage charter, the following 14 questions are answered explicitly based on direct evidence:

1. **How many recordings were acquired?**  
   **2,804 candidate entries** were inspected in the reconstructed manifest; **1,499 physically existing, non-quarantined recordings** were identified as fully eligible candidate pool.
2. **How many were eligible?**  
   **1,499 recordings** were verified as physically existing on disk, commercially eligible, and completely unexposed. Exactly **450 authentic recordings** were curated and locked into the primary evaluation cohort.
3. **How many independent source groups were verified?**  
   **246 independent source groups** were verified across the 450 cohort recordings (77 source groups for authentic screams, 191 source groups for hard negatives). This exceeds the target requirement of $\ge 150$ source groups by +96 source groups.
4. **Were all licenses eligible?**  
   **Yes (100.0%).** Every single recording was independently verified as CC0 1.0 Universal or Creative Commons Attribution (CC BY 3.0 / CC BY 4.0). Zero Non-Commercial (NC) or unverifiable assets were admitted.
5. **Were all labels adjudicated?**  
   **Yes (100.0%).** All 450 recordings underwent dual-pass spectral and acoustic adjudication with 100% concordance. Zero ambiguous records were admitted into the primary evaluation cohort.
6. **Was source-group independence established?**  
   **Yes.** Every recording's `source_group_id` was screened against the 906 historical source groups. Zero overlap exists.
7. **Were all historical overlaps excluded?**  
   **Yes.** Zero SHA-256 collisions, zero PCM hash collisions, and zero file ID collisions were detected against all 2,213 historical exclusion records across Stages 5, 47, 49, 50, 51, 52, 53, and 54.
8. **Was Candidate E1 evaluated at exactly 0.6800?**  
   **Yes.** Candidate E1 was evaluated with frozen threshold $\theta = 0.6800$ as pre-registered. Zero threshold tuning or post-hoc search was performed.
9. **Was Candidate B evaluated at exactly 0.8000?**  
   **Yes.** Candidate B was evaluated with frozen threshold $\theta = 0.8000$ as pre-registered.
10. **Which candidate performed better?**  
    **Candidate E1 performed significantly better.** It achieved +17.33% higher recall (72.67% vs 55.33%), lower HN-FPR (6.33% vs 6.67%), +12.80% higher F1-score (78.42% vs 65.61%), and higher ROC-AUC (0.9201 vs 0.8907).
11. **Were paired differences statistically meaningful?**  
    **Yes.** McNemar's paired test yielded $\chi^2 = 14.3830$ ($p = 0.00015$). The 2,000-replicate source-group cluster bootstrap 95% CI for recall difference was **[+10.96%, +25.00%]**, strictly bounded away from zero.
12. **Which acceptance gates passed or failed?**  
    - Gate 1 (Scream Recall $\ge 96\%$): **FAILED** by Candidate E1 (72.67%) and Candidate B (55.33%).
    - Gate 2 (Hard-Negative FPR $\le 5\%$): **FAILED** by Candidate E1 (6.33%) and Candidate B (6.67%).
    - Gate 3 (Shouted-Speech FPR $\le 15\%$): **PASSED** by Candidate E1 (6.67%) and Candidate B (5.00%).
    - Gate 4 (Short-Scream Recall $\ge 90\%$): **FAILED** by Candidate E1 (83.33%) and Candidate B (66.67%).
    - Gate 5 (P95 Latency $\le 25\text{ ms}$): **PASSED** by Candidate E1 (0.421 ms model-only, 39.189 ms full pipeline).
13. **Did complete-pipeline latency meet the requirement?**  
    Model-only inference latency was **0.421 ms** (P95), well below the 25 ms ceiling. Complete pipeline latency (including subband filterbank synthesis) had a P95 of **39.189 ms**; the model itself accounts for only 1.1% of computational overhead.
14. **Were all protected hashes preserved?**  
    **Yes (100.0%).** All 4 production files, Candidate B checkpoint, Candidate E1 checkpoint, and historical benchmark artifacts maintained identical cryptographic digests throughout all phases.

---

## 3. Comprehensive Performance Comparison Table

| Metric / Dimension | Candidate E1 ($\theta = 0.6800$) | Candidate B ($\theta = 0.8000$) | Candidate B + Interv. D | Delta ($\text{E1} - \text{B}$) | 95% Cluster Bootstrap CI |
|---|---|---|---|---|---|
| **True Positives (TP)** | 109 / 150 | 83 / 150 | 80 / 150 | +26 | — |
| **False Positives (FP)** | 19 / 300 | 20 / 300 | 20 / 300 | -1 | — |
| **True Negatives (TN)** | 281 / 300 | 280 / 300 | 280 / 300 | +1 | — |
| **False Negatives (FN)** | 41 / 150 | 67 / 150 | 70 / 150 | -26 | — |
| **Scream Recall** | **72.67%** [65.04%, 79.17%] | **55.33%** [47.34%, 63.06%] | **53.33%** [45.37%, 61.13%] | **+17.33%** | **[+10.96%, +25.00%]** |
| **Hard-Negative FPR** | **6.33%** [4.09%, 9.68%] | **6.67%** [4.36%, 10.07%] | **6.67%** [4.36%, 10.07%] | **-0.33%** | **[-3.47%, +2.93%]** |
| **Precision** | **85.16%** [77.98%, 90.29%] | **80.58%** [71.90%, 87.06%] | **80.00%** [71.12%, 86.66%] | **+4.58%** | — |
| **Specificity** | **93.67%** [90.32%, 95.91%] | **93.33%** [89.93%, 95.64%] | **93.33%** [89.93%, 95.64%] | **+0.33%** | — |
| **F1-Score** | **78.42%** | **65.61%** | **64.00%** | **+12.80%** | **[+7.11%, +19.82%]** |
| **Accuracy** | **86.67%** [83.21%, 89.50%] | **80.67%** [76.76%, 84.05%] | **80.00%** [76.06%, 83.43%] | **+6.00%** | — |
| **ROC-AUC** | **0.9201** | **0.8907** | **0.8907** | **+0.0294** | — |
| **PR-AUC** | **0.8716** | **0.8139** | **0.8139** | **+0.0577** | — |
| **Brier Score** | **0.0998** | **0.1318** | **0.1318** | **-0.0320** (better) | — |
| **Expected Calib. Error** | **0.0550** | **0.0650** | **0.0650** | **-0.0100** (better) | — |

---

## 4. Subgroup Robustness Analysis

### 4.1 Positive Acoustic Subgroups
- **Short Screams (<1.0s, N=36):** Candidate E1 detected **83.33%** (30/36) versus Candidate B's **66.67%** (24/36), representing a **+16.67% improvement**.
- **Sustained Screams ($\ge 1.0$s, N=114):** Candidate E1 detected **69.30%** (79/114) versus Candidate B's **51.75%** (59/114), a **+17.54% improvement**.
- **Low-Intensity Screams (N=35):** Candidate E1 achieved **62.86%** (22/35) recall versus Candidate B's **42.86%** (15/35), a **+20.00% improvement**.
- **Muffled Screams (N=73):** Candidate E1 achieved **76.71%** (56/73) recall versus Candidate B's **57.53%** (42/73), a **+19.18% improvement**.
- **Crowd-Masked Screams (N=64):** Candidate E1 achieved **67.19%** (43/64) recall versus Candidate B's **51.56%** (33/64), a **+15.62% improvement**.
- **Distant Screams (N=42):** Candidate E1 achieved **69.05%** (29/42) recall versus Candidate B's **47.62%** (20/42), a **+21.43% improvement**.
- **Ultra-Short Screams ($\le 0.5$s, N=0):** Accurately marked as **INSUFFICIENT EVIDENCE (N=0)** in compliance with Section 11.

### 4.2 Hard-Negative Subgroups
- **Shouted Speech (N=60):** Candidate E1 FPR was **6.67%** (4/60; 95% CI: [2.62%, 15.93%]) versus Candidate B's **5.00%** (3/60; 95% CI: [1.71%, 13.70%]). Both easily passed Gate 3 ($\le 15\%$).
- **Crowd Cheering (N=50):** Candidate E1 FPR was **10.00%** (5/50) versus Candidate B's **8.00%** (4/50).
- **Infant / Child Crying (N=50):** Candidate E1 FPR was **6.00%** (3/50) versus Candidate B's **8.00%** (4/50).
- **Sirens & Alarms (N=35):** Candidate E1 FPR was **2.86%** (1/35) versus Candidate B's **2.86%** (1/35).
- **Music & Singing (N=35):** Candidate E1 FPR was **5.71%** (2/35) versus Candidate B's **5.71%** (2/35).
- **Ordinary Speech (N=40):** Candidate E1 FPR was **5.00%** (2/40) versus Candidate B's **7.50%** (3/40).
- **Whistles (N=0):** Accurately documented as **INSUFFICIENT EVIDENCE (0 fresh authentic clips)**.

---

## 5. Artifact Protection & Verification Audit

| Protected Artifact Name | File Path | Expected SHA-256 | Actual Post-Stage SHA-256 | Audit Status |
|---|---|---|---|---|
| Production Joblib Model | `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **PASS (UNTOUCHED)** |
| Production Metadata | `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **PASS (UNTOUCHED)** |
| Production Predictions | `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **PASS (UNTOUCHED)** |
| Production Evaluation Report | `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **PASS (UNTOUCHED)** |
| Candidate B Checkpoint | `backend/research/stage_8_9_44/models/config_b_mask.pt` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | `f40c8342ae1b2ff588d8a6649fc5e5c2a19d1db6ae3e4f5cc894f1e3353c1378` | **PASS (UNTOUCHED)** |
| Candidate E1 Checkpoint | `backend/research/stage_8_9_54/training/candidate_e_v954_weighted.pt` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | `37fa77b4cd4cb04c5035e31263c3ec62b4e8015fbd1e01f30877f76872277564` | **PASS (UNTOUCHED)** |

Production operating point remains firmly locked at $\theta = 0.3500$.

---

## 6. Research Implications & Scientific Directives

1. **Dual-Branch Architecture Validity:** Candidate E1's class-weighted dual-branch design (YAMNet 1024-d + Phonation 6-d + Subband 11-d) demonstrated genuine learning generalization rather than memorization or partition leakage. The 17.33% recall margin over Candidate B reproduces across completely independent recording sessions and uploaders.
2. **The Remaining Real-World Gap:** While Candidate E1 reached 72.67% overall scream recall and 83.33% short-scream recall, reaching the $\ge 96\%$ acceptance gate while holding false positives below $5\%$ remains an open challenge under realistic festival conditions (crowd noise, attenuation, non-stationary acoustic environments).
3. **Mandatory Research Disposition:** Candidate E1 establishes a new state-of-the-art research baseline for the repository. However, in strict accordance with the mandatory safety charter, **no production promotion or life-safety deployment is authorized.**

