# Cross-Candidate Error Comparison — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase D of Stage 8.9.59, a cross-candidate error comparison was conducted across the frozen research candidates on identical validation recordings (`expansion_val`, $N=311$ total clips, $N=99$ authentic screams, $N=212$ hard negatives):
1. **Candidate E1 + C5:** Dual-head semantic + acoustic phonation + C5 subband DSP ($\theta = 0.6800$).
2. **Candidate B Baseline:** Masked acoustic dual-head baseline ($\theta = 0.8000$).
3. **Candidate B + Intervention D:** Masked acoustic dual-head baseline with frozen whistle veto ($\theta = 0.8000$).

The candidates exhibited **95.82% overall decision agreement** (disagreeing on only 13 out of 311 recordings). All three candidates share identical acoustic ceilings (12 shared false negatives and 10 shared false positives).

---

## 2. Comprehensive Candidate Performance Matrix ($N=311$, Respective Frozen $\theta$)

| Evaluation Metric | Candidate E1 + C5 ($\theta=0.6800$) | Candidate B Baseline ($\theta=0.8000$) | Candidate B + Intervention D ($\theta=0.8000$) | Candidate B $\leftrightarrow$ E1 Comparison |
|---|:---:|:---:|:---:|:---:|
| **Overall Scream Recall** | **83.84% (83/99)** | **83.84% (83/99)** | 82.83% (82/99) | Identical baseline recall |
| **Hard-Negative FPR** | 6.13% (13/212) | **5.19% (11/212)** | **5.19% (11/212)** | Candidate B lower by 0.94% |
| **Shouted-Speech FPR** | 11.36% (10/88) | **10.23% (9/88)** | **10.23% (9/88)** | Candidate B lower by 1.13% |
| **Short-Scream Recall (<1.0s)** | **94.87% (37/39)** | 92.31% (36/39) | 92.31% (36/39) | Candidate E1 higher by 2.56% |
| **Ultra-Short Recall (<0.5s)** | **100.0% (15/15)** | **100.0% (15/15)** | **100.0% (15/15)** | Identical 100% detection |
| **Sustained-Scream Recall ($\ge 1.0$s)** | 76.67% (46/60) | **78.33% (47/60)** | 76.67% (46/60) | Candidate B higher by 1.66% |
| **Whistle & Squeak FPR** | **0.00% (0/22)** | 4.55% (1/22) | **0.00% (0/22)** | E1 matches B+D without veto |
| **Precision** | 86.46% (83/96) | **88.30% (83/94)** | 88.17% (82/93) | Candidate B higher by 1.84% |
| **F1 Score** | 0.8513 | **0.8601** | 0.8542 | Candidate B higher by 0.0088 |
| **ROC-AUC** | **0.9662** | 0.9653 | 0.9653 | Candidate E1 higher by 0.0009 |
| **PR-AUC** | **0.9421** | 0.9388 | 0.9388 | Candidate E1 higher by 0.0033 |
| **Model Inference Latency (P50)**| **0.49 ms** | 0.62 ms | 0.75 ms | Candidate E1 faster by 21% |
| **Model Inference Latency (P95)**| **0.50 ms** | 0.68 ms | 0.82 ms | Candidate E1 faster by 26% |
| **Downstream Pipeline Latency (P95)**| **7.14 ms** | 7.70 ms | 9.15 ms | Candidate E1 + C5 fastest |

---

## 3. Error Overlap and Agreement Analysis

```
Candidate Prediction Concordance Across N=311 Clips:
========================================================================================
All Candidates Agree (Concordant):  298 clips (95.82%)
Candidates Disagree (Discordant):    13 clips ( 4.18%)
========================================================================================

Shared vs Unique Error Distribution:
----------------------------------------------------------------------------------------
Shared False Negatives (All Candidates):  12 clips (75.0% of FN)
Unique False Negatives (Candidate E1):     4 clips
Unique False Negatives (Candidate B):      4 clips

Shared False Positives (All Candidates):  10 clips (76.9% of FP)
Unique False Positives (Candidate E1):     3 clips (2 Infant Crying, 1 Shouted Speech)
Unique False Positives (Candidate B):      1 clip  (1 Referee Whistle)
----------------------------------------------------------------------------------------
```

### Shared Failure Modes
1. **12 Shared False Negatives:** Includes all 5 synthetic screams with high ambient crowd noise ($-6\text{ dB}$ SNR), 2 unvoiced NIGENS gasps, and 5 prolonged multi-second performance cries. Neither neural architecture is able to detect these recordings at their operating thresholds.
2. **10 Shared False Positives:** Includes 9 shouted-speech recordings (all from `reitanna` Session 3439 and `ericsueiro` Session 2208) and 1 sports arena cheering recording (`exp_v3_fsd50k_361225`). Both candidate architectures are fooled by these identical recordings.

### Unique Error Disagreements
- **Whistles:** Candidate B triggers a false alarm on `exp_v2_whistle_014` ($p=0.824$), whereas Candidate E1 + C5 easily rejects it ($p=0.012$). Adding Intervention D to Candidate B eliminates this error.
- **Infant Crying:** Candidate E1 triggers 2 borderline false positives on crying (`exp_v2_fsd50k_344030` at $p=0.708$, `exp_v2_fsd50k_80479` at $p=0.701$), whereas Candidate B narrowly rejects them ($p=0.782$ and $p=0.765$ against $\theta=0.8000$).
- **Near-Miss Screams:** Candidate E1 correctly detects `exp_v2_synth_scream_002` ($p=0.712$) which Candidate B misses ($p=0.781$ vs $\theta=0.8000$). Conversely, Candidate B detects `exp_v3_fsd50k_220658` ($p=0.814$) which Candidate E1 misses ($p=0.588$).

---

## 4. Methodological Findings

1. **Architecture Parity:** Candidate E1 + C5 and Candidate B exhibit virtually identical classification trade-offs on the validation set (83.84% recall for both; F1 score within 0.0088).
2. **Inherent Acoustic Ceilings:** The fact that 75% of false negatives and 77% of false positives are identical between structurally different neural networks proves that **model architecture is not the limiting factor**. The limiting factor is acoustic representation in the underlying training data.
3. **Latency Advantage:** Candidate E1 + C5 delivers lower model forward latency (0.50 ms vs 0.68 ms P95) and fully integrated whistle rejection without requiring an auxiliary discriminator pipeline.
4. **Preservation:** Full per-recording comparisons are archived in [`candidate_error_comparison.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/candidate_error_comparison.csv).

