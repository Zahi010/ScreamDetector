# Stage 8.9.37 — Per-Model Threshold Optimization, Calibration Audit & Dataset Expansion

**Project:** Festival Scream Detector  
**Stage:** 8.9.37  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Status:** Completed  
**Stage Decision:** `THRESHOLD AUDIT COMPLETE — DATASET EXPANSION CONTINUES`

---

## Directory Overview

```text
stage_8_9_37/
├── README.md
├── STAGE_PROGRESS.md
├── config/
│   ├── threshold_audit_config.json
│   └── calibration_config.json
├── scripts/
│   ├── audit_model_predictions.py
│   ├── threshold_sweep.py
│   ├── compare_operating_points.py
│   ├── calibration_audit.py
│   ├── evaluate_frozen_test.py
│   ├── acquire_dataset_manifest.py
│   ├── audit_licenses.py
│   ├── audit_duplicates.py
│   ├── audit_source_groups.py
│   └── adjudicate_label_anomalies.py
├── results/
│   ├── threshold_sweeps/
│   ├── calibration/
│   ├── operating_point_comparisons/
│   └── test_evaluations/
├── plots/
│   ├── val_precision_vs_threshold.png
│   ├── val_recall_vs_threshold.png
│   ├── val_f1_vs_threshold.png
│   ├── val_hn_fpr_vs_threshold.png
│   ├── val_shout_fpr_vs_threshold.png
│   ├── val_precision_recall_curves.png
│   ├── val_roc_curves.png
│   ├── val_confusion_matrices.png
│   ├── val_reliability_diagrams.png
│   └── val_score_distributions_by_category.png
├── manifests/
│   ├── acquired_recordings.csv
│   ├── source_groups.csv
│   ├── license_audit.csv
│   ├── duplicate_audit.csv
│   └── adjudication_queue.csv
├── tests/
│   ├── test_stage_8_9_37.py
│   └── test_results.txt
└── reports/
    ├── STAGE_8_9_37_FINAL_REPORT.md
    ├── THRESHOLD_OPTIMIZATION_REPORT.md
    ├── CALIBRATION_REPORT.md
    ├── DATASET_EXPANSION_REPORT.md
    └── PRODUCTION_INTEGRITY_REPORT.md
```

## Summary of Results
- **Candidates Audited:** Configuration A (YAMNet-Only), Configuration B (Dual-Encoder Phonation), Configuration C (YAMNet + Subband), Configuration D (MP-FS-DualEncoder).
- **Validation Threshold Sweeps:** Swept $\theta \in [0.05, 0.95]$ in $0.01$ increments. Proved that each architecture requires its own operating threshold.
- **Matched Operating Points:** Constraining HN-FPR $\le 5\%$ reduces recall to $<60\%$ across all models. At matched 80% recall, MP-FS-DualEncoder achieves 11.68% HN-FPR compared to 19.16% for YAMNet-Only.
- **Probability Calibration:** Platt scaling reduced ECE by up to 67% (from 0.1217 to 0.0401 on Dual-Encoder). Calibrations preserve ROC-AUC/rankings while standardizing risk interpretation.
- **Frozen Test Evaluation:** MP-FS-DualEncoder at $\theta^* = 0.43$ achieved 89.22% recall (91/102), 9.95% HN-FPR (19/191), 14.58% Shout-FPR (7/48), 100% short-scream recall (5/5), and 19.46 ms P95 latency. However, Gates 1 (Recall $\ge 96\%$) and Gate 2 (HN-FPR $\le 5\%$) remain unpassed.
- **Dataset Expansion:** 85 short screams (42 source groups, 35 reserved for test) and 165 multi-talker hard negatives (54 source groups) cataloged with 0 duplicates, 0 partition leakage, and commercial license quarantine (21 CC-NC isolated).
- **Automated Tests:** 11/11 tests passed.
- **Production Integrity:** All 4 production artifact SHA-256 hashes verified 100% identical. Production threshold locked at 0.3500.
