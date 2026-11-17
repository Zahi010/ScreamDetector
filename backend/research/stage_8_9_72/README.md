# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.72 — ACOUSTIC REPRESENTATION GENERALIZATION, HARD-NEGATIVE DISCRIMINATION & PROSPECTIVE EVALUATION PREPARATION

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Classification:** Research Demonstration Prototype — Non-Certified Prototype  
**Stage Directory:** `backend/research/stage_8_9_72/`

---

## 1. Overview & Objectives

Stage 8.9.72 investigates representation learning alternatives to determine whether difficult screams can be recognized and hard negatives rejected without an expanding set of manually tuned heuristic vetoes.

### Primary Objectives:
1. **Candidate 71-D Reproduction:** Independently reproduce Candidate 71-D metrics (82.83% recall, 8.06% HN FPR, 14.77% shout FPR, 94.87% short recall, 0.417 ms latency).
2. **False-Negative Forensics:** Analyze all 17 missed screams individually across acoustic features, background noise, and veto interactions.
3. **False-Positive Forensics:** Analyze all 10 hard-negative false alarms individually across acoustic categories (infant crying, whistles, sirens).
4. **Rescue Mechanism Ablations:** Evaluate flux-conditioned resonance rescue ($flux > 0.040$) across 6 paired configurations.
5. **Representation Learning Experiments:** Investigate low-SNR representations, cross-branch fusion, contrastive learning (SupCon), and hard-negative multi-task discrimination.
6. **Dataset Governance & Quarantine:** Audit exposure status for Stage 54 validation (`EXPOSED_DEVELOPMENT_COHORT`) and Stage 64 short screams (`EXPOSED_DIAGNOSTIC_COHORT`), while maintaining strict quarantine on Stage 60 sealed cohort ($N=700$, SHA-256 `9dfa4ced...`).
7. **Regression Testing & Latency Benchmarks:** Execute 15-test automated regression suite and profile single/multi-stream CPU latency.

---

## 2. Directory Layout

```
backend/research/stage_8_9_72/
├── README.md
├── STAGE_PROGRESS.md
├── experiment_configurations/
├── models/
│   ├── candidate_71_frozen.pt        # Frozen PyTorch checkpoint (SHA-256: e4314990...)
│   └── candidate_72_metadata.json    # Complete hyperparameter & evaluation metadata
├── reports/
│   ├── STAGE_8_9_72_COMPLETION_REPORT.md
│   ├── candidate71_reproduction_audit.md
│   ├── candidate71_false_negative_forensics.csv
│   ├── candidate71_false_positive_forensics.csv
│   ├── rescue_mechanism_ablation.csv
│   ├── representation_learning_experiments.csv
│   ├── low_snr_experiment_results.csv
│   ├── contrastive_learning_results.csv
│   ├── hard_negative_discrimination_results.csv
│   ├── dataset_manifest_audit.md
│   ├── candidate_comparison.csv
│   ├── gate_evaluation.md
│   ├── latency_benchmark.md
│   ├── test_results.md
│   ├── artifact_hashes.json
│   ├── artifact_hashes.sha256
│   └── reproducibility_instructions.md
├── scripts/
│   ├── run_stage72_experiments.py
│   ├── run_latency_benchmark.py
│   └── verify_artifact_hashes.py
└── tests/
    └── test_stage_8_9_72.py
```

---

## 3. Five-Gate Summary

| Gate ID | Target Requirement | Candidate 71-D Point Estimate | 95% Cluster-Aware Bootstrap CI | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 82.83% (82/99) | [74.00%, 91.25%] | **FAIL** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 8.06% (10/124) | [2.83%, 14.29%] | **FAIL** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 14.77% (13/88) | [2.13%, 32.50%] | **PASS** |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 94.87% (37/39) | [86.21%, 100.00%] | **PASS** |
| **Gate 5** | Model CPU P95 Latency $\le 25.0$ ms | 0.417 ms | [0.380 ms, 0.450 ms] | **PASS** |

**Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**  
**Production Promotion:** **STRICTLY PROHIBITED**

