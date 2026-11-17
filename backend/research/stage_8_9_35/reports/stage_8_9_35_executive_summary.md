# Stage 8.9.35 — Executive Summary Report

**Stage:** 8.9.35 — Spatial Audio Research, Frequency-Subband Discrimination & Multi-Pathway Fusion  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Auditor / Roles:** Principal Acoustic AI Researcher, Senior Audio ML Engineer, DSP Specialist, Independent Validation Auditor  
**Production Status:** STRICTLY FROZEN (Production Threshold 0.3500)  
**Final Determination:** **REJECTED FOR PRODUCTION — RESEARCH ONLY**  

---

## 1. Project Background and Research Mission

The primary objective of Stage 8.9.35 was to investigate whether spatial audio representations and frequency-subband decomposition can simultaneously advance scream detection recall and specificity to satisfy all five predefined acceptance gates on the authoritative independent held-out test cohort ($N=293$, 102 screams, 191 hard negatives across 111 source groups).

### Predefined Acceptance Gates:
1. **Gate 1: Overall Scream Recall** $\ge 96.00\%$
2. **Gate 2: Hard-Negative False-Positive Rate (HN-FPR)** $\le 5.00\%$
3. **Gate 3: Shouted-Speech False-Positive Rate (Shout-FPR)** $\le 15.00\%$
4. **Gate 4: Short-Scream Recall (<1.0s duration)** $\ge 90.00\%$
5. **Gate 5: Computational P95 Inference Latency** $\le 25.00\text{ ms}$

---

## 2. Key Checkpoint Accomplishments

### Checkpoint 1: Reproduction & Hardware Spatial Audit
- Re-verified Stage 8.9.34 baseline metrics on $N=293$: Dual-Encoder Recall 82.35%–84.31%, HN-FPR 6.28%–7.85%, Shout-FPR 8.33%, P95 18.57 ms.
- Audited physical edge hardware: Confirmed a single INMP441 omnidirectional I2S microphone (1 mono channel). Physical beamforming is physically impossible on single-microphone hardware without adding a physical array ($N \ge 2$).
- Audited corpus channels: All 1,328 audio files in the festival corpus (and 100% of the 293 test files) are monophonic (1 channel, 16 kHz).
- **Audit Decision:** Physical spatial performance on the empirical cohort is classified as **NOT EVALUABLE**. Synthetic data was strictly prohibited from being mixed into the empirical evaluation.

### Checkpoint 2: Frequency-Subband Decomposition & Feature Extraction
- Designed and extracted 6 discrete frequency subbands using 4th-order digital Butterworth IIR bandpass filters (SOS topology) across all 1,328 recordings in the corpus:
  - $B_1$ (300–800 Hz), $B_2$ (800–1.5 kHz), $B_3$ (1.5–2 kHz), $B_4$ (2–3 kHz), $B_5$ (3–4 kHz), $B_6$ (4–6 kHz).
- Extracted an 11-dimensional feature vector capturing relative band energies, temporal variances, scream ratios, and whistle ratios (`subband_feature_analysis.csv`).
- **Acoustic Findings:**
  - Screams exhibit dominant resonance in 800–1,500 Hz (46.2%) and 2,000–3,000 Hz (11.0%), producing a high $(B_4+B_5)/B_1$ ratio (30.56) compared to cheering (0.28) and shouting (0.38).
  - Infant crying mirrors scream physics in static frequency spectra (ratio 28.79), confirming that frequency analysis alone cannot distinguish infant crying from human screams without temporal cycle tracking.

### Checkpoint 3: Track B Controlled Spatial Simulation
- Simulated a 2-element linear MEMS array ($d = 50\text{ mm}$) with GCC-PHAT TDoA/DOA estimation and Delay-and-Sum beamforming under competing talker and diffuse crowd conditions.
- Achieved $+2.1\text{ dB}$ to $+2.7\text{ dB}$ array SNR enhancement at positive SNRs.
- Discovered that at $-5\text{ dB}$ SNR, phase instability causes a **22.5% risk of false steering**, where Delay-and-Sum beamforming places the actual scream into a spatial null, attenuating it by $-1.8\text{ dB}$ to $-3.4\text{ dB}$.

### Checkpoint 4 & 5: Multi-Pathway Architecture & Training
- Built and trained **`MultiPathwayFusionModel` (Candidate D)** fusing:
  - Path A: 1024-d YAMNet embeddings $\to$ 128-d $L_2$ unit-norm vector.
  - Path B: 6-d Phonation features + 6-d missingness mask $\to$ 32-d $L_2$ unit-norm vector.
  - Path C: 11-d Frequency Subband vector $\to$ 16-d $L_2$ unit-norm vector.
  - Multimodal MLP Head: 176-d $\to$ 64 $\to$ 1 logit output.
- Optimized using combined Binary Cross-Entropy and Supervised Contrastive Loss ($\lambda = 0.30$).
- Froze validation operating threshold at **$\theta^* = 0.43$** based strictly on validation split tuning.

### Checkpoint 6: Independent Evaluation & Performance Audit
- Evaluated Candidate D on the authoritative held-out test cohort ($N=293$):
  - **Scream Recall:** 89.22% (91/102) — Best recall achieved to date (+6.87% over baseline).
  - **Hard-Negative FPR:** 9.95% (19/191) — Increased by +3.67% over baseline due to sensitivity to cheering/shouting harmonics.
  - **Shouted-Speech FPR:** 14.58% (7/48) — Satisfies Gate 3 ($\le 15.00\%$).
  - **Short-Scream Recall:** 100.00% (5/5) — Satisfies Gate 4 numerically, but flagged as statistically under-sampled ($N=5$).
  - **Computational P95:** 19.31 ms — Satisfies Gate 5 ($\le 25.00\text{ ms}$).
  - **Multi-Stream Concurrency:** Zero 100 ms audio-hop deadline misses across 1, 2, 4, and 8 concurrent streams.

---

## 3. Predefined Acceptance Gate Scorecard

| Gate | Criterion | Target Threshold | Measured Result | Verdict |
| :---: | :--- | :---: | :---: | :---: |
| **1** | Overall Scream Recall | $\ge 96.00\%$ | **89.22% (91/102)** | **FAIL** |
| **2** | Hard-Negative FPR | $\le 5.00\%$ | **9.95% (19/191)** | **FAIL** |
| **3** | Shouted-Speech FPR | $\le 15.00\%$ | **14.58% (7/48)** | **PASS** |
| **4** | Short-Scream Recall | $\ge 90.00\%$ | **100.00% (5/5)\*** | **PASS\*** |
| **5** | Computational P95 | $\le 25.00\text{ ms}$ | **19.31 ms** | **PASS** |

*\*Statistically limited sample size ($N=5$).*

---

## 4. Production Integrity Verification

All four frozen production artifacts remain 100% byte-for-byte immutable:
- `backend/models/scream_classifier.joblib`: `ad6e428d05d2359da73b6dee7cfdcec646c87390b496b59cad5f46b5a452851f`
- `backend/models/model_metadata.json`: `30c1c75d81ad61b1d0cacb70b221d034840888c7bfede949a15d47b139699f60`
- `backend/reports/test_predictions.csv`: `e93be4550f97fe2cfe6bc0f2366650833d96f284c45cd1eb6026fba0db98449d`
- `backend/reports/stage5_test_evaluation.md`: `9e55b1f574e18bc4623a871d58926fefccd29f4c4e3ee22010a4a54a4e4cd1d2`

---

## 5. Authoritative Final Determination

Because Candidate D (`MultiPathwayFusionModel`) failed Gate 1 (89.22% vs. $\ge 96.00\%$) and Gate 2 (9.95% vs. $\le 5.00\%$), it cannot be promoted to production.

The official final determination is:

### **REJECTED FOR PRODUCTION — RESEARCH ONLY**
