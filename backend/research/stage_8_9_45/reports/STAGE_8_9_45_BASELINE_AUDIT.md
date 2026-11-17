# Baseline Forensic Audit — Stage 8.9.45

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe playback protocols only.

---

## 1. Executive Summary

This forensic audit evaluates the integrity, reproducibility, and methodology of the Stage 8.9.44 baseline results before initiating Stage 8.9.45 experiments. Stage 8.9.44 evaluated five `DualEncoderAcousticModel` candidates trained on different environmental acoustic transformations. The primary findings established that background noise masking (Candidate D) substantially improved detection on masked screams (+18.75%) and distant screams (+16.67%), but overall holdout recall dipped slightly from 75.36% (52/69) to 72.46% (50/69) due to a slight loss in sustained screams (from 35/52 to 33/52).

All ten audit criteria specified for Phase A have been verified against actual artifacts and manifests on disk.

---

## 2. Verification of the 10 Phase A Criteria

### Criterion 1: Identical Evaluation Recordings and Labels
All five candidates were evaluated on exactly identical sets of audio recordings:
- `v5_development_test`: Exactly 202 recordings (81 screams, 121 negatives) across 90 source groups.
- `v5_final_holdout`: Exactly 205 recordings (69 screams, 136 negatives) across 95 source groups.
Ground-truth binary labels and multi-label acoustic metadata are identical byte-for-byte across all model evaluations.

### Criterion 2: Source-Group Partition Independence
The master dataset manifest (`dataset_manifest_v5.csv`, $N=1,914$) was partitioned strictly at the source-group level:
- `v5_train`: 1,198 clips across 436 source groups.
- `v5_validation`: 309 clips across 107 source groups.
- `v5_development_test`: 202 clips across 90 source groups.
- `v5_final_holdout`: 205 clips across 95 source groups.
Pairwise intersection check confirmed **strictly 0 overlapping source groups** across all partition combinations.

### Criterion 3: Exclusivity of Augmentation to Training Data
Augmentation manifests (`augmented_manifest_condition_{b,c,d,e}.csv`) contain 401 clips each ($401 \times 4 = 1,604$ total). Forensic tracing confirmed that 100% of the `original_file_id` values belong strictly to the 401 positive recordings in `v5_train`. Zero recordings from `v5_validation`, `v5_development_test`, or `v5_final_holdout` were transformed, augmented, or added to training cohorts.

### Criterion 4: Validation-Only Threshold Selection
Operating decision thresholds were selected strictly on `v5_validation` ($N=309$) by sweeping $\theta \in [0.10, 0.99]$ to satisfy $\text{HN-FPR} \le 5.0\%$:
- Candidate A (`Config-B-v5-baseline`): $\theta^* = 0.8200$ (Val AUC: 0.9458, Val HN-FPR: 2.60%)
- Candidate B (`Config-B-RIR`): $\theta^* = 0.9800$ (Val AUC: 0.9365, Val HN-FPR: 0.87%)
- Candidate C (`Config-B-Atten`): $\theta^* = 0.9300$ (Val AUC: 0.9390, Val HN-FPR: 2.60%)
- Candidate D (`Config-B-Mask`): $\theta^* = 0.8600$ (Val AUC: 0.9362, Val HN-FPR: 3.46%)
- Candidate E (`Config-B-EnvCombined`): $\theta^* = 0.8500$ (Val AUC: 0.9372, Val HN-FPR: 2.60%)
Thresholds were permanently frozen in `configs/*.json` before evaluating test partitions.

### Criterion 5: Sealed Final Holdout Benchmark
The final holdout (`v5_final_holdout`, $N=205$) was never used for feature selection, hyperparameter tuning, loss calculation, early stopping, or threshold tuning. It was evaluated only after all configurations and thresholds were frozen.

### Criterion 6: Candidate D Detection Reproducibility
Candidate D's subtype performance on the sealed holdout was verified directly from saved predictions:
- **Masked Screams:** Exactly **11/16 (68.75%)** detected vs 8/16 (50.00%) in Baseline A.
- **Distant Screams:** Exactly **12/18 (66.67%)** detected vs 9/18 (50.00%) in Baseline A.
- **Overall Recall:** Exactly **50/69 (72.46%)** detected vs 52/69 (75.36%) in Baseline A.

### Criterion 7: Metric Calculation Accuracy
ROC-AUC and Brier scores were recalculated directly from holdout prediction arrays:
- Candidate D Holdout ROC-AUC: **0.9531** (matches `candidate_eval_metrics_v6.json` and `CANDIDATE_COMPARISON_V6.csv`).
- Candidate D Holdout Brier Score: **0.0909** (matches exactly).
- Baseline A Holdout ROC-AUC: **0.9487**, Brier Score: **0.0965** (matches exactly).

### Criterion 8: Documented Latency Pipeline Components
Inference latency was measured using the complete streaming pipeline:
1. Feature tensor packing (1024-d YAMNet embedding + 6-d acoustic features + 6-d presence mask).
2. PyTorch model forward pass through `DualEncoderAcousticModel`.
3. Logistic sigmoid probability computation and threshold comparison.
Measured P95 latency was $0.503\text{ ms} - 0.586\text{ ms}$ across all candidates, verifying Gate 5 compliance ($P95 \le 25.0\text{ ms}$).

### Criterion 9: 401-to-1,604 Augmentation Reconciliation
- Original authentic positive training clips: Exactly **401** in `v5_train`.
- Condition B (RIR): 401 transformed files.
- Condition C (Attenuation): 401 transformed files.
- Condition D (Masking): 401 transformed files.
- Condition E (Combined): 401 transformed files.
Total augmented files generated and cataloged: Exactly **1,604**, matching `augmented_features_v6.npz` rows $(1,604)$.

### Criterion 10: Subtype Categories and Overlapping Labels
In the positive test cohort ($N=69$ on holdout), clips carry multi-label acoustic attributes:
- **Duration-based (disjoint):** Ultra-short ($<0.5\text{ s}$, $N=8$), Standard short ($0.5–1.0\text{ s}$, $N=9$), Sustained ($>1.0\text{ s}$, $N=52$). Sum: $8 + 9 + 52 = 69$.
- **Acoustic condition (overlapping):**
  - Distant / reverberant ($N=18$): Recordings captured at substantial physical distance or with room reflections.
  - Masked screams ($N=16$): Recordings with simultaneous background sound (crowd, music, cheering).
  - Low-intensity / muffled ($N=3$): High-frequency attenuation or low SNR.
  - Note: A sustained scream can also be distant or masked, explaining why subtype counts overlap.

---

## 3. Conclusion

The Phase A forensic audit establishes that the Stage 8.9.44 baseline is methodologically sound, strictly partitioned, and completely reproducible. We now proceed to Phase B to analyze individual false negatives, false positives, and candidate disagreements.

