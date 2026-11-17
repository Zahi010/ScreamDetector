# Stage 8.9.36 — False-Positive Forensics Report

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Target:** All 19 Hard-Negative False Alarms from Candidate D (`MultiPathwayFusionModel`)  
**Data Artifacts:**
- Itemized Forensic Table: `backend/research/stage_8_9_36/evaluation/false_positive_forensics.csv`
- Category Summary Table: `backend/research/stage_8_9_36/evaluation/false_positive_category_summary.csv`

---

## 1. Executive Summary & Category Breakdown

Candidate D incurred **19 false alarms** across the 191 hard negatives in the independent held-out test cohort, yielding an overall Hard-Negative False-Positive Rate of **9.95%** and failing Gate 2 ($\le 5.00\%$).

All 19 false alarms were audited across acoustic properties, source groups, frequency subband distributions, and pathway activations:

| Negative Sound Category | False Positive Count | % of All False Alarms | Mean Candidate D Probability | Mean Baseline Probability | Mean Probability $\Delta$ | Primary Acoustic Driver |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Crowd Chanting & Cheering** | 7 / 42 (16.7% FPR) | **36.8%** | 0.7686 | 0.6558 | **+0.1128** | Multi-talker vocal resonance build-up in $1.5\text{--}3\text{ kHz}$ |
| **Shouted Speech** | 7 / 48 (14.6% FPR) | **36.8%** | 0.7638 | 0.5949 | **+0.1690** | Extreme physiological vocal strain and elevated $F_0$ |
| **Whistles & Squeaks** | 3 / 18 (16.7% FPR) | **15.8%** | 0.7111 | 0.5816 | **+0.1295** | Sharp resonant peaks overlapping scream formants |
| **Sirens & Fireworks** | 1 / 18 (5.6% FPR) | **5.3%** | 0.8426 | 0.0190 | **+0.8236** | Synthetic tonal sweep activating Band 4 head |
| **Infant Crying** | 1 / 15 (6.7% FPR) | **5.3%** | 0.9651 | 0.9854 | -0.0203 | Shorter vocal tract mimicking adult scream physics |
| **Total All Hard Negatives** | **19 / 191 (9.95% FPR)**| **100.0%** | **0.7661** | **0.6074** | **+0.1587** | Overall subband pathway sensitivity gain |

---

## 2. Key Forensic Discoveries

### A. The Subband Pathway's False-Alarm Penalty
A critical forensic discovery emerged when comparing Candidate D with the Stage 8.9.33 Dual-Encoder baseline:
- On 7 of the 19 false alarms, Candidate D's probability was **dramatically higher** than the baseline model ($>+0.20$ probability boost).
- Most notably, in the source group `stage8_9_benjaminharveydesign` (shouted speech):
  - `v2_fsd50k_350446`: Baseline was **0.0125**; Candidate D jumped to **0.4394** (+0.4269).
  - `v2_fsd50k_350451`: Baseline was **0.0520**; Candidate D jumped to **0.5718** (+0.5198).
  - `v2_fsd50k_350448`: Baseline was **0.1413**; Candidate D jumped to **0.4551** (+0.3138).
- **Physical Explanation:** These files contain high-energy speech with strong vocal projection, producing significant energy in Band 4 ($B_4: 2\text{--}3\text{ kHz}$, relative energy $0.206\text{--}0.258$). The subband projection head (Path C), designed to detect scream resonances in Band 4, strongly activated and dragged the fusion MLP logit above the 0.43 decision threshold, converting three previously correct rejections into false alarms.

### B. Siren Sweeps Bypassing the Semantic Filter
- File `v2_fsd50k_335983` (sfx_sirens_fireworks) had a baseline probability of **0.0190** (near-zero).
- Candidate D predicted **0.8426** (+0.8236 jump!).
- **Physical Explanation:** The recording contains a synthesized frequency sweep that dwells momentarily in the 2,500 Hz region with high energy concentration ($B_4$ relative energy $0.285$). While YAMNet correctly recognized it as non-vocal, the subband head produced an overpowering activation that skewed the uncalibrated linear fusion layer.

### C. Persistent Crowd Cheering Overlap (7 False Alarms)
Crowd cheering and chanted vocalizations account for 36.8% of all false alarms:
- When thousands of spectators cheer in a festival environment, the sum of multiple independent voices produces a dense harmonic comb that mimics the spectral envelope of an individual human scream.
- Both the semantic backbone ($P_{\text{base}} = 0.6558$) and the subband head ($P_D = 0.7686$) suffer from this acoustic ambiguity.

### D. Infant Crying (1 False Alarm)
- `v2_fsd50k_9429` triggered an extreme false alarm ($P = 0.9651$ in Candidate D, $P = 0.9854$ in baseline).
- Acoustic inspection reveals that an infant crying sound exhibits fundamental frequencies near 450 Hz, high jitter, and formants directly in Bands 2, 4, and 5. Neither semantic embeddings nor frequency band features alone can separate this without temporal respiration cycle analysis.
