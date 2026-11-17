# Stage 8.9.36 — False-Negative Forensics Report

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Target:** All 11 Missed Screams (False Negatives) from Candidate D (`MultiPathwayFusionModel`)  
**Data Artifact:** `backend/research/stage_8_9_36/evaluation/false_negative_forensics.csv`  

---

## 1. Forensic Executive Summary

Candidate D achieved 89.22% scream recall on the independent held-out test cohort, detecting 91 out of 102 genuine screams, but failing Gate 1 ($\ge 96.00\%$) by missing exactly **11 recordings**.

Rather than randomly sampling, every single one of the 11 missed screams was audited acoustically, physically, and metadata-wise. 100% of the raw audio waveforms were retrieved and analyzed.

### **High-Level Forensic Categorization:**
1. **Distant & Masked Screams in Low SNR (45.5%, 5/11):** Screams embedded in heavy crowd chatter, cheering, or music where signal-to-noise ratio is $\le +3\text{ dB}$ (down to $-6\text{ dB}$).
2. **Ground-Truth Label Anomalies (18.2%, 2/11):** Non-scream vocalizations ("gasp" and "surprised oooh") erroneously labeled as screams in the dataset.
3. **Low-Intensity & Long Muffled Files (27.3%, 3/11):** Very low-amplitude screams ($\text{RMS} < 0.05$) or lengthy recordings (8.0s) where a brief scream is diluted by excessive silence.
4. **Borderline Threshold Miss (9.1%, 1/11):** Moderate scream that generated $P = 0.3543$, passing under historical threshold 0.3500 but falling just below validation threshold 0.4300.

---

## 2. Itemized Forensic Ledger of All 11 False Negatives

| Recording ID | Source Group | Duration | RMS Energy | Est. SNR | Pred Prob | Primary Forensic Category | Acoustic Evidence & Failure Mechanism |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `v2_synth_scream_028_snr-06db` | `nigens_saraonsins` | 2.27s | 0.0941 | $-6\text{ dB}$ | 0.0499 | **Low-SNR Noise Masking** | Severe negative SNR ($-6\text{ dB}$). Diffuse festival crowd noise completely submerges harmonic structure in Bands 4–5 ($2\text{--}4\text{ kHz}$). |
| `v3_synth_scream_012_snr-03db` | `nigens_sangtao` | 1.09s | 0.1647 | $-3\text{ dB}$ | 0.3972 | **Low-SNR Masking & Borderline** | Negative SNR ($-3\text{ dB}$). Achieved $P = 0.3972$; detected under historical $\theta=0.35$, but missed at $\theta^*=0.43$. |
| `v3_synth_scream_018_snr+00db` | `openslr_speaker_7IOA`| 3.41s | 0.1960 | $0\text{ dB}$ | 0.0768 | **Low-SNR Noise Masking** | Noise floor equals scream energy ($0\text{ dB}$). Masked F0 and suppressed subband ratio ($B_4/B_1 = 0.82$). |
| `v3_synth_scream_019_snr+03db` | `openslr_speaker_GZAE`| 2.20s | 0.2346 | $+3\text{ dB}$ | 0.2906 | **Moderate Noise Masking** | Moderate SNR ($+3\text{ dB}$). Competing crowd cheering elevates Band 1 energy, suppressing the scream ratio. |
| `v3_synth_scream_029_snr+03db` | `openslr_speaker_QLQX`| 2.35s | 0.0577 | $+3\text{ dB}$ | 0.1184 | **Moderate Noise Masking** | Quiet female scream mixed at $+3\text{ dB}$ SNR with low peak amplitude ($0.21$). |
| `v2_nigens_242607__reitanna__gasp-oooh` | `nigens_reitanna` | 1.32s | 0.3683 | Clean | 0.0407 | **Label Anomaly (Non-Scream)** | **Clear ground-truth labeling defect.** Audio is a soft gasp / sigh from artist Reitanna. Fundamental frequency is only 185 Hz; zero scream turbulence or strain. |
| `v2_nigens_242644__reitanna__another-surprised-oooh` | `nigens_reitanna` | 1.50s | 0.4362 | Clean | 0.0273 | **Label Anomaly (Non-Scream)** | **Clear ground-truth labeling defect.** Audio is a theatrical "oooh" of surprise. No screaming characteristics; correctly rejected by model as non-scream. |
| `v3_fsd50k_9433` | `fsd50k_uploader_thanvannispen` | 2.00s | 0.2590 | Clean | 0.3543 | **Borderline Threshold Miss** | Clean scream with moderate vocal strain. Model predicted $P = 0.3543$; detected at historical $\theta=0.35$, but missed at $\theta^*=0.43$. |
| `v2_openslr_QLQX_15_15_0_19_0_0_0` | `openslr_speaker_QLQX` | 2.35s | 0.0469 | Clean | 0.1571 | **Low-Intensity Muffled Vocal**| Low-amplitude recording ($\text{RMS} = 0.0469$, peak $0.18$). Muffled acoustics prevent high-frequency harmonic propagation. |
| `v3_fsd50k_29849` | `fsd50k_uploader_thanvannispen` | 8.00s | 0.0810 | Clean | 0.0149 | **Silence Dilution in Long Audio**| 8.0-second file containing a 0.6s scream followed by 7.4s of quiet room tone. Global temporal average pooling in YAMNet dilutes the 0.6s burst. |
| `v3_fsd50k_166621` | `fsd50k_uploader_j.zazvurek` | 2.02s | 0.2048 | Clean | 0.0297 | **Atypical Theatrical Vocalization**| High-pitched stylized voice effect with synthetic flutter and echo, confusing the phonation head. |

---

## 3. Key Forensic Insights & Systematic Failure Patterns

### A. The Severe-Noise Barrier (5/11 Misses)
In real-world festival conditions, when ambient crowd/music noise approaches or exceeds the acoustic energy of a scream ($\text{SNR} \le +3\text{ dB}$), standard spectral representations break down.
- The high-frequency scream resonances ($B_4: 2\text{--}3\text{ kHz}$ and $B_5: 3\text{--}4\text{ kHz}$) are overwhelmed by the broadband noise floor.
- At the same time, ambient bass and crowd chatter elevate Band 1 ($300\text{--}800\text{ Hz}$), causing the $\frac{B_4+B_5}{B_1}$ ratio to collapse from $>20$ down to $<1.5$.
- As a result, the model cannot distinguish the masked scream from background noise without specialized noise-suppression pre-filtering.

### B. Dataset Labeling Defects (2/11 Misses)
Two of the missed screams are **not genuine screams**:
- Both originate from Freesound uploader `reitanna` (`gasp-oooh` and `another-surprised-oooh`).
- Acoustic inspection verifies that these are mild vocal gasps and theatrical sigh sounds.
- **The model was acoustically correct in rejecting them.** If these two mislabeled files were removed from the test cohort, Candidate D's true positive rate would be **91 / 100 = 91.00%**.

### C. Silence Dilution in Long Files (1/11 Misses)
`v3_fsd50k_29849` is 8.0 seconds long, but the scream occurs for only 600 ms.
- Because the evaluation pipeline computed global average pooling across all YAMNet frames, the 7.4 seconds of silence diluted the 0.6s scream embedding, dropping the probability to $0.0149$.
- **Architectural Remedy:** Using max-pooling over sliding temporal windows rather than mean-pooling across whole files would directly solve this failure mode.
