# STAGE 8.9.36 PROGRESS TRACKER — ERROR FORENSICS, BASELINE RECONCILIATION & DATASET EVIDENCE AUDIT

**Project:** Festival Scream Detector  
**Stage:** 8.9.36 — Deep Error Forensics, Baseline Reconciliation, Threshold Audit & Dataset Evidence Quality  
**Operating Mode:** Strictly Isolated Offline Research & Forensic Investigation  
**Production Status:** STRICTLY FROZEN (Decision Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Initial Pre-Stage Hash Audit:** 100% VERIFIED PASS (2026-11-02T22:15:31+05:30)  
**Final Post-Stage Hash Audit:** 100% VERIFIED PASS (2026-11-02T22:28:51+05:30)  
**Final Determination:** **AUDIT COMPLETE — DATASET EXPANSION RECOMMENDED**  
**Last Updated:** November 2, 2026  

---

## 1. CHECKPOINT LEDGER

| Checkpoint | Description | Status | Deliverables / Artifacts |
|---|---|---|---|
| **Pre-Stage** | Production Hash Immutability Verification | **COMPLETED** | Verified all 4 production SHA-256 hashes intact |
| **Phase 0** | Repository & Artifact Discovery | **COMPLETED** | Inspected Stage 8.9.33, 8.9.34, 8.9.35 files; created directory structure |
| **Phase 1** | Baseline Reconciliation (84/102 vs 86/102) | **COMPLETED** | `src/reconcile_baselines.py`, `reports/baseline_reconciliation.md`, `evaluation/baseline_prediction_diff.csv`, `evaluation/baseline_recomputed_metrics.json` |
| **Phase 2** | Threshold and Operating-Point Audit (0.35 vs 0.43) | **COMPLETED** | `src/audit_thresholds.py`, `reports/threshold_selection_audit.md`, `evaluation/validation_threshold_sweep.csv`, `evaluation/threshold_comparison.json` |
| **Phase 3** | False-Negative Forensics (11 Missed Screams) | **COMPLETED** | `src/analyze_false_negatives.py`, `reports/false_negative_forensics.md`, `evaluation/false_negative_forensics.csv` |
| **Phase 4** | False-Positive Forensics (19 False Alarms) | **COMPLETED** | `src/analyze_false_positives.py`, `reports/false_positive_forensics.md`, `evaluation/false_positive_forensics.csv`, `evaluation/false_positive_category_summary.csv` |
| **Phase 5** | Subband Contribution & Pathway Ablation Audit | **COMPLETED** | `src/audit_pathway_ablation.py`, `reports/subband_ablation_audit.md`, `evaluation/pathway_ablation_results.csv` |
| **Phase 6** | Short-Scream Evidence Audit (<1.0s Duration) | **COMPLETED** | `src/audit_short_screams.py`, `reports/short_scream_evidence_audit.md`, `evaluation/short_scream_source_group_analysis.csv` |
| **Phase 7** | Dataset & Source-Group Quality Audit (1,328 Corpus) | **COMPLETED** | `src/audit_dataset_integrity.py`, `reports/dataset_integrity_audit.md`, `evaluation/source_group_integrity.csv`, `evaluation/duplicate_risk_report.csv`, `evaluation/label_consistency_report.csv` |
| **Phase 8** | Evidence-Based Next-Step Decision & Research Roadmap | **COMPLETED** | `reports/next_stage_recommendation.md`, `reports/stage_8_9_36_executive_summary.md` |
| **Phase 9** | Automated Testing & Post-Stage Production Integrity | **COMPLETED** | `tests/test_stage_8_9_36.py` (12/12 passed), `tests/test_results.txt`, `reports/production_integrity_report.md` |

---

## 2. DISCOVERED HISTORICAL ARTIFACTS
- Stage 8.9.33 Predictions: `backend/research/stage_8_9_33/predictions/test_predictions_stage8_9_33.csv` ($N=293$)
- Stage 8.9.34 Predictions: `backend/research/stage_8_9_34/predictions/test_predictions_stage8_9_34.csv` ($N=293$)
- Stage 8.9.35 Predictions: `backend/research/stage_8_9_35/predictions/test_predictions_stage8_9_35.csv` ($N=293$)
- Dataset Manifest: `backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv` ($N=1,328$)
- Feature NPZ: `backend/experiments/v2_hard_negative_training/features/yamnet_features_v3.npz`
- Subband Features: `backend/research/stage_8_9_35/frequency_analysis/subband_feature_analysis.csv`
- Multi-Pathway Model: `backend/research/stage_8_9_35/models/mp_fs_dual_encoder_model.pt`
- Dual-Encoder Baseline Model: `backend/research/stage_8_9_33/models/best_dual_encoder.pt`

---

## 3. KEY FORENSIC FINDINGS SUMMARY
1. **Baseline Reconciled:** Difference between 84.31% (Stage 8.9.34) and 82.35% (Stage 8.9.35) baseline recall is 100% attributable to operating threshold ($\theta=0.35$ vs. $\theta=0.43$). Underlying probabilities and models are identical to 6 decimal places.
2. **Threshold Provenance Verified:** $\theta^* = 0.43$ was derived strictly from the validation partition by maximizing validation F1 (0.7861). Zero test labels were used.
3. **11 Missed Screams Forensic Drivers:**
   - 45.5% (5/11): Severe noise masking ($\text{SNR} \le +3\text{ dB}$, down to $-6\text{ dB}$).
   - 18.2% (2/11): Ground-truth labeling defect (`gasp-oooh` and `surprised-oooh` are non-screams).
   - 18.2% (2/11): Low-intensity muffled vocalizations ($\text{RMS} < 0.05$).
   - 9.1% (1/11): Global average pooling dilution over long audio (8.0s file with 0.6s scream).
   - 9.1% (1/11): Borderline probability ($P=0.3543$).
4. **19 False Alarms Forensic Drivers:**
   - 73.7% (14/19): Crowd cheering (7 FP) and shouted speech (7 FP).
   - Subband head (Path C) triggered on Band 4 ($2\text{--}3\text{ kHz}$) energy, elevating false alarms.
5. **Short-Scream Sample Inadequacy:**
   - Test cohort contains only $N=5$ short screams (<1.0s).
   - 95% Wilson confidence interval spans $[56.55\%, 100.00\%]$.
   - Statistically impossible to prove $\ge 90\%$ population recall with only 5 samples.
6. **Dataset Deduplication & Disjointness:**
   - 100% unique PCM hashes (0 duplicates).
   - 100% disjoint source groups across Train, Val, Test.
   - 152 CC BY-NC recordings (11.4%) quarantined from commercial production.
