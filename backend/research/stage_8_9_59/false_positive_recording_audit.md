# False-Positive Recording Audit — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase C of Stage 8.9.59, an audit was conducted into the false-positive classifications produced on the validation cohort (`expansion_val`, $N=212$ hard negatives).

Under frozen Candidate E1 + C5 ($\theta = 0.6800$):
- **Total False Positives:** Exactly **13 / 212 (6.13% FPR)** (compared to 11 / 212 = 5.19% FPR reported for historical Candidate B).
- **Category Breakdown:**
  - **Shouted Speech:** **10 / 88 (11.36% FPR)** (historical Candidate B: 9 / 88 = 10.23% FPR).
  - **Infant Crying:** **2 / 20 (10.00% FPR)** (historical Candidate B: 0 / 20 = 0.00% FPR).
  - **Crowd Cheering / Chanting:** **1 / 37 (2.70% FPR)** (historical Candidate B: 1 / 37 = 2.70% FPR).
  - **Referee Whistles & Squeaks:** **0 / 22 (0.00% FPR)** (Candidate E1 completely rejects all 22 whistles; Candidate B without Intervention D failed 1 / 22).
  - **General Environmental Noise:** **0 / 36 (0.00% FPR)**.
  - **Emergency Sirens & SFX:** **0 / 9 (0.00% FPR)**.

---

## 2. Complete Inventory of False-Positive Recordings ($N=13$)

| # | Recording ID | Category | Subtype | Duration | C5 Prob | Excess ($p - \theta$) | Source Group ID | Root Cause Pattern |
|:---:|---|---|---|:---:|:---:|:---:|---|---|
| 1 | `exp_v2_fsd50k_343872` | `shouting_and_speech` | SUSTAINED | 1.45s | 0.9240 | +0.2440 | `exp_sg_stage8_9_reitanna` | Aggressive sustained shouting with phonatory strain |
| 2 | `exp_v2_fsd50k_343952` | `shouting_and_speech` | SUSTAINED | 1.80s | 0.9410 | +0.2610 | `exp_sg_stage8_9_reitanna` | Borderline scream-shout vocalization; extreme vocal fry |
| 3 | `exp_v2_fsd50k_343955` | `shouting_and_speech` | SUSTAINED | 1.60s | 0.9028 | +0.2228 | `exp_sg_stage8_9_reitanna` | Theatrical vocal projection with high subband energy |
| 4 | `exp_v2_fsd50k_343960` | `shouting_and_speech` | SHORT | 0.85s | 0.7053 | +0.0253 | `exp_sg_stage8_9_reitanna` | Transient vocal exclamation; elevated F0 standard deviation |
| 5 | `exp_v2_fsd50k_343965` | `shouting_and_speech` | SUSTAINED | 2.10s | 0.9810 | +0.3010 | `exp_sg_stage8_9_reitanna` | Severe vocal over-blowing; acoustic chaos near scream boundary |
| 6 | `exp_v2_fsd50k_344030` | `infant_crying` | SUSTAINED | 2.40s | 0.7079 | +0.0279 | `exp_sg_fsd50k_uploader_4412` | High F0 wailing (>500 Hz) with periodic roughness |
| 7 | `exp_v2_fsd50k_220823` | `shouting_and_speech` | SHORT | 0.90s | 0.9980 | +0.3180 | `exp_sg_fsd50k_uploader_ericsueiro` | High-effort performance shouting line ("Hey! Stop!") |
| 8 | `exp_v2_fsd50k_80479` | `infant_crying` | SUSTAINED | 1.95s | 0.7012 | +0.0212 | `exp_sg_fsd50k_uploader_1892` | Distressed infant cry; scream band energy concentration |
| 9 | `exp_v2_fsd50k_168725` | `shouting_and_speech` | SUSTAINED | 1.70s | 0.8810 | +0.2010 | `exp_sg_fsd50k_uploader_11linda` | Loud athletic cheering/shouting; high acoustic intensity |
| 10 | `exp_v2_fsd50k_220822` | `shouting_and_speech` | SHORT | 0.75s | 0.8960 | +0.2160 | `exp_sg_fsd50k_uploader_ericsueiro` | Transient shouted command; rapid pitch rise |
| 11 | `exp_v3_fsd50k_361225` | `crowd_chant_cheering` | SUSTAINED | 3.20s | 0.8356 | +0.1556 | `exp_sg_fsd50k_uploader_9910` | High-pitched stadium cheering; harmonic energy cluster in Band 3 |
| 12 | `exp_v3_fsd50k_220817` | `shouting_and_speech` | SUSTAINED | 1.50s | 0.9570 | +0.2770 | `exp_sg_fsd50k_uploader_ericsueiro` | Overdriven theatre vocal shouting; vocal tract non-linearity |
| 13 | `exp_v3_fsd50k_220818` | `shouting_and_speech` | SHORT | 0.80s | 0.8784 | +0.1984 | `exp_sg_fsd50k_uploader_ericsueiro` | Shouted performance line; elevated jitter and spectral centroid |

---

## 3. Acoustic Analysis Across Negative Subtypes

### 3.1 Shouted Speech ($10 / 88$ False Positives)
Shouted speech is the dominant false-positive driver ($76.9\%$ of all false alarms). Acoustic inspection confirms that the detector does NOT trigger on normal conversational speech (FPR on conversational speech is $0.0\%$). False positives occur exclusively when speakers push their vocal apparatus into extreme vocal effort, generating:
- Formant elevation above $1,500\text{ Hz}$.
- Subband energy concentration in Band 3 (2000–4000 Hz) resembling scream phonation.
- Acoustic roughness / vocal fry mimicking deterministic chaos.

### 3.2 Infant Crying ($2 / 20$ False Positives)
Infant crying is biologically structured around very high fundamental frequencies ($F_0 \approx 450–700\text{ Hz}$), which is significantly higher than adult speech ($100–250\text{ Hz}$) and approaches adult scream pitch. When infants wail in distress, vocal tract instability produces elevated jitter and subband energy that trigger the detector just above the threshold ($p = 0.701$ and $p = 0.708$ vs $\theta = 0.6800$).

### 3.3 Cheering & Crowd Chanting ($1 / 37$ False Positives)
Only 1 clip triggered: `exp_v3_fsd50k_361225` ($p = 0.836$). This recording features intense high-pitch female cheering bursts in a sports arena. The remaining 36 cheering files were correctly rejected ($97.3\%$ true negative rate).

### 3.4 Whistle Rejection ($0 / 22$ False Positives)
Candidate E1 + C5 achieved **100.0% true negative rejection on referee whistles and squeaks** (0 false alarms out of 22 clips). Candidate E1’s subband DSP successfully differentiates narrow-band whistle tones from wideband chaotic scream phonation without requiring an external veto module.

---

## 4. Preservation & Traceability

Full per-recording metrics are preserved in [`false_positive_recordings.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/false_positive_recordings.csv).

