# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.70 — GENERALIZATION AUDIT, VETO SIMPLIFICATION & LOW-SNR SCREAM RECOVERY

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Classification:** Research Demonstration Prototype — Non-Certified Prototype  
**Stage Directory:** `backend/research/stage_8_9_70/`

---

## 1. Overview & Objectives

Stage 8.9.70 executes a comprehensive generalization audit and simplification of the dual-resolution scream detector research architecture.

### Primary Objectives:
1. **Independent Metric Reproduction:** Re-verify Candidate 69-D performance metrics from frozen checkpoints.
2. **Multi-Label False-Negative Forensic Re-Audit:** Investigate co-occurring acoustic failure modes (reverberation smearing, raw neural underconfidence, low-SNR masking, veto over-suppression) across historical misses.
3. **268 Short-Scream Provenance & Gap Analysis:** Trace lineage of the held-out short-scream cohort across 7 source groups and isolate why recall differs from the development cohort.
4. **Veto Simplification Ablations:** Perform systematic ablations to identify and eliminate redundant heuristic suppression rules.
5. **Low-SNR & Reverberation Interventions:** Test acoustic de-smearing and resonance recovery methods to establish Candidate 70-D.
6. **Latency Profiling & Verification:** Benchmark CPU inference latency and streaming pipeline performance against the 250 ms hop deadline.

---

## 2. Directory Layout

```
backend/research/stage_8_9_70/
├── README.md
├── experiment_configurations/
├── models/
│   ├── candidate_70_frozen.pt        # Frozen PyTorch checkpoint (SHA-256: 40a162d1...)
│   └── candidate_70_metadata.json    # Complete hyperparameter & evaluation metadata
├── reports/
│   ├── STAGE_8_9_70_COMPLETION_REPORT.md
│   ├── candidate69_reproduction_audit.md
│   ├── candidate69_false_negative_reaudit.csv
│   ├── short_scream_268_provenance_audit.md
│   ├── short_scream_268_subgroup_results.csv
│   ├── veto_ablation_results.csv
│   ├── low_snr_experiment_results.csv
│   ├── reverberation_experiment_results.csv
│   ├── candidate_comparison.csv
│   ├── dataset_manifest_audit.md
│   ├── gate_evaluation.md
│   ├── latency_benchmark.md
│   ├── reproducibility_instructions.md
│   ├── test_results.md
│   ├── artifact_hashes.json
│   └── artifact_hashes.sha256
├── scripts/
│   ├── generate_fn_reaudit.py
│   ├── audit_268_recordings.py
│   ├── ablation_study.py
│   ├── run_experiments.py
│   ├── run_latency_benchmark.py
│   └── verify_artifact_hashes.py
└── tests/
    └── test_stage_8_9_70.py
```

---

## 3. Key Findings & Verdict

- **100% Redundancy of HFCR Veto:** Ablation C proved that the HFCR roll-off veto produces identical predictions when removed, allowing the suppression architecture to be simplified from 4 heuristics to 3 without any loss in shouted-speech rejection.
- **Root Cause of Short-Scream Gap:** 83.9% of misses on the 268-clip held-out cohort fail at the raw neural level ($p_{\text{raw}} < 0.4920$) due to low SNR (mean 2.4 dB in `sg_short_supp`), refuting the hypothesis that heuristic vetoes are the primary bottleneck.
- **Candidate 70-D Performance:** Recovers 82/99 validation screams (82.83% recall, +3 screams over 69-D and +9 over 67-D), holds shouted-speech FPR at 14.77% ($\le 15.0\%$, Gate 3 PASS), improves short-scream recall to 94.87% (Gate 4 PASS), and maintains 0.384 ms CPU latency (Gate 5 PASS).
- **Formal Verdict:** **PARTIAL IMPROVEMENT — ONE OR MORE GATES FAILED** (Gate 1 Recall: 82.83% vs. 96.0%; Gate 2 Hard-Negative FPR: 9.68% vs. 5.0%). Production promotion is strictly unauthorized.

