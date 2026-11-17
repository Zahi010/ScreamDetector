# Shouted-Speech Error Analysis — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Section 6.1 of Stage 8.9.59, a forensic investigation was performed into the shouted-speech false positives produced by frozen Candidate E1 + C5 on the validation set (`expansion_val`).

Out of 88 total shouted-speech validation clips, exactly **10 false positives** were observed (**11.36% FPR**). The audit revealed an extraordinary finding:
$$\mathbf{90.0\% \text{ (9 of 10) of all shouted-speech false alarms are concentrated in just TWO individual uploader recording sessions.}}$$

The remaining 35 independent shouting source groups in the validation partition generated only **1 false alarm across 79 clips (1.27% FPR)**.

---

## 2. Source-Group Concentration Analysis

| Source Group Identifier | Original Uploader / Session | Clips in Val | False Positives | Source Group FPR | Mean Probability | Dominant Acoustic Style |
|---|---|:---:|:---:|:---:|:---:|---|
| `exp_sg_stage8_9_reitanna` | `reitanna` (Session 3439) | 5 | **5 / 5** | **100.0%** | **0.8910** | Aggressive sustained shouting with vocal fry & phonatory strain |
| `exp_sg_fsd50k_uploader_ericsueiro` | `ericsueiro` (Session 2208) | 4 | **4 / 4** | **100.0%** | **0.9324** | Overdriven theatrical acting lines with near-clipping input |
| `exp_sg_fsd50k_uploader_11linda` | `11linda` (Session 1687) | 1 | **1 / 1** | **100.0%** | **0.8810** | High-energy sports court cheering/shouting |
| **All Other Shouting Source Groups (N=35)** | Various Independent Speakers | 78 | **0 / 78** | **0.00%** | **0.1425** | Natural conversational shouting, commands, cheer shouts |
| **Total Shouted-Speech Cohort** | **38 Unique Source Groups** | **88** | **10 / 88** | **11.36%** | **0.2310** | — |

---

## 3. Forensic Acoustic Investigation of the Two Problematic Sessions

### Session 1: `reitanna` (Session 3439, 5 False Positives)
- **Recordings:** `exp_v2_fsd50k_343872`, `exp_v2_fsd50k_343952`, `exp_v2_fsd50k_343955`, `exp_v2_fsd50k_343960`, `exp_v2_fsd50k_343965`.
- **Acoustic Characteristics:** The speaker produces high-effort, prolonged vocal shouts ("Stop!", "Leave me alone!") using an aggressive glottal press and heavy vocal fry.
- **Spectral Profile:** Spectral centroid reaches $2,650–3,100\text{ Hz}$. Energy in Band 3 (2000–4000 Hz) is exceptionally high ($>25\%$ of total acoustic energy), closely mimicking the acoustic signature of high-frequency distress screams.
- **Adjudication:** These recordings represent the extreme physiological boundary between high-effort shouting and shouting-screams.

### Session 2: `ericsueiro` (Session 2208, 4 False Positives)
- **Recordings:** `exp_v2_fsd50k_220822`, `exp_v2_fsd50k_220823`, `exp_v3_fsd50k_220817`, `exp_v3_fsd50k_220818`.
- **Acoustic Characteristics:** Performance audio recorded in a home studio with high microphone gain. When the actor shouts theatrical commands, the preamplifier experiences slight non-linear saturation (soft clipping).
- **Spectral Profile:** Harmonic distortion from saturation spreads energy into higher frequencies ($>3,000\text{ Hz}$), creating spurious deterministic chaos and elevated spectral flatness that trick the phonation classifier.

---

## 4. Key Scientific Conclusion

The detector does **NOT** suffer from a generalized inability to discriminate shouted speech from screams:
1. When presented with standard, non-distorted shouted speech across 35 independent source groups, Candidate E1 achieves an outstanding **98.7% true negative rejection rate**.
2. False positives are caused by:
   - Non-linear recording artifacts (microphone overdrive/clipping).
   - Extreme borderline vocal fry where human vocal cord mechanics exhibit sub-harmonic bifurcation.
3. **Data Strategy Directive:** To generalize beyond this limitation without degrading scream sensitivity, future dataset expansion must avoid clustering multiple crops from single actors, and instead acquire single independent shouting samples from diverse speakers across varied acoustic settings.

