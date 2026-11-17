# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.66.1 — SOURCE-GROUP & RECORDING LEAKAGE AUDIT REPORT
**Cryptographic Hash, Decoded PCM, and Source-Group Overlap Analysis**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous external response, police notification, active-shooter alerting, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
This audit evaluated cryptographic PCM hashes (`pcm_sha256`), file hashes (`file_sha256`), duration boundaries, and hierarchical source-group identifiers (`source_group_id`) across all major historical partitions and evaluation cohorts.

The complete pairwise overlap matrix is cataloged in [`reports/recording_source_group_overlap_matrix.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66_1/reports/recording_source_group_overlap_matrix.csv).

### Key Findings:
1. **$N=312$ Cohort vs. Historical Stage 54 Partitions:** Exactly **0** exact recording matches and **0** source-group overlaps with the Stage 54 Training, Validation, or Reserved Test partitions.
2. **$N=312$ Cohort vs. Stage 60 Sealed Cohort:** Exactly **0** exact recording matches and **0** source-group overlaps with the Stage 60 sealed evaluation cohort ($N=700$).
3. **Candidate 65-F Training vs. $N=312$ Cohort:** **100% overlap**. The frozen model checkpoint (`models/candidate_65f_frozen.pt`) was trained on all 312 recordings across all 188 source groups.
4. **Candidate 65-F 5-Fold Validation vs. $N=312$ Cohort:** In cross-validation, fold-wise separation was strictly maintained (each fold trained on 4/5ths and validated on 1/5th with stratified class balance), but source-group stratification was not enforced across folds, allowing mild intra-cluster cross-fold correlation.

---

## 3. Comprehensive Leakage Matrix

| Partition / Cohort Comparison | Total Recordings (A vs B) | Exact PCM Hash Overlap | Near-Duplicate Overlap | Source-Group Overlap | Leakage Assessment |
|---|---|---|---|---|---|
| **Candidate 65-F Frozen Train vs. $N=312$** | 312 vs 312 | **312 (100.0%)** | 0 | **188 (100.0%)** | **COMPLETE EXPOSURE (Model Trained on Dataset)** |
| **Stage 54 Train vs. $N=312$ Dev** | 988 vs 312 | **0 (0.0%)** | 0 | **0 (0.0%)** | **CLEAN (Zero Overlap)** |
| **Stage 54 Val vs. $N=312$ Dev** | 356 vs 312 | **0 (0.0%)** | 0 | **0 (0.0%)** | **CLEAN (Zero Overlap)** |
| **Stage 54 Reserved Test vs. $N=312$ Dev** | 388 vs 312 | **0 (0.0%)** | 0 | **0 (0.0%)** | **CLEAN (Zero Overlap)** |
| **Stage 60 Sealed Cohort vs. $N=312$ Dev** | 700 vs 312 | **0 (0.0%)** | 0 | **0 (0.0%)** | **CLEAN (Zero Overlap, Preserved Sealed)** |
| **Stage 64 Short Screams vs. $N=312$ Dev** | 401 vs 312 | **133 (33.2%)** | 0 | **86 (45.7%)** | **PARTIAL EXPOSURE (133 Dev Clips, 268 Held-Out)** |
| **Stage 64 Short Screams vs. Stage 60 Sealed** | 401 vs 700 | **0 (0.0%)** | 0 | **0 (0.0%)** | **CLEAN (Zero Overlap)** |
| **Stage 66 Shouted Speech vs. $N=312$ Dev** | 529 vs 312 | **1 (0.2%)** | 0 | **1 (0.5%)** | **NEGLIGIBLE (1 File Overlap: `s60_rec_0332`)** |
| **Stage 66 Shouted Speech vs. Stage 60 Sealed** | 529 vs 700 | **150 (28.4%)** | 0 | **34 (21.3%)** | **HEAVY CONTAMINATION WITH SEALED COHORT** |
| **Stage 66 Hard Negatives vs. $N=312$ Dev** | 462 vs 312 | **116 (25.1%)** | 0 | **115 (30.7%)** | **HEAVY EXPOSURE (116 Negatives are in Dev Set)** |
| **Stage 66 Hard Negatives vs. Stage 60 Sealed** | 462 vs 700 | **331 (71.6%)** | 0 | **260 (69.3%)** | **MASSIVE CONTAMINATION WITH SEALED COHORT** |

---

## 4. In-Depth Forensic Analysis

### A. The Independence of $N=312$ from Sealed Data
A critical positive finding of this audit is that **the $N=312$ development cohort is 100% disjoint from the Stage 60 sealed evaluation cohort**:
- Not a single recording, decoded PCM audio byte, or source group from the $N=312$ development set exists within the 700-recording sealed evaluation manifest (`future_evaluation_manifest.json`).
- This proves that while Candidate 65-F was tuned on the $N=312$ development set, **the Stage 60 sealed evaluation cohort remains pristine and uncompromised**.

### B. The Contamination of the Stage 66 Expanded Negative Datasets
A critical risk uncovered by this audit is that **the expanded negative datasets constructed in Stage 66 are heavily contaminated with both development data and sealed cohort data**:
- **Hard Negative Cohort ($N=462$):** 116 of these recordings are in the $N=312$ development cohort, and 331 are in the sealed evaluation cohort! Only 15 files are outside both, and those 15 share source groups with the sealed cohort.
- **Shouted Speech Cohort ($N=529$):** 150 of these files belong to the sealed evaluation cohort, 147 belong to Stage 54 training, and 88 belong to Stage 54 validation.

### C. Governance Implication
Evaluating Candidate 65-F on the entirety of the Stage 66 expanded negative files would violate evaluation integrity by either:
1. Re-evaluating on data used to train/tune the model (116 hard negatives).
2. Unsealing and leaking 481 recordings (331 HN + 150 Shouted) that belong to the sealed evaluation cohort!

---

## 5. Conclusion
- The $N=312$ cohort is confirmed to have zero leakage into historical test or sealed cohorts, but 100% leakage into Candidate 65-F's training history.
- The Stage 66 expanded negative cohorts must NOT be evaluated as a single monolithic "unseen" test set. Only verified disjoint subsets (such as the 111 Stage 54 reserved test shouted-speech files) can be evaluated without compromising sealed assets.

