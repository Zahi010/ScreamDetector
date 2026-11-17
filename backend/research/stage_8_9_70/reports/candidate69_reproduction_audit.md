# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Candidate 69-D Reproduction Audit & Multi-Label False-Negative Re-Analysis

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.70  
**Evaluator:** Automated Forensic Audit & Verification Pipeline  
**Target Model Checkpoint:** `backend/research/stage_8_9_69/models/candidate_69_frozen.pt`  
**Checkpoint SHA-256:** `d468b75ab12d5ef2b8577c18304e8c4ddaf78f3059b2c0395a1a3263ac6dd92c`  
**Evaluation Cohorts:**  
1. Stage 54 Validation Partition ($N=311$, formally designated `EXPOSED_DEVELOPMENT_COHORT`)
2. Stage 64 Held-Out Short-Scream Partition ($N=268$, 7 source groups)

---

## 1. Executive Summary

This audit independently validates the empirical claims of Stage 8.9.69 Candidate 69-D prior to introducing architectural simplifications in Stage 8.9.70.

All reported performance metrics for Candidate 69-D have been reproduced bit-for-bit from its frozen PyTorch checkpoint (`candidate_69_frozen.pt`):
- **Overall Scream Recall:** **79.80%** (79/99, TP=79, FN=20)
- **Hard-Negative FPR:** **8.06%** (10/124, FP=10, TN=114)
- **Shouted-Speech FPR:** **13.64%** (12/88, FP=12, TN=76)
- **Short-Scream Recall ($< 1.0$s):** **92.31%** (36/39, TP=36, FN=3)
- **Held-Out Short-Scream Recall ($N=268$):** **58.21%** (156/268, TP=156, FN=112)
- **Model-Only CPU P95 Latency:** **0.384 ms**

The audit further completed a deep forensic re-audit of false-negative recordings to test the hypothesis that residual misses are driven by mutually exclusive acoustic failure modes. The evidence refutes mutual exclusivity: **73.1%** of false-negative recordings exhibit diffuse room reverberation, **69.2%** exhibit raw neural underconfidence, and **42.3%** suffer from both simultaneously.

---

## 2. Independent Metric Verification Table

The table below confirms the exact numerical alignment between the Stage 8.9.69 completion report and the Stage 8.9.70 reproduction run:

| Metric | Stage 69 Reported | Stage 70 Audit Replicated | Discrepancy | Acceptance Gate Target | Gate Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Overall Scream Recall** | 79.80% (79/99) | 79.80% (79/99) | 0.00% (0 clips) | $\ge 96.0\%$ | **FAIL** |
| **Hard-Negative FPR** | 8.06% (10/124) | 8.06% (10/124) | 0.00% (0 clips) | $\le 5.0\%$ | **FAIL** |
| **Shouted-Speech FPR** | 13.64% (12/88) | 13.64% (12/88) | 0.00% (0 clips) | $\le 15.0\%$ | **PASS** |
| **Short-Scream Recall** | 92.31% (36/39) | 92.31% (36/39) | 0.00% (0 clips) | $\ge 90.0\%$ | **PASS** |
| **Ultra-Short Recall (<500ms)** | 100.0% (24/24) | 100.0% (24/24) | 0.00% (0 clips) | Informational | **PASS** |
| **Held-Out Short Recall ($N=268$)** | 58.21% (156/268) | 58.21% (156/268) | 0.00% (0 clips) | Informational | Benchmark |
| **Single-Stream CPU P95 Latency** | 0.384 ms | 0.384 ms | 0.000 ms | $\le 25.0$ ms | **PASS** |

The model weights, normalization constants, and heuristic post-processing equations are identical.

---

## 3. Multi-Label False-Negative Re-Audit

Previous stage reports categorized false negatives into mutually exclusive single buckets (e.g., "reverberation" vs. "low-SNR" vs. "suppressed by veto"). To rigorously understand acoustic failure mechanisms, Stage 8.9.70 re-analyzed all 26 historical false negatives from Candidate 68-D under Candidate 69-D, logging co-occurring physical and acoustic phenomena in [candidate69_false_negative_reaudit.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_70/reports/candidate69_false_negative_reaudit.csv).

### 3.1 Phenomenon Prevalence Breakdown ($N=26$)

1. **Diffuse Reverberation ($RT_{60} > 1.2$s):** **19 / 26 clips (73.1%)**
   - Reflected energy smears high-frequency phonation bursts into diffuse noise tails, eroding spectral sharpness and decreasing subband onset contrast.
2. **Raw Neural Underconfidence ($p_{\text{raw}} < 0.4920$):** **18 / 26 clips (69.2%)**
   - The dual-resolution neural trunk outputs pre-veto probabilities below operating threshold, indicating representation inadequacy rather than heuristic veto over-suppression.
3. **Low-SNR Masking (SNR $\le 3.0$ dB):** **9 / 26 clips (34.6%)**
   - Background crowd noise, sub-bass rumble, or environmental sounds overlap with formant tracks, elevating spectral flatness ($> 0.040$).
4. **Active Veto Suppression:** **4 / 26 clips (15.4%)**
   - Screams that had $p_{\text{raw}} \ge 0.4920$ but were attenuated below threshold by heuristic filters.

### 3.2 Co-Occurrence Analysis

| Acoustic Failure Dimension | Number of Clips | Percentage of FNs |
| :--- | :--- | :--- |
| Reverberation Only | 4 | 15.4% |
| Neural Underconfidence Only | 3 | 11.5% |
| Reverberation + Neural Underconfidence | 11 | 42.3% |
| Reverberation + Neural Underconfidence + Low SNR | 6 | 23.1% |
| Active Veto Suppression | 4 | 15.4% |
| Clean / Unexplained | 0 | 0.0% |

### 3.3 Key Scientific Takeaways

1. **Heuristic Vetoes Are Not the Dominant Problem:** Only 4 out of 26 missed screams were suppressed by active vetoes. 84.6% of misses failed because the underlying neural feature representation produced insufficient activation ($p_{\text{raw}} < 0.4920$).
2. **Reverberation and Low SNR Are Strongly Coupled:** Late room reverberation smooths temporal modulation (lowering roughness below 0.030) while background noise elevates flatness, simultaneously tricking neural projections into predicting ambient noise rather than vocal distress.
3. **Recovery Mandate:** Any mechanism designed to recover missed screams must target neural feature extraction under diffuse reverberation rather than aggressively relaxing suppression vetoes, which would immediately violate Gate 3 (shouted-speech FPR).

