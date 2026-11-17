# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — CANDIDATE 65-F PROVENANCE AUDIT REPORT
**Reconstruction of Training Lineage, Validation History, and Selection Influences**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
This audit reconstructs the complete developmental and empirical lineage of **Candidate 65-F** (`Candidate_65_F_Combined_Selective`) across Stages 8.9.63, 8.9.64, 8.9.65, and 8.9.66.

The historical investigation confirms:
1. **Candidate 65-F was trained directly on the $N=312$ cohort:** During Stage 8.9.65 development, Candidate 65-F was trained via 5-fold cross-validation on `stage_63_development_manifest.csv` ($N=312$). In Stage 8.9.66, 100% of the $N=312$ cohort was used to train the frozen checkpoint (`models/candidate_65f_frozen.pt`).
2. **Threshold Selection was derived from the $N=312$ cohort:** The operating threshold $\tau = 0.48$ was determined through an empirical grid search on this exact cohort.
3. **Filter Design was customized against $N=312$ false alarms:** The narrow-band whistle veto ($\text{HNR} > 12.0\text{ dB}, \text{Flatness} < 0.001$) and branch cosine agreement check ($\text{sim} > 0.40$) were designed specifically to suppress the 25 false positives produced by the Baseline model on the $N=312$ cohort.
4. **Model Selection was determined on the $N=312$ cohort:** Candidate 65-F was selected over Candidates 65-A through 65-E and Sust_D based entirely on its performance on this cohort.

---

## 3. Candidate 65-F Chronological Development Timeline

| Stage | Dataset Used | Dataset Role | Candidate Exposure | Selection Influence | Evidence Source |
|---|---|---|---|---|---|
| **Stage 8.9.63** | `stage_63_development_manifest.csv` ($N=312$) | Development / Architecture Exploration | EXPOSED (Feature exploration & initial dual-resolution training) | Architecture Selection (Dual-Resolution 250ms/1000ms branch design) | `stage_63_development_manifest.csv` |
| **Stage 8.9.64** | `stage_63_development_manifest.csv` ($N=312$) | Development Benchmark | EXPOSED (Baseline model evaluation: 184 TP, 25 FP) | Established Baseline vs Variant 6 comparison | `dual_resolution_reproduction.csv` |
| **Stage 8.9.64** | `stage_64_short_scream_manifest.csv` ($N=401$) | Benchmark Exploration | PARTIALLY EXPOSED (133 clips in dev, 268 held-out) | Motivated short-branch 250 ms energy pooling | `stage_64_short_scream_manifest.csv` |
| **Stage 8.9.65** | `stage_63_development_manifest.csv` ($N=312$) | 5-Fold CV Training & Filter Tuning | FULLY EXPOSED (Refined contrastive weights $w=1.60$) | Filter Design: HNR, Flatness, and Agreement tuning | `run_selective_suppression_ablations.py` |
| **Stage 8.9.65** | `stage_63_development_manifest.csv` ($N=312$) | Threshold Sweep | FULLY EXPOSED ($\tau \in [0.30, 0.70]$ sweep) | Threshold Selection ($\tau = 0.4800$ selected) | `threshold_calibration_sweep.csv` |
| **Stage 8.9.65** | `stage_63_development_manifest.csv` ($N=312$) | Model Selection Tournament | FULLY EXPOSED (Ablations 65-A to 65-F) | Model Selection (65-F selected as lead candidate) | `selective_suppression_ablation.csv` |
| **Stage 8.9.66** | `stage_63_development_manifest.csv` ($N=312$) | Reproduction & Final Parameter Freeze | FULLY EXPOSED (100% of cohort trained frozen weights) | Frozen Checkpoint Generation (`candidate_65f_frozen.pt`) | `freeze_evaluation_candidate.py` |

---

## 4. Key Provenance Audit Findings

### 1. Training Recordings
Candidate 65-F was trained on all 312 recordings from `backend/research/stage_8_9_63/stage_63_development_manifest.csv`. In cross-validation evaluation, 80% (249 or 250 recordings) formed the training set in each fold. In final artifact freezing, all 312 recordings were used as training data.

### 2. Validation Recordings
Validation was conducted using 5-fold stratified cross-validation on the same 312 recordings. Out-of-fold predictions were aggregated into `candidate_65f_predictions.csv`.

### 3. Threshold Selection Influence
The threshold $\tau = 0.4800$ was selected by optimizing the harmonic balance between recall and false positive rate on the out-of-fold probabilities of the $N=312$ cohort (`stage_8_9_65/run_threshold_calibration.py`).

### 4. Filter and Suppression Architecture Influence
The selective suppression stack comprises:
- High-confidence protection: $p \ge 0.80$
- Branch cosine similarity agreement: $\text{sim} > 0.40$
- Narrow-band pure-tone veto: $\text{HNR} > 12.0\text{ dB}$ and $\text{Flatness} < 0.001$
- Post-threshold targeted suppression of pure tones and transient noise

Every one of these heuristics was conceived, refined, and benchmarked directly against the error modes of the $N=312$ cohort.

### 5. Candidate Selection Influence
Candidate 65-F was chosen over Baseline Dual-Resolution, Variant 6 Full-Stack, and Sust_D Dual-Branch solely based on comparative scorecards on the $N=312$ cohort.

---

## 5. Conclusion
Candidate 65-F was developed, trained, calibrated, and selected entirely within the $N=312$ development cohort. Its reported metrics on this cohort are **cross-validated development benchmark results**, not independent test results.

