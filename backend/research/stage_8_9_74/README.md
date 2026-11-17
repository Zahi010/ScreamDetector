# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.74 — PROVENANCE RECONCILIATION, ANNOTATION RELIABILITY & TARGETED BOUNDARY VALIDATION

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Classification:** Research Demonstration Prototype — Non-Certified Prototype  
**Stage Directory:** `backend/research/stage_8_9_74/`

---

## 1. Overview & Objectives

Stage 8.9.74 executes a rigorous provenance reconciliation, annotation reliability audit, and targeted boundary validation to determine whether previous experimental findings are reproducible, whether historical dataset provenance is trustworthy, and whether residual errors represent model limitations, acoustic ambiguity, annotation uncertainty, or evaluation defects.

### Primary Objectives:
1. **Stage 60 Provenance Reconciliation:** Resolve the historical contradiction between Stage 61 evaluations and subsequent Stage 67–73 claims regarding the Stage 60 cohort ($N=700$). Binding verdict: **`CONFIRMED_PREVIOUSLY_ACCESSED`**.
2. **Candidate 71-D Reproduction:** Independently recalculate all classification and latency metrics from binary checkpoints and cache arrays. Reconciled 100% exact.
3. **Statistical Confidence Methodology:** Formal audit comparing Naive i.i.d. Bootstrap vs. Source-Group Cluster Bootstrap ($B=2,000$ resamples).
4. **Annotation Reliability & Taxonomy Audit:** Audit all 40 classification discrepancies (17 FN, 10 HN FP, 13 Shout FP), establishing that 62.5% are acoustic classification errors while 37.5% represent annotation uncertainty.
5. **Targeted Child Scream Investigation:** End-to-end signal trace of child scream suppression (`273153__hoerspielwerkstatt-hef__child-scream2`) and the resulting shouted-speech false alarm trade-off under Candidate 73-C.
6. **Real vs. Synthetic Reliability:** Document the severe SNR masking gradient (+12 dB: 100%, -6 dB: 20%) and confirm zero leakage into the training partition.
7. **Architecture Decision:** Formal ruling that new architecture training is ungrounded without an unexposed test set. Preserve Candidate 71-D as active frozen champion.

---

## 2. Directory Layout

```
backend/research/stage_8_9_74/
├── README.md
├── STAGE_PROGRESS.md
├── STAGE_8_9_74_COMPLETION_REPORT.md
├── stage60_provenance_audit.md
├── candidate_reproduction_audit.md
├── candidate_metric_reconciliation.csv
├── confidence_interval_method_audit.md
├── annotation_taxonomy_audit.md
├── vocalization_label_review.csv
├── annotation_ambiguity_summary.csv
├── label_definition_proposal.md
├── child_scream_veto_forensics.md
├── distress_veto_case_comparison.csv
├── targeted_veto_ablation_results.csv
├── real_vs_synthetic_reliability.md
├── snr_stratified_results.csv
├── synthetic_source_leakage_audit.md
├── architecture_research_decision.md
├── gate_evaluation.md
├── latency_benchmark.md
├── test_results.md
├── artifact_hashes.json
├── artifact_hashes.sha256
├── reproducibility_instructions.md
├── models/
│   └── candidate_71_frozen.pt        # Frozen PyTorch checkpoint (SHA-256: e4314990...)
├── scripts/
│   ├── run_stage74_reconciliation.py
│   ├── run_latency_benchmark.py
│   └── verify_artifact_hashes.py
└── tests/
    └── test_stage_8_9_74.py
```

---

## 3. Five-Gate Summary

| Gate ID | Target Requirement | Candidate 71-D Point Estimate | 95% Cluster-Aware Bootstrap CI | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 82.83% (82/99) | [74.07%, 91.77%] | **FAIL — POINT ESTIMATE** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 8.06% (10/124) | [2.94%, 14.16%] | **FAIL — POINT ESTIMATE** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 14.77% (13/88) | [2.33%, 31.15%] | **PASS — POINT ESTIMATE** (CI crosses ceiling) |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 94.87% (37/39) | [86.84%, 100.00%] | **PASS — POINT ESTIMATE** (CI crosses floor) |
| **Gate 5** | Model CPU P95 Latency $\le 25.0$ ms | 0.370 ms - 0.392 ms | [0.350 ms, 0.450 ms] | **PASS — POINT ESTIMATE** ($> 63\times$ Headroom) |

**Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**  
**Final Stage Research Decision:** **`RESEARCH CONTINUES — DATASET/ANNOTATION LIMITATIONS`**  
**Production Promotion:** **STRICTLY PROHIBITED**

