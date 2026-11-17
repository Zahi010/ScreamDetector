# Subtype Reconciliation & Historical Report Discrepancy Audit — Stage 8.9.52

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.  
> No live-fire experiments, autonomous emergency dispatch, external emergency alerts, or claims of life-safety efficacy.  
> No production promotion is authorized.

---

## 1. Executive Summary & Root Cause Analysis

Stage 8.9.52 investigated the apparent discrepancies between subtype metrics reported in Stage 8.9.50 and Stage 8.9.51:

| Metric / Subtype | Stage 8.9.50 Report Text | Stage 8.9.51 Direct Forensic | True Recording-Level Ground Truth | Discrepancy Cause |
|---|---:|---:|---:|---|
| **Overall Detected Screams** | 131 / 160 | 131 / 160 | **131 / 160 (81.88%)** | Exact parity across all stages |
| **Standard Short ($0.5 < d \le 1.0\text{s}$)** | 45 / 45 | 41 / 45 | **41 / 45 (91.11%)** | Report Documentation Drift (Historical template table copied) |
| **Ultra-Short ($d \le 0.5\text{s}$)** | 25 / 25 | 25 / 25 | **25 / 25 (100.0%)** | Exact parity across all stages |
| **Combined Short ($d \le 1.0\text{s}$)** | 70 / 70 | 66 / 70 | **66 / 70 (94.29%)** | Report Documentation Drift ($41 + 25 = 66$) |
| **Sustained Screams ($d > 1.0\text{s}$)** | 31 / 35 | 26 / 35 | **26 / 35 (74.29%)** | Report Documentation Drift (Historical template table copied) |
| **Distant / Reverberant** | 15 / 20 | 20 / 20 | **20 / 20 (100.0%)** | Report Documentation Drift (Historical template table copied) |
| **Crowd-Masked Screams** | 14 / 20 | 13 / 20 | **13 / 20 (65.00%)** | Report Documentation Drift (Historical template table copied) |
| **Low-Intensity & Muffled** | 6 / 15 | 6 / 15 | **6 / 15 (40.00%)** | Exact parity across all stages |
| **Shouted-Speech False Positives** | 0 / 80 | 1 / 80 | **1 / 80 (1.25%)** | Typographical error in Stage 50 text column |

---

## 2. Root Cause 1: The Historical Documentation Drift in Stage 8.9.49/50

A forensic audit of all markdown reports across the repository revealed how the subtype discrepancies originated:

1. **The Inconsistent Stage 8.9.49 Table:**
   In `backend/research/stage_8_9_49/STAGE_8_9_49_REPORT.md` (lines 60–75) and `CANDIDATE_B_PRESERVATION_REPORT.md`, an earlier draft template table from Stage 8.9.47 was inadvertently preserved. That draft table displayed:
   - Standard short: $45 / 45$
   - Ultra-short: $25 / 25$
   - Sustained: $31 / 35$
   - Distant/reverberant: $15 / 20$
   - Crowd-masked: $14 / 20$
   - Low-intensity: $6 / 15$
   
   **The Internal Arithmetic Contradiction:**
   Notice that the numbers in that copied draft table sum to:
   $$45 + 25 + 31 + 15 + 14 + 6 = \mathbf{136\text{ detected screams}}$$
   However, the headline overall metric in that exact same report was **$131 / 160$** detected screams!
   The draft table reported 136 detected screams, which contradicted its own overall total of 131.

2. **Stage 8.9.50 Re-Quoted the Text Without Recalculating Subtypes:**
   When Stage 8.9.50 audited Stage 8.9.49, it reproduced `INDEPENDENT_EVALUATION_PREDICTIONS.csv` with **100% exact match** ($0$ discordant predictions, $131$ TP, $29$ FN, $1$ FP). However, in the high-level report text summary, Stage 8.9.50 quoted Stage 8.9.49's draft table rather than recalculating the per-subtype counts directly from the CSV.

3. **Stage 8.9.51 Evaluated Directly from Raw Audio and Prediction Records:**
   In Stage 8.9.51, Workstreams A, B, and C extracted every single one of the 160 positive audio files and evaluated metrics directly from the underlying data:
   $$41 + 25 + 26 + 20 + 13 + 6 = \mathbf{131\text{ detected screams}}$$
   $$4 + 0 + 9 + 0 + 7 + 9 = \mathbf{29\text{ missed screams}}$$
   The Stage 8.9.51 numbers sum **exactly and mathematically** to the 131 true positives and 29 false negatives.

---

## 3. Recording-Level Explanation of Every Discrepancy

### 3.1 Standard Short Screams ($45/45$ reported vs $41/45$ actual)
The 4 recordings accounting for the difference are authentic short screams that scored just below the $\theta=0.8000$ threshold:
1. `s49_indep_pos_0057`: $d = 0.80\text{s}$, Prob = $0.7316$ (Missed, pred = 0)
2. `s49_indep_pos_0060`: $d = 0.97\text{s}$, Prob = $0.6902$ (Missed, pred = 0)
3. `s49_indep_pos_0061`: $d = 0.96\text{s}$, Prob = $0.5583$ (Missed, pred = 0)
4. `s49_indep_pos_0063`: $d = 0.95\text{s}$, Prob = $0.7923$ (Missed, pred = 0)

All 4 recordings were missed in Candidate B's saved predictions from the beginning. They were never detected in Stage 8.9.49 or Stage 8.9.50. Their listing as $45/45$ was strictly a documentation artifact.

### 3.2 Sustained Screams ($31/35$ reported vs $26/35$ actual)
The 5 recordings accounting for the difference between 31 and 26 detected are:
1. `s49_indep_pos_0071`: $d = 1.68\text{s}$, Prob = $0.4054$ (Missed, pred = 0)
2. `s49_indep_pos_0072`: $d = 2.29\text{s}$, Prob = $0.1276$ (Missed, pred = 0)
3. `s49_indep_pos_0079`: $d = 2.26\text{s}$, Prob = $0.5043$ (Missed, pred = 0)
4. `s49_indep_pos_0080`: $d = 1.85\text{s}$, Prob = $0.6523$ (Missed, pred = 0)
5. `s49_indep_pos_0090`: $d = 1.58\text{s}$, Prob = $0.3789$ (Missed, pred = 0)

Together with `s49_indep_pos_0077` ($0.7691$), `s49_indep_pos_0082` ($0.6429$), `s49_indep_pos_0097` ($0.7753$), and `s49_indep_pos_0100` ($0.7055$), exactly **9 sustained screams were missed**, leaving **26 / 35 detected**.

### 3.3 Distant & Reverberant Screams ($15/20$ reported vs $20/20$ actual)
In `INDEPENDENT_EVALUATION_PREDICTIONS.csv`, all 20 distant/reverberant screams (`s49_indep_pos_0101` through `s49_indep_pos_0120`) scored probabilities between $0.8142$ and $0.9991$. **All 20 were detected ($20/20 = 100.0\%$)** by frozen Candidate B. The historical figure of $15/20$ was an artifact from Stage 8.9.47.

### 3.4 Crowd-Masked Screams ($14/20$ reported vs $13/20$ actual)
Exactly 7 crowd-masked screams were missed:
- `s49_indep_pos_0126`: Prob = $0.6875$
- `s49_indep_pos_0127`: Prob = $0.7561$
- `s49_indep_pos_0132`: Prob = $0.4028$
- `s49_indep_pos_0136`: Prob = $0.4977$
- `s49_indep_pos_0138`: Prob = $0.6735$
- `s49_indep_pos_0142`: Prob = $0.7990$
- `s49_indep_pos_0144`: Prob = $0.6695$

Detected count is exactly $20 - 7 = \mathbf{13 / 20}$ ($65.0\%$).

---

## 4. Root Cause 2: Shouted-Speech False-Positive Reconciled ($0/80$ vs $1/80$)

In Stage 8.9.50's `STATISTICAL_REANALYSIS.md` (line 15), the table reported:
```markdown
| **Shouted-Speech FPR** | **1.25%** | 0/80 | [0.22%, 6.75%] | ...
```

### Forensic Proof:
1. **Mathematical Evidence:**
   $$\frac{1}{80} = 0.0125 = \mathbf{1.25\%}$$
   The exact 95% Wilson score confidence interval for $k = 1, n = 80$ is:
   $$\text{Wilson}(1, 80) = [\mathbf{0.22\%}, \mathbf{6.75\%}]$$
   For $k = 0, n = 80$, the 95% Wilson confidence interval is $[0.00\%, 4.51\%]$.
   Stage 8.9.50 calculated the exact mathematical point estimate ($1.25\%$) and confidence interval ($[0.22\%, 6.75\%]$) for **$1/80$**, but suffered a clerical typographical error writing `0/80` in the text column.
2. **Recording-Level Identification:**
   The exact recording responsible is:
   - **File ID:** `s49_indep_neg_0009`
   - **Target Category:** `shouting_and_speech`
   - **Acoustic Subtype:** `shouted_speech`
   - **Candidate B Probability:** `0.8769` (Threshold: $0.8000$)
   - **Intervention D Prediction:** `1` (FP)
   - **Audit Tag:** `accepted` (Protected by vocal formant gate)
   - **File SHA-256:** `df28ac301fa4c6ed39331aa3f104e2eb110d0ca1a084c9dc108b512d39555416`
   - **Source Group ID:** `s49_sg_indep_neg_009`

The prediction for `s49_indep_neg_0009` never changed between Stage 8.9.49, 8.9.50, and 8.9.51. It has always been a false positive ($1/80 = 1.25\%$).

---

## 5. Authoritative Baseline Reference Table

The definitive, mathematically verified metrics for Candidate B + Intervention D on the independent evaluation cohort ($N=480$) are:

| Metric | Ground Truth Denominator | Detections / Errors | Authoritative Metric | 95% Wilson Confidence Interval |
|---|---|---|---|---|
| **Overall Scream Recall** | 160 authentic screams | 131 detected | **81.88%** | $[75.19\%, 87.05\%]$ |
| **Standard Short Screams** | 45 screams | 41 detected | **91.11%** | $[79.29\%, 96.62\%]$ |
| **Ultra-Short Screams** | 25 screams | 25 detected | **100.0%** | $[86.68\%, 100.0\%]$ |
| **Combined Short ($d \le 1.0\text{s}$)** | 70 screams | 66 detected | **94.29%** | $[86.20\%, 97.79\%]$ |
| **Sustained Screams** | 35 screams | 26 detected | **74.29%** | $[57.94\%, 85.84\%]$ |
| **Distant / Reverberant** | 20 screams | 20 detected | **100.0%** | $[83.89\%, 100.0\%]$ |
| **Crowd-Masked Screams** | 20 screams | 13 detected | **65.00%** | $[43.29\%, 81.88\%]$ |
| **Low-Intensity & Muffled** | 15 screams | 6 detected | **40.00%** | $[19.34\%, 65.64\%]$ |
| **Hard-Negative FPR** | 320 hard negatives | 1 false positive | **0.31%** | $[0.06\%, 1.75\%]$ |
| **Shouted-Speech FPR** | 80 shouted speech clips | 1 false positive | **1.25%** | $[0.22\%, 6.75\%]$ |
| **Referee Whistle FPR** | 45 referee whistles | 0 false positives | **0.00%** | $[0.00\%, 7.87\%]$ |

---

## 6. Audit Conclusion

All historical discrepancies between Stage 8.9.50 and Stage 8.9.51 are **100% reconciled and explained by recording-level evidence**. The underlying prediction files were never discordant.

