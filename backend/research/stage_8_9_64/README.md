# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Directory Navigation & Research Map

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Directory Structure

```
backend/research/stage_8_9_64/
├── models/
│   └── stage63_dual_resolution_gated.pt      <- Frozen dual-resolution model checkpoint
├── scripts/
│   ├── verify_artifact_hashes.py             <- Bit-level SHA-256 baseline asset verifier
│   ├── audit_original_gate_definitions.py    <- Authority audit restoring Gate 4 definition
│   ├── reproduce_dual_resolution.py          <- Exact reproduction harness for Stage 63
│   ├── calculate_clustered_confidence_intervals.py <- 2,000 paired cluster bootstrap engine
│   ├── run_short_event_boundary_tests.py     <- 189 synthetic & 133 real boundary test harness
│   ├── audit_short_scream_acquisition.py     <- 401 short-scream curation & annotation harness
│   ├── extract_hnr_features.py               <- FFT-based autocorrelation HNR & spectral analysis
│   ├── build_contrastive_hard_negative_dataset.py <- Forensic FP audit & contrastive mining
│   ├── train_false_positive_suppression_candidates.py <- 6-variant suppression ablations
│   ├── run_temporal_aggregation_ablation.py  <- Rolling-window aggregation (Methods A–F)
│   ├── run_latency_benchmarks.py             <- Multi-stream real-time latency profiler
│   └── run_future_evaluation_power_analysis.py <- Clustered power analysis for N=1,050 cohort
├── tests/
│   └── test_stage_8_9_64.py                  <- 52-test automated verification suite (pytest)
├── Data Artifacts (CSVs & JSONs):
│   ├── artifact_hashes.json                  <- Bit-level baseline SHA-256 hashes
│   ├── dual_resolution_reproduction.csv      <- Model predictions & gating weights (N=312)
│   ├── dual_resolution_clustered_metrics.csv <- Clustered bootstrap confidence intervals
│   ├── source_group_performance.csv          <- Clustered error performance (258 groups)
│   ├── short_event_boundary_metrics.csv      <- 189 boundary configurations & results
│   ├── stage_64_short_scream_manifest.csv    <- 401 verified short screams (< 1.00s)
│   ├── short_scream_annotation_records.csv   <- Double-blind annotation & adjudication data
│   ├── hnr_feature_metrics.csv               <- Category-level HNR and roughness metrics
│   ├── false_positive_forensic_inventory.csv <- Physical forensic audit of 25 false alarms
│   ├── contrastive_hard_negative_metrics.csv <- 117 curated hard negatives (zero leakage)
│   ├── false_positive_suppression_metrics.csv<- 6-variant cross-validation metrics
│   ├── temporal_aggregation_metrics.csv      <- Performance of 7 temporal aggregation methods
│   ├── latency_benchmarks.csv                <- Latency profiles across 1, 2, 4, 8 streams
│   └── future_evaluation_power_metrics.csv   <- Statistical power & DEFF across ICC levels
└── Research Reports (Markdown):
    ├── STAGE_PROGRESS.md                     <- Comprehensive progress & milestone ledger
    ├── repository_inventory.md               <- Repository asset & dependency inventory
    ├── artifact_hash_audit.md                <- Baseline asset bit-level audit report
    ├── original_gate_definition_audit.md     <- Restoration of authoritative Gate 4 definition
    ├── dual_resolution_reproduction.md       <- Reproduction of Stage 63 dual-resolution model
    ├── dual_resolution_clustered_statistics.md <- Source-group clustered bootstrap audit
    ├── short_event_boundary_report.md        <- Boundary sensitivity & temporal alignment report
    ├── short_scream_annotation_protocol.md   <- Annotation rules & adjudication criteria
    ├── short_scream_dataset_acquisition_report.md <- Short-scream expansion dataset report
    ├── annotation_agreement_report.md        <- Double-blind agreement & Cohen's kappa report
    ├── hnr_feature_research.md               <- Acoustic feature formulation & HNR analysis
    ├── false_positive_forensic_report.md     <- Forensic analysis of false positives
    ├── contrastive_hard_negative_report.md   <- Contrastive hard-negative pool governance
    ├── false_positive_suppression_ablation.md<- Suppression architecture ablation report
    ├── temporal_aggregation_report.md        <- Rolling-window temporal aggregation report
    ├── latency_and_engineering_report.md     <- Multi-stream latency certification report
    ├── sample_size_rationale.md              <- Power analysis & sample size rationale
    ├── future_evaluation_preregistration_plan.md <- Preregistration governance & rules
    ├── acceptance_gate_report.md             <- Authoritative five-gate scorecard & veto
    ├── limitations_and_open_issues.md        <- Failure modes & open research questions
    ├── stage_8_9_64_test_report.md           <- Complete 52-test test suite execution report
    └── final_stage_report.md                 <- Capstone research report & final sign-off
```

---

## 2. Key Research Documents Quick-Links

- **Capstone Report:** [`final_stage_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/final_stage_report.md)
- **Gate Scorecard & Promotion Denial:** [`acceptance_gate_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/acceptance_gate_report.md)
- **Verification Test Suite Report:** [`stage_8_9_64_test_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/stage_8_9_64_test_report.md)
- **Gate 4 Authority Restoration:** [`original_gate_definition_audit.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/original_gate_definition_audit.md)
- **Dual-Resolution Reproduction:** [`dual_resolution_reproduction.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/dual_resolution_reproduction.md)
- **Boundary Robustness Report:** [`short_event_boundary_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/short_event_boundary_report.md)
- **Short-Scream Expansion:** [`short_scream_dataset_acquisition_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/short_scream_dataset_acquisition_report.md)
- **False-Positive Suppression:** [`false_positive_suppression_ablation.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/false_positive_suppression_ablation.md)
- **Temporal Aggregation:** [`temporal_aggregation_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/temporal_aggregation_report.md)
- **Engineering & Latency:** [`latency_and_engineering_report.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/latency_and_engineering_report.md)

