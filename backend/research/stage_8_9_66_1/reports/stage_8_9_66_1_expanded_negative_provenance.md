# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — EXPANDED NEGATIVE DATASET PROVENANCE & UNSEEN INFERENCE AUDIT
**Provenance Deconstruction, Exposure Classification, and Frozen Inference Evaluation**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
In Stage 8.9.66 Track D, two large negative datasets were assembled and cataloged:
- **Shouted-Speech Cohort:** 529 recordings across 160 source groups (`shouted_speech_manifest.csv`)
- **Hard-Negative Expansion Cohort:** 462 recordings across 375 source groups (`hard_negative_expansion_manifest.csv`)

This audit investigated whether these datasets represent genuinely unseen evaluation benchmarks for Candidate 65-F.

### Definitive Provenance Findings:
1. **The 462 Hard Negatives Contain ZERO Disjoint Unseen Data:**
   - **116 recordings (25.1%)** were members of the $N=312$ development set used to train and tune Candidate 65-F.
   - **331 recordings (71.6%)** belong to the Stage 60 Sealed Evaluation Cohort ($N=700$).
   - **15 recordings (3.3%)** share source groups with the sealed cohort.
   - *Verdict:* Evaluating the 462 hard negatives as an "unseen test set" would commit severe data leakage and breach the sealed evaluation barrier.
2. **The 529 Shouted-Speech Files Contain Exactly 111 Eligible Unseen Recordings:**
   - **150 recordings (28.4%)** belong to the Stage 60 Sealed Cohort.
   - **236 recordings (44.6%)** were used in Stage 54 training/validation or development.
   - **32 recordings (6.0%)** share source groups with the sealed cohort.
   - **Exactly 111 recordings (21.0%)** originate from Stage 54 `expansion_reserved_test`. These files were never seen by Candidate 65-F, never used to tune dual-resolution models, and share zero source groups with the $N=312$ development cohort or the sealed cohort.
3. **Frozen Inference on the 111 Unseen Shouted-Speech Files Revealed Severe Failure:**
   - **Observed Shouted-Speech FPR:** **44.14% (49 / 111)** (95% CI: **[35.26%, 53.42%]**).
   - **Gate 3 Target ($\le 15.00\%$):** **CRITICAL FAIL (+29.14% excess)**.
   - Candidate 65-F's apparent 20% shouted-speech FPR in Stage 66 was an artifact of evaluating only 5 files. On genuinely unseen shouted speech, the model fails Gate 3 catastrophically.

---

## 3. Dataset Exposure Classification Breakdown

The complete per-recording exposure classifications are cataloged in [`reports/dataset_exposure_classification.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/dataset_exposure_classification.csv):

| Cohort | Exposure Category | Recording Count | % of Cohort | Historical Exposure / Provenance Detail | Eligible for Frozen Inference? |
|---|---|---|---|---|---|
| **Shouted Speech ($N=529$)** | `SEALED_COHORT_MEMBER` | 150 | 28.36% | Member of Stage 60 sealed 700-clip evaluation cohort. | NO (Must remain sealed) |
| | `PREVIOUSLY_EXPOSED_TRAIN` | 147 | 27.79% | Stage 54 `expansion_train` partition. | NO (Used in training) |
| | `PREVIOUSLY_EXPOSED_VAL` | 88 | 16.64% | Stage 54 `expansion_val` partition. | NO (Used in validation) |
| | `SEALED_SOURCE_GROUP_OVERLAP` | 32 | 6.05% | Shares source groups with sealed cohort. | NO (Leakage risk) |
| | `PREVIOUSLY_EXPOSED_DEV` | 1 | 0.19% | Clip `s60_rec_0332` in $N=312$ dev set. | NO (Used in dev tuning) |
| | `CONFIRMED_UNSEEN` | **111** | **20.98%** | **Stage 54 `expansion_reserved_test` (Never exposed to Dual-Res).** | **YES (Eligible)** |
| **Hard Negatives ($N=462$)** | `SEALED_COHORT_MEMBER` | 331 | 71.65% | Member of Stage 60 sealed 700-clip evaluation cohort. | NO (Must remain sealed) |
| | `PREVIOUSLY_EXPOSED_DEV` | 116 | 25.11% | Present in $N=312$ dev cohort used to train/tune Candidate 65-F. | NO (Training/Dev data) |
| | `SEALED_SOURCE_GROUP_OVERLAP` | 15 | 3.25% | Shares source groups with sealed cohort. | NO (Leakage risk) |
| | `CONFIRMED_UNSEEN` | **0** | **0.00%** | **Zero recordings are both non-dev and unsealed.** | **NO** |

---

## 4. Frozen Inference Evaluation on Unseen Shouted Speech ($N=111$)

In strict compliance with Section 6.1, frozen inference was executed on the 111 confirmed unseen shouted-speech files using:
- **Frozen Checkpoint:** `backend/research/stage_8_9_66/models/candidate_65f_frozen.pt` (SHA-256: `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab`)
- **Fixed Operating Threshold:** $\tau = 0.4800$
- **Inference Pipeline:** C5 DSP feature extraction + selective suppression stack (high-confidence bypass $p \ge 0.80$, branch agreement $\text{sim} > 0.40$, narrow-band whistle veto $\text{HNR} > 12.0, \text{Flatness} < 0.001$).
- **Prediction Log:** [`reports/frozen_inference_shouted_speech_predictions.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/frozen_inference_shouted_speech_predictions.csv)

### Quantitative Results:

| Metric | Measured Value | Standard / Threshold | Evaluation Outcome |
|---|---|---|---|
| **Total Unseen Shouted Files ($N$)** | 111 | $\ge 100$ | Well-powered sample |
| **Independent Source Groups** | 34 | $\ge 25$ | Disjoint source groups |
| **True Negatives (TN)** | 62 | — | Correctly rejected |
| **False Positives (FP)** | **49** | — | **Triggered False Alarms** |
| **Observed Shouted-Speech FPR** | **44.14%** (49 / 111) | $\le \mathbf{15.00\%}$ (Gate 3) | **CRITICAL FAIL (+29.14%)** |
| **95% Wilson Score Confidence Interval** | **[35.26%, 53.42%]** | Entirely above 15% | Statistically decisive failure |

---

## 5. Acoustic Forensic Analysis of the 49 False Alarms

Detailed acoustic inspection of the 49 false positives revealed why Candidate 65-F fails on vocal shouting:
1. **Formant Alignment with Screams:** High-effort vocal shouting produces high acoustic energy concentrated between 1.5 kHz and 3.5 kHz, which mirrors the first and second formant resonance of screams.
2. **Selective Suppression Bypass:**
   - Candidate 65-F's high-confidence bypass protects events with $p \ge 0.80$. In 31 of the 49 false positives, the raw neural posterior exceeded 0.80 due to vocal intensity, bypassing all downstream acoustic checks.
   - Candidate 65-F's branch agreement check protects events with $\text{sim}(z_s, z_l) > 0.40$. In 14 additional cases, the short and sustained branch embeddings showed strong cross-resolution agreement because the shouting was sustained across multiple syllables.
3. **Inapplicability of the Whistle Veto:** Shouted speech is broadband and harmonic, so its harmonics-to-noise ratio rarely exceeds 12 dB and its spectral flatness is $\approx 0.02$ (far above the $0.001$ pure-tone cutoff). The narrow-band whistle veto is physically incapable of suppressing vocal speech.

---

## 6. Conclusion
- Candidate 65-F does **not** generalize to unseen shouted speech. Its real-world false alarm rate on high-effort vocal shouting is $\approx 44.14\%$, far higher than the $20\%$ reported on the 5-sample development subset.
- The 462 hard negatives cannot be used for independent validation because 100% of them either duplicate the development set or breach the sealed evaluation cohort.

