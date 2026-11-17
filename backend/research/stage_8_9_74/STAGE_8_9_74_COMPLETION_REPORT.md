# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.74 COMPLETION REPORT: Provenance Reconciliation, Annotation Reliability & Targeted Boundary Validation

**Stage Identifier:** Stage 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Date:** 2026-11-14  
**Project Directory:** [`festival-scream-detector/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector)  
**Stage Directory:** [`backend/research/stage_8_9_74/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74)  
**Active Research Champion:** **Candidate 71-D** (Frozen Checkpoint SHA-256: `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b`)  
**Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**  
**Final Stage Research Decision:** **`RESEARCH CONTINUES — DATASET/ANNOTATION LIMITATIONS`**  
**Live Dashboard Verdict:** **`RECORDED AUDIO VERIFIED; MICROPHONE UNVERIFIED`**  
**Production Promotion Status:** **NOT AUTHORIZED — STRICTLY EXPERIMENTAL RESEARCH PROTOTYPE**

---

## 0. Mandatory Safety & Operational Boundaries

> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This acoustic research prototype is non-certified software intended solely for scientific evaluation and controlled laboratory demonstrations.  
> - **Strict Prohibitions:** No deployment for emergency dispatch, autonomous alerts, police notification, active-shooter systems, perimeter defense, or critical life-safety operations.  
> - **Input Media:** Only legally obtained recorded audio datasets and controlled playback environments are authorized.  
> - **Advisory Only:** Acoustic model predictions represent statistical pattern matching and do not establish danger, violence, distress, or emergency events.  
> - **No Production Promotion:** Research candidates are ineligible for production deployment.

---

## 1. Executive Summary & Mission Objectives

Stage 8.9.74 was commissioned to conduct an exhaustive scientific audit into dataset provenance, annotation consistency, and acoustic boundary cases before authorizing further architectural modeling.

The major outcomes of this stage are:
1. **Critical Provenance Resolution (Stage 60 Cohort):**
   - Conducted a strictly read-only historical investigation into the Stage 60 cohort (`future_evaluation_manifest.json`, $N=700$).
   - Resolved the historical contradiction: Stage 61 Track B formally unsealed and evaluated all 700 recordings across 4 candidates, generating 2,800 predictions (`sealed_cohort_predictions.csv`).
   - The later claim in Stages 67–73 that this cohort was "sealed and untouched" was false, caused by conflating an unaltered JSON manifest hash (`9dfa4ced...`) with an absence of historical access.
   - Binding Verdict: **`CONFIRMED_PREVIOUSLY_ACCESSED`**. The cohort is permanently reclassified as `HISTORICALLY_EXPOSED_COHORT`.
2. **Exact Reproduction of Candidate 71-D & Stage 73 Results:**
   - All classification metrics (82.83% overall recall, 88.75% real scream recall, 57.89% synthetic scream recall, 8.06% hard-negative FPR, 14.77% shouted-speech FPR, 94.87% short-scream recall) were reproduced bit-for-bit from binary checkpoints and arrays.
   - Reconciled host CPU latency timing jitter (0.370 ms vs 0.417 ms) and source-group partition accounting (47 Pos, 69 HN, 28 Shout, 138 total unique).
3. **Statistical Confidence Interval Methodology:**
   - Formal audit demonstrated that source-group cluster bootstrap yields substantially wider, scientifically honest confidence intervals than naive i.i.d. bootstrap (e.g. Gate 3 Shouted FPR CI is [2.33%, 31.15%] vs [7.78%, 22.89%]).
4. **Annotation Reliability & Taxonomy Audit:**
   - Audited all 40 classification errors from Candidate 71-D: **62.5%** represent genuine acoustic classification errors, while **37.5%** represent ground-truth annotation uncertainty (surprise vocal gasps labeled as screams; 8 theatrical acting shouts from uploader `reitanna` labeled as non-scream speech).
   - Formally documented that inter-rater reliability ($\kappa$) cannot be calculated for the validation cache because individual annotator votes were not preserved.
5. **Targeted Child-Scream & Distress-Veto Forensics:**
   - Traced the two child screams (`273153__hoerspielwerkstatt-hef__child-scream2`, raw probs 0.574 and 0.572) and confirmed that adult-calibrated distress veto ($roughness < 0.022$) collaterally suppresses them.
   - Traced the two added shouted-speech false alarms (`fsd50k_220823` and `fsd50k_220822` from uploader `ericsueiro`) induced when relaxing the veto. Ruled that hand-tuning rules for 2 positive clips on development data constitutes overfitting.
6. **Real vs. Synthetic Reliability:**
   - Quantified the steep SNR masking gradient (+12 dB: 100%, 0 dB: 60%, -6 dB: 20%). Confirmed 0% leakage into the training partition.
7. **Architecture Decision:**
   - Ruled that 4 of the 6 prerequisite conditions for architectural experimentation are unmet. Formally halted new model training in Stage 74, preserving **Candidate 71-D as the active frozen champion**.

---

## 2. Five-Gate Mandatory Acceptance Scorecard

Evaluated against the exposed Stage 54 Validation Cohort ($N=311$, 138 Source Groups, `EXPOSED_DEVELOPMENT_COHORT`) with 95% cluster-aware bootstrap confidence intervals ($B=2,000$ resamples across 138 source groups):

| Gate ID | Target Requirement | Metric Name | Numerator / Denominator | Point Estimate | 95% Cluster-Aware Bootstrap CI | Source Groups ($N_{sg}$) | Cohort Exposure Status | Gate Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Gate 1** | $\ge 96.0\%$ | Overall Scream Recall | 82 / 99 | **82.83%** | [74.07%, 91.77%] | 47 SGs | `EXPOSED_DEVELOPMENT_COHORT` | **FAIL — POINT ESTIMATE** |
| **Gate 2** | $\le 5.0\%$ | Hard-Negative FPR | 10 / 124 | **8.06%** | [2.94%, 14.16%] | 69 SGs | `EXPOSED_DEVELOPMENT_COHORT` | **FAIL — POINT ESTIMATE** |
| **Gate 3** | $\le 15.0\%$ | Shouted-Speech FPR | 13 / 88 | **14.77%** | [2.33%, 31.15%] | 28 SGs | `EXPOSED_DEVELOPMENT_COHORT` | **PASS — POINT ESTIMATE** (CI crosses ceiling) |
| **Gate 4** | $\ge 90.0\%$ | Short-Scream Recall (< 1.0s) | 37 / 39 | **94.87%** | [86.84%, 100.00%] | 24 SGs | `EXPOSED_DEVELOPMENT_COHORT` | **PASS — POINT ESTIMATE** (CI crosses floor) |
| **Gate 5** | $\le 25.0$ ms | Model CPU P95 Latency | 0.392 ms / 25.0 ms | **0.392 ms** | [0.350 ms, 0.450 ms] | N/A (Local CPU) | Benchmarked Synthetic Batch | **PASS — POINT ESTIMATE** ($> 63\times$ Headroom) |

---

## 3. Cryptographic Baseline Verification

All protected baseline assets and historical checkpoints were verified bit-for-bit identical before and after Stage 8.9.74:

| Artifact Identifier | Expected SHA-256 | Observed SHA-256 | Integrity Status |
| :--- | :--- | :--- | :--- |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH** |
| `backend/research/stage_8_9_60/future_evaluation_manifest.json` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | `9dfa4ced3620e568a6c4b247eabab76a94fff655c367b918f97d5d875b4e32cd` | **MATCH (PROVENANCE RECONCILED)** |
| `backend/research/stage_8_9_74/models/candidate_71_frozen.pt` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | `e4314990f1314402f885878818651a0efb8aa5c75eaf51487f684356b0835d6b` | **MATCH (FROZEN CHAMPION)** |

---

## 4. Key Deliverables & Primary Artifact Directory

All 23 required technical deliverables for Stage 8.9.74 are stored directly inside [`backend/research/stage_8_9_74/`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74):

1. [STAGE_8_9_74_COMPLETION_REPORT.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/STAGE_8_9_74_COMPLETION_REPORT.md)
2. [STAGE_PROGRESS.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/STAGE_PROGRESS.md)
3. [stage60_provenance_audit.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/stage60_provenance_audit.md)
4. [candidate_reproduction_audit.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/candidate_reproduction_audit.md)
5. [candidate_metric_reconciliation.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/candidate_metric_reconciliation.csv)
6. [confidence_interval_method_audit.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/confidence_interval_method_audit.md)
7. [annotation_taxonomy_audit.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/annotation_taxonomy_audit.md)
8. [vocalization_label_review.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/vocalization_label_review.csv)
9. [annotation_ambiguity_summary.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/annotation_ambiguity_summary.csv)
10. [label_definition_proposal.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/label_definition_proposal.md)
11. [child_scream_veto_forensics.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/child_scream_veto_forensics.md)
12. [distress_veto_case_comparison.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/distress_veto_case_comparison.csv)
13. [targeted_veto_ablation_results.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/targeted_veto_ablation_results.csv)
14. [real_vs_synthetic_reliability.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/real_vs_synthetic_reliability.md)
15. [snr_stratified_results.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/snr_stratified_results.csv)
16. [synthetic_source_leakage_audit.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/synthetic_source_leakage_audit.md)
17. [architecture_research_decision.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/architecture_research_decision.md)
18. [gate_evaluation.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/gate_evaluation.md)
19. [latency_benchmark.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/latency_benchmark.md)
20. [test_results.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/test_results.md)
21. [artifact_hashes.json](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/artifact_hashes.json)
22. [reproducibility_instructions.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/reproducibility_instructions.md)
23. [README.md](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/README.md)

---

## 5. Final Research Decision & Future Roadmap

In compliance with section 18 of the stage specification, the governing research decision is:

**`RESEARCH CONTINUES — DATASET/ANNOTATION LIMITATIONS`**

### Scientific Rationale:
1. **Model Architecture is Not the Primary Bottleneck:** Candidate 71-D reproduces reliably and achieves 88.75% recall on genuine human screams with 0.392 ms inference latency.
2. **Current Partitions Are Exhausted:** The Stage 54 validation set has been exposed through dozens of tuning iterations. The Stage 60 cohort was previously evaluated in Stage 61. There is no valid prospective test set left in the project archives.
3. **Labels Contain Ambiguity:** 37.5% of errors represent forced binary ambiguity (theatrical voice acting and vocal gasps). Training new models on noisy labels will only fit annotation artifacts.
4. **Mandatory Next Phase:** The project must focus on independent data acquisition under the proposed 11-class multi-reviewer taxonomy, sourcing authentic child distress vocalizations and real festival background noise, before any new model candidate can be qualified.

