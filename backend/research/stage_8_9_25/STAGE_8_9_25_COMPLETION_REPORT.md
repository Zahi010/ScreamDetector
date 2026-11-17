# STAGE 8.9.25 COMPLETION REPORT: Acoustic Architecture Benchmark & Phonetic Discriminability Research

**Stage Identifier:** 8.9.25  
**System Name:** Festival Scream Detector  
**Stage Category:** Pure Research & Offline Acoustic Benchmarking (Non-Production)  
**Author / Lead:** Senior Audio ML Researcher, Speech-Processing Engineer & Systems Architect  
**Completion Date:** 2026-10-31  
**Target Operational Environment:** Outdoor Festival / Public Venue Scream Alarm Pipeline  
**Production Decision Threshold:** **0.3500** (Strictly Frozen)  
**Production Promotion Status:** **NO CANDIDATE PROMOTED — ALL CANDIDATES REJECTED FOR PRODUCTION**  

---

## 1. Executive Summary

Stage 8.9.25 executed a controlled, leak-free empirical investigation into whether alternative acoustic architectures (Custom 2D CNN, Dilated 1D Temporal CNN, Multimodal Hybrids) and phonetic/vocal-tract resonance features can resolve the fundamental scream-versus-shout confusion barrier identified in Stages 8.9.20 through 8.9.24.

The stage operated strictly under the frozen single-objective charter:
> **Detect human scream-like vocalizations and distinguish them from other sounds, particularly speech-like shouting and other confusing vocal sounds.**

### Key Empirical Findings:
1. **The Monosyllabic Invariance Barrier Confirmed:**
   - On vocalizations under 800 ms, isolated monosyllabic shouting ("NO!", "HEY!", "STOP!") and screams exhibit statistically indistinguishable macroscopic temporal envelope dynamics (Burst Continuity Ratio AUC = 0.6154, Energy Modulation Depth AUC = 0.5280, Vocal Closure Count AUC = 0.5000). At this timescale, screaming and shouting are temporally isomorphic.
2. **Resonance and Phonation Provide Disambiguation:**
   - High-register screams concentrate acoustic energy into the vocal-tract horn resonance band (1.5–3.5 kHz, AUC = 0.7063, $p = 0.0308$) and exhibit elevated Harmonic-to-Noise Ratio (HNR median 28.78 dB vs 14.69 dB in shouts, AUC = 0.7360, $p = 0.0221$).
   - Formant dispersion proxy ($F_{\text{disp}}$) achieves strong separation across the broader cohort (AUC = 0.8356, $p = 1.70 \times 10^{-13}$), but fails in 45.8% of ultra-high pitched screams ($F_0 > 650\text{ Hz}$) where harmonic spacing exceeds vocal tract formant bandwidth.
3. **Architecture Benchmark Results:**
   - **Model B (Custom 2D CNN on Log-Mel Spectrograms)** achieved high precision (89.5%) and ultra-low shouting false alarms (2.38%), but suffered catastrophic under-recall (21.79% overall, 22.73% short screams) because global average pooling across zero-padded fixed windows diluted brief scream activations.
   - **Model C (Temporal 1D Dilated CNN)** showed superior short-event burst recognition using global max-pooling (81.82% short scream recall, 10.71% shouting FPR) at tiny computational cost (22.6k parameters, 3.1 ms P95 latency).
   - **Model E (Hybrid Multimodal Model)** achieved the highest discrimination overall: ROC-AUC = 0.9371, Short-Scream Recall = 90.91% (passing the short-scream gate $\ge 90\%$), Overall Scream Recall = 80.77%, and Shouting FPR = 15.48%.
4. **Acceptance Gate Verdict:**
   - The required production acceptance gates are: Overall Event Recall $\ge 96.0\%$, Hard-Negative FPR $\le 5.0\%$, Shouting FPR $\le 15.0\%$, Short-Scream Recall $\ge 90.0\%$, and Computational P95 $\le 25.0\text{ ms}$.
   - While Model E passed the short-scream gate (90.91%) and latency gate (21.3 ms), it achieved 80.77% overall recall (gate $\ge 96\%$) and 5.47% hard-negative FPR (gate $\le 5\%$).
   - Therefore, **ALL CANDIDATES (Models A through F) ARE MARKED: REJECTED — RESEARCH ONLY**.
   - No production artifacts were modified, and the production classifier remains 100% untouched.

---

## 2. Research Questions and Empirical Answers

### RQ1: Does a custom 2D CNN trained on Log-Mel spectrograms capture scream-specific acoustic information?
**Answer: Yes, but with severe context-window trade-offs.**  
A compact 3-layer 2D CNN ($64 \times 128$ Log-Mel, 25,857 parameters) attained an ROC-AUC of 0.9027 and reduced shouting false-positive rate to 2.38% (2/84). However, when evaluated at the fixed production threshold of 0.3500, overall recall collapsed to 21.79% (17/78). Global average pooling across 1.0-second windows inherently dilutes short scream bursts with padded background.

### RQ2: Do temporal CNNs learn useful vocal dynamics beyond handcrafted temporal features?
**Answer: Yes, particularly for onset bursts.**  
Model C (Dilated 1D CNN with dilations 1, 2, 4 and global max-pooling) achieved 70.51% recall and 81.82% short-scream recall while keeping shouting FPR at 10.71% (9/84). Dilated receptive fields of 300 ms naturally match the rise time of scream onset bursts without requiring manual syllabic segmentation.

### RQ3: Does combining pretrained YAMNet representations with custom acoustic features improve discrimination?
**Answer: Yes, decisively.**  
Feature ablation revealed that fusing YAMNet max-pooled embeddings with temporal CNN probabilities and handcrafted phonetic/resonance features (Model E) raised ROC-AUC from 0.8874 (Baseline Model A) to 0.9371 (Model E), and boosted short-scream recall from 77.27% to 90.91%. Removing handcrafted phonetic features caused short-scream recall to plummet back to 81.82%.

### RQ4: Do phonetic and resonance characteristics distinguish short screams from monosyllabic shouts ("NO!", "HEY!")?
**Answer: Yes, but only spectral envelope and resonance features succeed; temporal metrics completely fail.**  
Mann-Whitney U tests showed that while burst continuity and modulation depth have $p > 0.20$ (invariant), Horn Resonance Ratio ($p = 0.0308$) and Harmonic-to-Noise Ratio ($p = 0.0221$) provide statistically significant separation.

### RQ5: Do improvements generalize to independent recordings and unseen speakers or sources?
**Answer: Yes.**  
Evaluation on the 142 completely isolated test source groups (zero overlap with the 669 training groups and 144 validation groups) confirmed that Model E maintains its superior ROC-AUC (0.9371) without catastrophic overfitting.

---

## 3. Dataset Integrity and Leakage Prevention Audit

A comprehensive source-group isolation audit was executed using SHA-256 file content hashing across all 2,804 repository recordings:

```
Total Active Repository Recordings: 2,804 files (100% on disk)
Split Cardinality:
  - Train: 1,969 recordings (669 source groups)
  - Validation: 373 recordings (144 source groups)
  - Test: 462 recordings (142 source groups)
```

### Audit Verification Metrics:
- **Cross-Split Source Group Leakage:** **0 source groups (0.00%)**.
- **Cross-Split Audio Content Hash Duplicates:** **0 files (0.00%)**.
- **Historical Stage 5 Test Isolation:** Maintained without modification; no tuning or fitting performed on test cohorts.
- **License Breakdown:** 37.9% commercially permissible (CC-BY, CC0, OpenSLR); 62.1% non-commercial research (CC-BY-NC).

---

## 4. Architecture Benchmark Results (Models A through F)

All models were evaluated on the exact same held-out test cohort ($N=462$: 78 Screams, 384 Hard Negatives including 84 Shouts, 56 Cheering, 17 Whistles/Sirens, 31 Music, 196 Ambient Noise) at the frozen production decision threshold of **0.3500**.

### 4.1 Comparative Architecture Benchmark Matrix

| Architecture Candidate | Overall Recall ($N=78$) | Hard-Neg FPR ($N=384$) | Shouting FPR ($N=84$) | Short Scream Recall ($N=22$) | Cheering FPR ($N=56$) | Whistle FPR ($N=17$) | ROC-AUC | PR-AUC | P95 Latency | Params | Gate Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Model A: Frozen YAMNet Baseline** | 64.10% (50/78) | 6.25% (24/384) | 17.86% (15/84) | 77.27% (17/22) | 5.36% (3/56) | 5.88% (1/17) | 0.8874 | 0.6305 | 16.4 ms | 3.40M | **REJECTED** |
| **Model B: Custom 2D CNN (Log-Mel)** | 21.79% (17/78) | 0.52% (2/384) | 2.38% (2/84) | 22.73% (5/22) | 0.00% (0/56) | 0.00% (0/17) | 0.9027 | 0.7197 | 5.2 ms | 25.8k | **REJECTED** |
| **Model C: Temporal 1D Dilated CNN** | 70.51% (55/78) | 3.65% (14/384) | 10.71% (9/84) | 81.82% (18/22) | 1.79% (1/56) | 17.65% (3/17) | 0.9015 | 0.6694 | 3.1 ms | 22.6k | **REJECTED** |
| **Model D: YAMNet + Temporal 1D CNN** | 75.64% (59/78) | 4.95% (19/384) | 15.48% (13/84) | 81.82% (18/22) | 5.36% (3/56) | 11.76% (2/17) | 0.9291 | 0.7110 | 17.8 ms | 3.42M | **REJECTED** |
| **Model E: Hybrid Multimodal Model** | **80.77% (63/78)** | **5.47% (21/384)** | **15.48% (13/84)** | **90.91% (20/22)** | 5.36% (3/56) | 11.76% (2/17) | **0.9371** | 0.6937 | 21.3 ms | 3.45M | **REJECTED** |
| **Model F: Candidate G Reference** | 80.77% (63/78) | 5.99% (23/384) | 15.48% (13/84) | 86.36% (19/22) | 5.36% (3/56) | 5.88% (1/17) | 0.8739 | **0.7864** | **2.42 ms** | 3.44M | **REJECTED** |

*(Note: Target acceptance gates require: Recall $\ge 96.0\%$, Hard-Neg FPR $\le 5.0\%$, Shouting FPR $\le 15.0\%$, Short-Scream Recall $\ge 90.0\%$, P95 Latency $\le 25.0\text{ ms}$.)*

---

## 5. Feature Ablation Analysis (Model E Deconstruction)

To determine the exact contribution of each feature family within Model E, controlled systematic ablations were conducted on the held-out test split:

| Ablation Condition | Configuration Description | Overall Recall | Hard-Neg FPR | Shouting FPR | Short Scream Recall | Delta vs Full Model E |
|---|---|---|---|---|---|---|
| **E0: Full Hybrid** | Complete Multimodal (YAMNet + LogMel + Temp + Phonation) | **80.77%** | **5.47%** | **15.48%** | **90.91%** | Baseline reference |
| **E1: No Phonation** | Ablate 32-dim acoustic & resonance features | 76.92% | 5.47% | 16.67% | 81.82% | **-9.09% Short Scream Recall** |
| **E2: No CNN Branches**| Ablate Log-Mel 2D CNN & Temporal 1D CNN | 70.51% | 8.59% | 21.43% | 72.73% | **+5.95% Shouting FPR, -10.26% Recall** |
| **E3: No YAMNet** | Custom CNNs + Phonation alone (No pretrained backbone) | 69.23% | 4.43% | 11.90% | 86.36% | **-11.54% Recall; Low FPR (4.43%)** |
| **E4: YAMNet Alone** | Simple YAMNet Max-Pool Logistic Regression | 67.95% | 6.25% | 20.24% | 77.27% | **-12.82% Recall, +4.76% Shouting FPR** |

### Key Takeaways from Ablation:
- **Phonetic & Resonance features are critical for short screams:** Ablating them directly drops short-scream recall by 9.09% (from 90.91% to 81.82%).
- **Temporal & 2D CNN branches protect against speech shouting:** Removing them inflates shouting FPR from 15.48% to 21.43%.
- **Pretrained YAMNet backbone is essential for overall coverage:** Without YAMNet, recall drops below 70%, proving that lightweight custom CNNs trained from scratch on small datasets lack generalized acoustic priors.

---

## 6. Phonetic and Resonance Discriminability Findings

### 6.1 The Monosyllabic Invariance Barrier
On short vocalizations ($< 800\text{ ms}$), monosyllabic shouts ("NO!", "HEY!", "STOP!") share identical envelope burst characteristics with short screams:
- `Burst_Continuity_Ratio`: Screams median 1.000 vs Monosyllabic shouts median 0.963 ($p = 0.219$).
- `Energy_Modulation_Depth`: Screams median 1.831 vs Monosyllabic shouts median 1.827 ($p = 0.798$).
- `Vocal_Closure_Gap_Count`: Both median 0.000 ($p = 1.000$).

### 6.2 Separable Resonance Features
- **Horn Resonance Band (1.5–3.5 kHz Ratio):** Screams median 0.482 vs Monosyllabic shouts median 0.381 (AUC = 0.7063, $p = 0.0308$).
- **Harmonic-to-Noise Ratio (HNR):** Screams median 28.78 dB vs Monosyllabic shouts median 14.69 dB (AUC = 0.7360, $p = 0.0221$).
- **Formant Dispersion Proxy ($F_{\text{disp}}$):** Across all screams vs shouts, $F_{\text{disp}}$ separates with AUC = 0.8356 ($p = 1.70 \times 10^{-13}$). However, in 45.8% of ultra-high pitched screams ($F_0 > 650\text{ Hz}$), LPC formant tracking fails because fundamental frequency spacing exceeds vocal tract formant bandwidth.

---

## 7. Short-Scream Analysis Summary

Across the 78 test screams stratified by duration:
- **200–500 ms ($N=8$):** Model E achieved 87.5% recall (7/8). Model B achieved only 62.5% (5/8) due to zero-padding dilution.
- **500–800 ms ($N=14$):** Model E achieved 92.9% recall (13/14).
- **Combined Short Screams ($< 800\text{ ms}$, $N=22$):** Model E achieved **90.91% recall (20/22)**, successfully satisfying the Short-Scream Acceptance Gate ($\ge 90.0\%$).
- **Receptive Field Finding:** Convolutional networks operating on short vocal bursts must use **Global Max-Pooling** or attention pooling. Global Average Pooling (GAP) penalizes short events by averaging activations over padded silence.

---

## 8. Latency and Computational Resource Assessment

Benchmarked on CPU (Windows 11, Intel i7 single-thread equivalent, 100 timed iterations after 500 warmup runs):

| Candidate Architecture | Input Representation | Median Latency | P95 Latency | P99 Latency | RAM Working Set | Gate Status ($\le 25\text{ ms}$) |
|---|---|---|---|---|---|---|
| **Model A: YAMNet Baseline** | Audio Buffer (0.975s) | 14.1 ms | 16.4 ms | 18.2 ms | 65.0 MB | **PASSED** |
| **Model B: Custom 2D CNN** | Log-Mel Spectrogram | 3.8 ms | 5.2 ms | 6.8 ms | 28.0 MB | **PASSED** |
| **Model C: Temporal 1D CNN** | Feature Sequence (70x16) | 2.1 ms | 3.1 ms | 4.2 ms | 22.0 MB | **PASSED** |
| **Model D: YAMNet + T-CNN** | YAMNet Embed + Seq | 15.2 ms | 17.8 ms | 20.1 ms | 72.0 MB | **PASSED** |
| **Model E: Hybrid Multimodal**| Multimodal Buffer | 17.5 ms | 21.3 ms | 24.5 ms | 85.0 MB | **PASSED** |
| **Model F: Candidate G** | Dual-Pathway Features | 1.96 ms | 2.42 ms | 2.91 ms | 42.0 MB | **PASSED** |

---

## 9. Limitations

1. **Context Accumulation Latency vs Computational Latency:** While all models achieved computational P95 latency $< 25\text{ ms}$, models relying on 1.0–1.5 second windows require context accumulation buffers, introducing an operational alert delay of 500–1500 ms for sustained screams.
2. **High-Pitch Phonation Breakdown:** LPC-based formant estimation and autocorrelation pitch trackers break down when vocalizations exceed $F_0 > 650\text{ Hz}$. Robust spectral peak tracking must be developed to replace LPC formants in high-frequency vocal shrieks.
3. **Small Sample Size for Monosyllabic Shouts:** The held-out test split contains 13 isolated monosyllabic shouting files. While statistically significant differences were observed in HNR and horn resonance, a larger targeted cohort of isolated shout commands ("FIRE!", "STOP!", "HELP!") is recommended.

---

## 10. Acceptance Gate Assessment

| Evaluation Metric | Target Gate Requirement | Model A | Model B | Model C | Model D | Model E | Model F | Gate Compliance |
|---|---|---|---|---|---|---|---|---|
| **Overall Scream Recall** | $\ge 96.0\%$ | 64.10% | 21.79% | 70.51% | 75.64% | 80.77% | 80.77% | **ALL FAILED** |
| **Hard-Negative FPR** | $\le 5.0\%$ | 6.25% | 0.52% | 3.65% | 4.95% | 5.47% | 5.99% | Model B, C, D Passed; A, E, F Failed |
| **Shouted-Speech FPR** | $\le 15.0\%$ | 17.86% | 2.38% | 10.71% | 15.48% | 15.48% | 15.48% | Model B, C Passed; A, D, E, F Failed |
| **Short-Scream Recall** | $\ge 90.0\%$ | 77.27% | 22.73% | 81.82% | 81.82% | **90.91%** | 86.36% | **Model E Passed**; Others Failed |
| **End-to-End P95 Latency**| $\le 25.0\text{ ms}$ | 16.4 ms | 5.2 ms | 3.1 ms | 17.8 ms | 21.3 ms | 2.42 ms | **ALL PASSED** |
| **FINAL GATE STATUS** | **All 5 Gates Required** | **REJECTED** | **REJECTED** | **REJECTED** | **REJECTED** | **REJECTED** | **REJECTED** | **RESEARCH ONLY** |

---

## 11. Production Integrity Verification

All 4 authoritative production files and metadata were checked via cryptographic SHA-256 verification and confirmed 100% untouched:

- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f` (VERIFIED)
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60` (VERIFIED)
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d` (VERIFIED)
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2` (VERIFIED)
- **Production Threshold:** Maintained strictly at **0.3500**.

---

## 12. Strategic Recommendations for Stage 8.9.26

Based on the empirical breakthroughs and boundaries uncovered in Stage 8.9.25, Stage 8.9.26 should focus on:

1. **Dual-Pathway Asymmetric Fusion:**
   - Deploy a high-sensitivity, fast-receptive-field branch (Model C Temporal Dilated CNN, 300 ms receptive field) to detect rapid scream onsets and guarantee $\ge 90\%$ short-scream recall.
   - Deploy an asymmetric slow branch (Candidate G TMSCV + Model E Horn Resonance) that is strictly permitted to suppress multi-syllabic speech shouting when cadence evidence ($\ge 2$ closure gaps, $3\text{–}5\text{ Hz}$ modulation) is statistically established.
2. **Rejection of Global Average Pooling for Spectrogram CNNs:**
   - Future 2D audio CNNs must utilize **Global Max-Pooling** or **Attention-Weighted Pooling** to prevent zero-padding from suppressing short scream activations.
3. **High-Frequency Spectral Peak Tracking:**
   - Replace standard LPC formant tracking with non-parametric spectral peak prominence within the 1.5–3.5 kHz scream horn to bypass harmonic spacing failures on female and child shrieks ($F_0 > 650\text{ Hz}$).

---

*Report Approved by: Senior Audio ML Researcher & Speech Processing Systems Architect*  
*Stage 8.9.25 Independent Research Audit*
