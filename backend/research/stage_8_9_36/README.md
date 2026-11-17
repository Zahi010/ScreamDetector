# STAGE 8.9.36 — DEEP ERROR FORENSICS, BASELINE RECONCILIATION, THRESHOLD AUDIT & DATASET EVIDENCE QUALITY

**Project:** Festival Scream Detector  
**Stage:** 8.9.36  
**Status:** **COMPLETED (AUDIT FINALIZED)**  
**Safety Designation:** **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE**  
**Production Status:** **STRICTLY FROZEN** (Production Threshold: 0.3500)  
**Execution Timestamp:** November 2, 2026  
**Final Scientific Determination:** **AUDIT COMPLETE — DATASET EXPANSION RECOMMENDED**  

---

## 1. Stage Overview & Purpose

Stage 8.9.36 executed an in-depth forensic investigation into Stage 8.9.35 to determine exactly why the research candidates fail the five predefined acceptance gates, reconcile numerical discrepancies between historical stages, audit threshold provenance, and establish the statistical evidence quality of the dataset.

In accordance with strict research governance, **zero new neural network architectures were built in this stage**.

---

## 2. Directory Structure & Deliverables

All artifacts reside strictly under `backend/research/stage_8_9_36/`:

```text
stage_8_9_36/
├── README.md
├── STAGE_PROGRESS.md
├── configs/
│   └── stage_8_9_36_config.json
├── reports/
│   ├── stage_8_9_36_executive_summary.md
│   ├── baseline_reconciliation.md
│   ├── threshold_selection_audit.md
│   ├── false_negative_forensics.md
│   ├── false_positive_forensics.md
│   ├── subband_ablation_audit.md
│   ├── short_scream_evidence_audit.md
│   ├── dataset_integrity_audit.md
│   ├── next_stage_recommendation.md
│   └── production_integrity_report.md
├── evaluation/
│   ├── baseline_prediction_diff.csv
│   ├── baseline_recomputed_metrics.json
│   ├── validation_threshold_sweep.csv
│   ├── threshold_comparison.json
│   ├── false_negative_forensics.csv
│   ├── false_positive_forensics.csv
│   ├── false_positive_category_summary.csv
│   ├── pathway_ablation_results.csv
│   ├── short_scream_source_group_analysis.csv
│   ├── source_group_integrity.csv
│   ├── duplicate_risk_report.csv
│   └── label_consistency_report.csv
├── src/
│   ├── reconcile_baselines.py
│   ├── audit_thresholds.py
│   ├── analyze_false_negatives.py
│   ├── analyze_false_positives.py
│   ├── audit_pathway_ablation.py
│   ├── audit_short_screams.py
│   └── audit_dataset_integrity.py
└── tests/
    ├── test_stage_8_9_36.py (12 automated tests)
    └── test_results.txt (12/12 passed)
```

---

## 3. Key Forensic Takeaways

1. **Baseline Reconciliation (86/102 vs 84/102):**
   - The Stage 8.9.34 Dual-Encoder baseline (84.31% recall, 86/102) and Stage 8.9.35 baseline (82.35% recall, 84/102) share **100% identical model weights, features, and raw probabilities**.
   - The difference was purely due to operating threshold: Stage 8.9.34 evaluated at $\theta = 0.3500$, while Stage 8.9.35 evaluated at the candidate validation threshold $\theta^* = 0.4300$. Exactly two screams fell into $[0.3500, 0.4300)$, while three false alarms were eliminated.
2. **Threshold Provenance ($\theta^* = 0.43$):**
   - Mathematically verified that $\theta^* = 0.43$ was chosen strictly at the global maximum of validation F1 score ($\text{Val } F_1 = 0.7861$) with zero test-set leakage.
3. **False-Negative Forensics (11 Missed Screams):**
   - 45.5% (5/11) were distant screams masked by diffuse noise ($\text{SNR} \le +3\text{ dB}$).
   - 18.2% (2/11) were non-scream vocalizations mislabeled as screams (`gasp-oooh` and `surprised-oooh`).
   - 27.3% (3/11) were low-intensity screams or diluted by silence in multi-second files.
   - 9.1% (1/11) was a borderline probability miss ($P = 0.3543$).
4. **False-Positive Forensics (19 False Alarms):**
   - 73.7% (14/19) were crowd cheering (7 FP) and high-intensity shouting (7 FP).
   - The subband head (Path C), which rewards Band 4 ($2\text{--}3\text{ kHz}$) energy, is triggered by synchronous multi-talker cheering harmonics, boosting false alarms.
5. **Short-Scream Sample Inadequacy:**
   - The test split contains only $N=5$ short screams (<1.0s).
   - Although 5/5 were detected, the 95% Wilson confidence interval spans $[56.55\%, 100.00\%]$. Validating Gate 4 ($\ge 90\%$) is statistically impossible with only 5 samples.
6. **Dataset & Partition Integrity:**
   - 0 duplicate PCM hashes across all 1,328 recordings.
   - 0 source-group leakage across Train (294 groups), Val (98 groups), and Test (111 groups).
   - 152 CC BY-NC recordings (11.4%) are quarantined from commercial production.

---

## 4. Production Immutability Verification

All four frozen production artifact hashes were verified before and after Stage 8.9.36:

| Production Artifact Path | Mandatory Expected SHA-256 Hash | Post-Stage Verified SHA-256 Hash | Status |
| :--- | :--- | :--- | :---: |
| `backend/models/scream_classifier.joblib` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` | **MATCH (VERIFIED)** |
| `backend/models/model_metadata.json` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` | **MATCH (VERIFIED)** |
| `backend/reports/test_predictions.csv` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` | **MATCH (VERIFIED)** |
| `backend/reports/stage5_test_evaluation.md` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` | **MATCH (VERIFIED)** |

---

## 5. Authoritative Scientific Determination

# **AUDIT COMPLETE — DATASET EXPANSION RECOMMENDED**
*(Short-Scream Expansion, Targeted Crowd Cheering Mining & Temporal Window Aggregation)*
