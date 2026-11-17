# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.61 — Rolling-Window DSP Research, Temporal Aggregation Validation & Preregistered Independent Evaluation

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Overview and Scope

Stage 8.9.61 investigates continuous rolling-window acoustic analysis and temporal aggregation to resolve the historical sensitivity limitations of static center-window classification. 

The stage is structured into two strictly quarantined operational tracks:
- **Track A (Development & Engineering Validation):** Development on an unexposed cohort ($N=187$, 180 source groups) to design a circular ring buffer, benchmark five temporal aggregation strategies, validate streaming boundary handling across 15 test scenarios, profile multi-stream concurrency (1–8 streams), and freeze the candidate configuration (`E1_ROLLING_C5_STRATEGY_D`).
- **Track B (Preregistered Independent Evaluation):** Preregistering the evaluation protocol, unsealing the evaluation cohort ($N=700$, 453 source groups) constructed in Stage 8.9.60, executing blind evaluation of four frozen candidates, performing inferential statistical testing (2,000 clustered bootstraps, McNemar tests), and auditing the five original project acceptance gates.

---

## 2. Directory Layout

```
backend/research/stage_8_9_61/
├── scripts/                              # Automated Python pipelines & benchmarks
│   ├── verify_artifact_hashes.py         # Cryptographic hash verification of 12 baseline assets
│   ├── reconcile_acquisition_accounting.py # Stage 60 manifest reconciliation
│   ├── audit_creator_independence.py     # Cross-partition creator independence audit
│   ├── build_development_manifest.py     # Track A development cohort builder (N=187)
│   ├── verify_sealed_manifest.py         # Track B sealed manifest digest verifier (N=700)
│   ├── extract_dev_rolling_features.py   # Rolling C5 feature extraction on dev cohort
│   ├── compare_temporal_aggregation.py   # Benchmark of 5 temporal aggregation strategies
│   ├── validate_streaming_correctness.py # 15-scenario streaming buffer validation suite
│   ├── run_latency_benchmarks.py         # Multi-stream latency and concurrency profiling
│   ├── freeze_rolling_window_candidate.py# Frozen candidate parameter seal
│   ├── extract_sealed_cohort_features.py # Feature extraction on sealed evaluation cohort
│   ├── run_preregistered_evaluation.py   # Blind inference of 4 frozen candidate models
│   └── analyze_independent_results.py    # Clustered bootstrap, McNemar, and subgroup analysis
├── tests/                                # Automated pytest test suite
│   └── test_stage_8_9_61.py              # 35 comprehensive automated invariant tests
├── rolling_window_experiments/           # Intermediate extracted features and reference DSP
│   ├── c5_combined_reference.py          # Reference copy of C5 combined filterbank
│   ├── dev_rolling_features.npz          # Extracted rolling features for dev cohort (N=187)
│   └── sealed_cohort_features.npz        # Extracted features for sealed cohort (N=700)
├── *.csv / *.json                        # Verified data tables, predictions, and metrics
└── *.md                                  # Comprehensive research documentation reports
```

---

## 3. Key Findings Summary

1. **Rolling EMA Substantially Improves Sustained Sensitivity:**
   Transitioning from static center-window extraction to a 500 ms rolling window with Exponential Moving Average ($\alpha=0.50, \theta=0.6000$) boosted sustained scream recall on the sealed cohort from **69.47% to 86.26%**, and overall scream recall from **58.00% to 70.00%** (paired McNemar $p < 10^{-6}$).
2. **Multiple-Testing Penalty Inflates False Alarms:**
   Evaluating 4.2 windows per recording increased the hard-negative false positive rate from **19.20% to 35.40%**, demonstrating that single-frame classifiers require high-level temporal sequence models to avoid false alarms in continuous streams.
3. **Candidate B Baseline Parity:**
   On static evaluation, Candidate E1 (58.00% recall, 19.20% FPR) and Candidate B (57.50% recall, 15.80% FPR) are statistically indistinguishable ($p = 0.0935$).
4. **Intervention D Effectiveness:**
   Candidate B + Intervention D achieved the lowest overall FPR (**14.80%**) and suppressed referee whistle false alarms to **1.67%** (compared to 25.00% for Candidate E1 Rolling).
5. **Acceptance Gate Verdict:**
   **No candidate passes all five project acceptance gates.** Zero production promotion is authorized. The system remains strictly an experimental research prototype.

---

## 4. Reproduction Instructions

To reproduce the complete test suite and audit verifications:

```powershell
# Run the 35 automated invariant tests
python -m pytest festival-scream-detector/backend/research/stage_8_9_61/tests/test_stage_8_9_61.py -v

# Verify baseline cryptographic hashes
python festival-scream-detector/backend/research/stage_8_9_61/scripts/verify_artifact_hashes.py
```

