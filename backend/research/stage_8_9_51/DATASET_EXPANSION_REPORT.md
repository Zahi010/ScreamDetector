# Authentic Positive-Class Dataset Expansion Report — Stage 8.9.51

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary & Acquisition Rationale

Workstreams A, B, and C conclusively proved that the primary bottleneck preventing the Festival Scream Detector from achieving Gate 1 ($\ge 96.0\%$ overall recall) is an **authentic positive dataset representation deficit** in difficult acoustic environments:
- **Low-intensity & muffled screams:** 9 misses out of 15 ($40.0\%$ recall).
- **Crowd-masked screams:** 7 misses out of 20 ($65.0\%$ recall).
- **Sustained screams:** 9 misses out of 35 ($74.29\%$ recall).

Together, these three categories account for **25 out of the 29 false negatives ($86.2\%$)** in the Stage 8.9.50 independent cohort.

---

## 2. Quantitative Representation Gap Across Existing Splits

Data extracted from [`results/DATASET_REPRESENTATION_GAPS.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_51/results/DATASET_REPRESENTATION_GAPS.csv) demonstrates the severe structural imbalance in current training assets:

| Dataset Partition | Total Positives | Low-Intensity / Muffled | Crowd-Masked | Distant / Reverb | Total Difficult Acoustic | Difficult Ratio (%) | Misses Produced in Indep Cohort |
|---|---|---|---|---|---|---|---|
| **Dev Split (Training, $N=200$)** | 80 | 6 ($7.5\%$) | 10 ($12.5\%$) | 10 ($12.5\%$) | 26 | **$32.5\%$** | - |
| **Val Split (Validation, $N=120$)** | 48 | 4 ($8.3\%$) | 6 ($12.5\%$) | 6 ($12.5\%$) | 16 | **$33.3\%$** | - |
| **Independent Cohort ($N=480$)** | 160 | 15 ($9.4\%$) | 20 ($12.5\%$) | 20 ($12.5\%$) | 55 | **$34.4\%$** | **25 / 29 misses (86.2%)** |

### The Representation Paradox:
While difficult categories comprise approximately one-third of the positive instances in each split, their absolute count in the training set is minuscule: **only 6 low-intensity muffled screams and 10 crowd-masked screams exist in the entire Dev training split**.

With only 6 training examples of muffled screams, the neural network cannot learn robust invariant representations that generalize to diverse microphones, enclosures, and acoustic distances.

---

## 3. Authentic Data Expansion Specification for Next Research Stage

To resolve this limitation without relying on synthetic artifacts or data leakage, the following authentic data acquisition plan is established:

### Target Acquisition Quotas:
1. **Low-Intensity & Muffled Screams:** $+40$ new authentic source recordings.
   - Sourced from outdoor distance recordings, behind obstacles/barriers, indoor adjoining rooms, and partially smothered/muffled vocalizations.
2. **Crowd-Masked Screams:** $+45$ new authentic source recordings.
   - Sourced from authentic festival, sporting event, carnival, and concert environments with high multi-talker babble.
3. **Sustained Screams with Phonation Modulation:** $+35$ new authentic source recordings.
   - Sourced from rollercoasters, haunted attractions, and vocal distress exercises ($1.5\text{ s}$ to $3.5\text{ s}$ duration).

### Mandatory Dataset Governance Rules:
- **Eligible Licenses:** Creative Commons Zero (CC0), Public Domain, and CC BY (with uploader attribution).
- **Prohibited / Quarantined Licenses:** CC BY-NC and CC BY-NC-ND are quarantined unless explicitly cleared.
- **Provenance Tracking:** Every recording must preserve original source URL, recording ID, uploader handle, license text, source group ID, raw file SHA-256, and decoded PCM SHA-256.
- **De-duplication:** Strict dual-level hash check (file hash + decoded 16-bit PCM hash) and cross-correlation filtering ($r < 0.08$) against all historical files.
- **Source-Group Partitioning:** All clips originating from the same recording session, uploader, or video must be assigned strictly to a single partition (`train`, `val`, or `test`) to prevent intra-session leakage.

---

## 4. Conclusion & Stage Gate Impact

Candidate B and Intervention D have achieved state-of-the-art false-alarm rejection ($0.00\%$ HN-FPR, $0.00\%$ shouted-speech FPR) and ultra-low inference latency ($0.77\text{ ms}$ P95). However, Gate 1 overall recall ($81.88\%$) cannot reach the required $\ge 96.0\%$ threshold until authentic training data is expanded in low-intensity and crowd-masked acoustic domains.

