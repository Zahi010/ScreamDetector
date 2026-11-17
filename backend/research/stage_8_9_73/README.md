# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.73 — VOCALIZATION DISCRIMINATION, ACOUSTIC BOUNDARY LEARNING & RESIDUAL ERROR RECOVERY

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Classification:** Research Demonstration Prototype — Non-Certified Prototype  
**Stage Directory:** `backend/research/stage_8_9_73/`

---

## 1. Overview & Objectives

Stage 8.9.73 investigates whether a hierarchical vocalization-discrimination architecture can distinguish scream-like vocalizations from acoustically similar non-scream sounds, resolve residual errors, and eliminate hand-crafted acoustic vetoes.

### Primary Objectives:
1. **Candidate 71-D Independent Reproduction:** Independently reproduce Candidate 71-D metrics (82.83% overall recall, 8.06% HN FPR, 14.77% shout FPR, 94.87% short recall, 0.370–0.417 ms latency).
2. **Disentanglement Analysis:** Disentangle positive scream recall between genuine recorded human screams ($N=80$, recall = 88.75%) and synthetic crowd-masked screams ($N=19$, recall = 57.89%).
3. **Forensic Analysis of Residual Errors:** Detailed clip-by-clip forensic analysis of all 17 false negatives and 10 hard-negative false positives.
4. **Vocalization Discrimination:** Analyze acoustic differences between screams, infant crying, and high-effort shouted speech.
5. **Hierarchical Architecture Design:** Formulate and evaluate a 3-stage hierarchical architecture (Non-vocal vs Vocal non-scream vs Scream) with and without acoustic vetoes.
6. **Residual Veto Ablation & Child Scream Recovery:** Audit the collateral suppression of child screams by the distress veto, testing trade-offs between scream recall and shouted-speech rejection.
7. **Dataset Governance & Quarantine:** Maintain cryptographic quarantine on Stage 60 sealed prospective cohort ($N=700$, SHA-256 `9dfa4ced...`) and document exposure statuses.
8. **Regression Testing & Latency Benchmarks:** Execute 16-test automated regression suite and benchmark single/multi-stream CPU latency.

---

## 2. Directory Layout

```
backend/research/stage_8_9_73/
├── README.md
├── STAGE_PROGRESS.md
├── experiment_configurations/
├── models/
│   ├── candidate_71_frozen.pt        # Frozen PyTorch checkpoint (SHA-256: e4314990...)
│   └── candidate_73_metadata.json    # Complete hyperparameter & evaluation metadata
├── reports/
│   ├── STAGE_8_9_73_COMPLETION_REPORT.md
│   ├── candidate71_reproduction_audit.md
│   ├── candidate71_false_negative_forensics.csv
│   ├── candidate71_false_positive_forensics.csv
│   ├── hierarchical_architecture_design.md
│   ├── vocalization_discrimination_results.csv
│   ├── infant_cry_vs_scream_results.csv
│   ├── shouted_speech_vs_scream_results.csv
│   ├── whistle_siren_discrimination_results.csv
│   ├── residual_veto_ablation_results.csv
│   ├── synthetic_vs_real_evaluation.md
│   ├── dataset_manifest_audit.md
│   ├── candidate_comparison.csv
│   ├── gate_evaluation.md
│   ├── latency_benchmark.md
│   ├── test_results.md
│   ├── artifact_hashes.json
│   ├── artifact_hashes.sha256
│   └── reproducibility_instructions.md
├── scripts/
│   ├── run_stage73_experiments.py
│   ├── run_latency_benchmark.py
│   └── verify_artifact_hashes.py
└── tests/
    └── test_stage_8_9_73.py
```

---

## 3. Five-Gate Summary

| Gate ID | Target Requirement | Candidate 71-D Point Estimate | 95% Cluster-Aware Bootstrap CI | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Overall Scream Recall $\ge 96.0\%$ | 82.83% (82/99) | [74.00%, 91.25%] | **FAIL** |
| **Gate 2** | Hard-Negative FPR $\le 5.0\%$ | 8.06% (10/124) | [2.83%, 14.29%] | **FAIL** |
| **Gate 3** | Shouted-Speech FPR $\le 15.0\%$ | 14.77% (13/88) | [2.13%, 32.50%] | **PASS** |
| **Gate 4** | Short-Scream Recall $\ge 90.0\%$ | 94.87% (37/39) | [86.21%, 100.00%] | **PASS** |
| **Gate 5** | Model CPU P95 Latency $\le 25.0$ ms | 0.370 ms | [0.350 ms, 0.450 ms] | **PASS** |

**Research Model Verdict:** **`PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED`**  
**Production Promotion:** **STRICTLY PROHIBITED**

