# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.71 — LOW-SNR REPRESENTATION LEARNING, SOURCE-GROUP GENERALIZATION & FALSE-POSITIVE RECOVERY

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Classification:** Research Demonstration Prototype — Non-Certified Prototype  
**Stage Directory:** `backend/research/stage_8_9_71/`

---

## 1. Overview & Objectives

Stage 8.9.71 conducts controlled low-SNR representation learning, distance and reverberation breakdown analysis, cluster-aware source-group generalization auditing, and false-positive recovery.

### Primary Objectives:
1. **Independent Reproduction:** Re-verify Candidate 70-D performance across all statistical dimensions.
2. **False-Positive Forensics:** Analyze all 12 hard-negative false positives individually to identify root acoustic causes.
3. **Cluster-Aware Short-Scream Audit:** Assess source-group clustering in the 268-clip held-out short-scream collection.
4. **Controlled Low-SNR & Attenuation Experiments:** Evaluate noise-floor normalization, ISO 9613-1 distance attenuation, crowd masking, and room reverberation.
5. **Veto Ablations & Candidate 71-D:** Establish Candidate 71-D featuring flux-conditioned resonance rescue, reducing Hard-Negative FPR from 9.68% to 8.06% while preserving recall at 82.83%.
6. **Regression Testing & Verification:** Execute an expanded test suite and measure CPU latency.

---

## 2. Directory Layout

```
backend/research/stage_8_9_71/
├── README.md
├── STAGE_PROGRESS.md
├── experiment_configurations/
├── models/
│   ├── candidate_71_frozen.pt        # Frozen PyTorch checkpoint (SHA-256: e4314990...)
│   └── candidate_71_metadata.json    # Complete hyperparameter & evaluation metadata
├── reports/
│   ├── STAGE_8_9_71_COMPLETION_REPORT.md
│   ├── candidate70_reproduction_audit.md
│   ├── candidate70_false_positive_forensics.csv
│   ├── candidate70_short_scream_generalization_audit.md
│   ├── low_snr_experiment_results.csv
│   ├── distance_attenuation_experiment_results.csv
│   ├── crowd_masking_experiment_results.csv
│   ├── reverberation_experiment_results.csv
│   ├── veto_ablation_results.csv
│   ├── candidate_comparison.csv
│   ├── dataset_manifest_audit.md
│   ├── gate_evaluation.md
│   ├── latency_benchmark.md
│   ├── reproducibility_instructions.md
│   ├── test_results.md
│   ├── artifact_hashes.json
│   └── artifact_hashes.sha256
├── scripts/
│   ├── reproduce_candidate70_and_audit.py
│   ├── run_stage71_experiments.py
│   ├── run_latency_benchmark.py
│   └── verify_artifact_hashes.py
└── tests/
    └── test_stage_8_9_71.py
```

---

## 3. Key Findings & Verdict

- **Flux-Conditioned Resonance Rescue:** Candidate 71-D eliminates 2 hard-negative false alarms introduced in Stage 70, reducing Hard-Negative FPR to 8.06% while preserving Overall Scream Recall at 82.83% and Short-Scream Recall at 94.87%.
- **Heuristic Overfitting Proof:** Suppressing development whistle false alarms via heuristic roughness rules destroys 17–21 genuine held-out short screams, proving that hand-crafted vetoes fail to generalize out-of-distribution.
- **Cluster-Aware Uncertainty:** The 268-clip held-out short cohort clusters within 7 source groups, with a true 95% bootstrap CI spanning [46.67%, 83.14%].
- **Formal Verdict:** **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED** (Gate 1: 82.83% vs. 96.0%; Gate 2: 8.06% vs. 5.0%). Production promotion is strictly unauthorized.

