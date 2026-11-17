# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — N=312 EVALUATION COHORT CLASSIFICATION
**Definitive Evidentiary Audit of Cohort Function, Role, and Independence**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Cohort Specification & Reconstruction

- **Manifest File:** `backend/research/stage_8_9_63/stage_63_development_manifest.csv`
- **Manifest SHA-256:** `a33e37ecf1bef23bf610baf2a5b42d5e800152dbc518be00a0d4fb5a8229df51`
- **Total Recordings:** 312
- **Positive Recordings (True Screams):** 195 (62.50%)
  - Short screams ($< 1.00$s): 133
  - Sustained screams ($\ge 1.00$s): 62
- **Negative Recordings (Hard Negatives):** 117 (37.50%)
  - Environmental noise: 114
  - Referee whistles / pure tones: 2
  - Shouted speech: 1 (nominally labeled) / 5 (forensically audited)
- **Unique Source Groups:** 188
- **Creation Stage & Date:** Stage 8.9.63 (November 11, 2026)

---

## 3. Cohort Functional Role Classification

Based on exhaustive forensic tracking of code, training loops, threshold selection, and model selection across Stages 8.9.63, 8.9.64, 8.9.65, and 8.9.66, the $N=312$ cohort is formally classified under the following roles:

| Functional Category | Classification Verdict | Evidentiary Basis |
|---|---|---|
| **A. Training Data** | **CONFIRMED** | 100% of the 312 recordings were used to train the frozen checkpoint (`models/candidate_65f_frozen.pt`). In cross-validation, 80% was in `train_idx` per fold. |
| **B. Validation Data** | **CONFIRMED** | Used as the out-of-fold validation set during 5-fold cross-validation in Stages 65 and 66. |
| **C. Development Benchmark** | **CONFIRMED** | Repeatedly evaluated across Stages 63, 64, 65, and 66 to evaluate Baseline, Variant 6, Candidates 65-A through 65-F, and Sust_A through Sust_F. |
| **D. Final Model Selection** | **CONFIRMED** | Candidate 65-F was chosen as the lead model over all competing architectures because of its metrics on this cohort. |
| **E. Untouched Independent Test Set** | **DEFINITIVELY REFUTED** | Fails all five independence criteria (used for training, validation, threshold selection, filter tuning, and model selection). |

### Formal Verdict:
```
========================================================================================
                      FORMAL COHORT ROLE CLASSIFICATION:
                   DEVELOPMENT BENCHMARK & CALIBRATION DATA
                     (CATEGORICALLY NOT AN INDEPENDENT TEST SET)
========================================================================================
```

---

## 4. Application of Mandatory Governance Rules

1. **Rule 1: A dataset used for repeated candidate comparisons is development data.**
   - *Evidence:* The $N=312$ cohort was evaluated in Stage 64 (`dual_resolution_reproduction.csv`), Stage 65 (`baseline_reproduction.csv`, `variant6_reproduction.csv`, `selective_suppression_ablation.csv`), and Stage 66 (`candidate_65f_predictions.csv`, `sust_d_predictions.csv`, `four_candidate_comparison.csv`). Over 15 distinct model variations were compared on these identical 312 audio clips.
2. **Rule 2: A dataset used for threshold selection is not an untouched final test set.**
   - *Evidence:* In `stage_8_9_65/run_threshold_calibration.py`, the decision threshold $\tau = 0.4800$ was selected by performing a threshold sweep across these 312 files to maximize F1 score.
3. **Rule 3: A dataset used to select Candidate 65-F over alternatives is not an untouched final test set.**
   - *Evidence:* Candidate 65-F was chosen over Sust_D and Variant 6 in `stage_8_9_66/scripts/select_evaluation_candidate.py` based directly on the confusion matrix derived from these 312 files.
4. **Rule 4: A dataset with source-group overlap with training data is not fully independent.**
   - *Evidence:* In the final frozen checkpoint `models/candidate_65f_frozen.pt`, all 188 source groups in the $N=312$ cohort were present in the training set.

---

## 5. Preservation of Historical Comparative Value

Classifying the $N=312$ cohort as development data does not diminish its scientific utility:
- It serves as a **high-precision standardized development benchmark** that reliably detected Variant 6's recall destruction (13 screams destroyed) and Sust_D's false alarm explosion (68 false positives).
- It established that Candidate 65-F achieves the highest internal discrimination ($F1 = 0.9534$).
- However, its metrics ($94.36\%$ recall, $5.98\%$ FPR) must be understood as **cross-validated training/development estimates**, not unbiased measures of generalization to the real world.

