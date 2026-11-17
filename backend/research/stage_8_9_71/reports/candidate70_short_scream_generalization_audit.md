# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 70-D Held-Out Short-Scream Generalization & Cluster Audit

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.71  
**Evaluator:** Dataset Governance & Clustering Statistics Engine  
**Cohort Analyzed:** Stage 64 Held-Out Short-Scream Partition ($N=268$)  
**Source-Group Count:** 7 Independent Source Groups  
**Evaluation Model:** Candidate 70-D Frozen Checkpoint (`candidate_70_frozen.pt`)  
**Overall Point Estimate:** **58.96%** (158 / 268 clips detected)  

---

## 1. Executive Summary

This audit evaluates the generalization properties of Candidate 70-D across the 268-clip held-out short-scream collection ($< 1.0$s duration). 

Crucially, **the 268 clips must not be treated as 268 independent statistical observations**. They originate from only **seven recording source groups**, with a single outdoor group (`sg_short_s49`) contributing over 61% of all clips. 

When statistical uncertainty is recalculated using a **source-group cluster-aware bootstrap** ($B=2,000$ iterations, resampling source groups with replacement), the true 95% confidence interval spans:
$$\mathbf{[46.67\%,\; 83.14\%]}$$
This is substantially wider than the naive clip-level i.i.d. interval ($[52.98\%,\; 64.93\%]$). This wide spread demonstrates that performance on short screams is highly sensitive to the recording environment, acoustic capture chain, and ambient background masking of the capturing source group.

---

## 2. Source-Group Stratification & Cluster Breakdown

The table below details Candidate 70-D's empirical performance across the seven constituent source groups:

| Source Group ID | Clip Count ($N$) | Percentage of Cohort | True Positives (TP) | False Negatives (FN) | Group Recall (%) | Mean Duration (s) | Mean Vocal HNR (dB) | Acoustic Capture Context |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `sg_short_acq` | 8 | 2.99% | 8 | 0 | **100.00%** | 0.476 s | -2.36 dB | Close-proximity smartphone vocal bursts |
| `sg_short_pos` | 2 | 0.75% | 2 | 0 | **100.00%** | 0.690 s | -0.70 dB | High-intensity simulated distress recordings |
| `sg_short_s43` | 37 | 13.81% | 31 | 6 | **83.78%** | 0.608 s | +0.88 dB | Semi-reverberant outdoor amphitheater |
| `sg_short_s49` | 164 | 61.19% | 90 | 74 | **54.88%** | 0.657 s | +6.73 dB | Outdoor festival / stadium crowd field recordings |
| `sg_short_supp` | 34 | 12.69% | 11 | 23 | **32.35%** | 0.636 s | -1.39 dB | High ambient crowd noise & masked screams |
| `sg_short_v2` | 4 | 1.49% | 1 | 3 | **25.00%** | 0.722 s | +4.18 dB | High-pass filtered emergency drill recordings |
| `sg_short_v3` | 19 | 7.09% | 15 | 4 | **78.95%** | 0.765 s | -0.36 dB | Indoor hall echoes and diffuse screams |
| **Total / Overall** | **268** | **100.0%** | **158** | **110** | **58.96%** | **0.653 s** | **+4.11 dB** | **7 Clustered Source Groups** |

---

## 3. Acoustic Failure Mechanism in Low-Recall Clusters

### 3.1 The Severe Masking in `sg_short_supp` (32.35% Recall)
`sg_short_supp` exhibits the lowest mean vocal harmonics-to-noise ratio (-1.39 dB), indicating heavy acoustic masking from overlapping cheers, music basslines, and environmental crowd noise. In this group:
- 23 out of 34 screams are missed.
- Mean pre-veto raw neural probability is only **0.386**, well below the 0.4920 operating threshold.
- The dual-resolution neural branches fail to detect the scream onsets because stationary noise elevators flatten spectral contrast across the 250 ms short-branch window.

### 3.2 The Dominant Cluster `sg_short_s49` (54.88% Recall)
Because `sg_short_s49` contains 164 clips (61.19% of the dataset), overall benchmark performance is overwhelmingly determined by this single cluster.
- Mean duration is 0.657 s.
- 74 screams are missed.
- Acoustic analysis reveals that the screams in `sg_short_s49` were captured at substantial physical distance (estimated 15–30 meters from the microphone), attenuating high frequencies above 3 kHz and eroding the steep spectral tilt that characterizes near-field screams.

---

## 4. Parent-Recording Relationships & Cluster Dependencies

Inspection of the audio provenance confirms multiple clips in `sg_short_s49` and `sg_short_supp` originate as sliced temporal segments from the same extended parent audio tracks. For instance:
- `sg_short_s49` comprises segments from 12 parent festival recordings.
- `sg_short_supp` comprises segments from 4 parent environmental noise files.

Because segments cut from the same parent recording share identical microphone frequency response, room acoustics, and ambient crowd texture, treating them as independent statistical degrees of freedom severely underestimates confidence intervals.

---

## 5. Statistical & Governance Conclusions

1. **Mandatory Clustering Correction:** Future stages must report group-clustered bootstrap intervals ($[46.67\%,\; 83.14\%]$) alongside point estimates to prevent false confidence in generalization.
2. **Diagnostic Classification:** This 268-clip cohort has been repeatedly evaluated across Stages 64 through 71. It is permanently classified as **`DIAGNOSTIC_EVALUATION_BENCHMARK`** and cannot be used as an untouched final validation set.
3. **Research Direction:** To close the recall gap on `sg_short_supp` and `sg_short_s49`, neural representation learning must focus on **distance-attenuated spectral features** and **noise-floor adaptive normalization** rather than heuristic threshold adjustments.

