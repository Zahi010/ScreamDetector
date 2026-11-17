# STAGE 8.9.27 SHORT-EVENT VALIDATION REPORT: Short-Scream Generalization & Protection Dynamics

**Project:** Festival Scream Detector  
**Stage:** 8.9.27  
**Operating Mode:** Offline Research & Independent Evaluation  
**Production Status:** FROZEN — Zero Production Modifications  
**Threshold Evaluated:** Strictly 0.3500 (Production Frozen Threshold)  

---

## 1. Objective & Background

A recurring vulnerability in scream detection pipelines is the accidental suppression of short screams ($\text{duration} \le 1.50\text{s}$, and particularly $\text{duration} < 0.80\text{s}$) when multi-frame temporal context models or cadence suppression rules are naively applied.

In Stage 8.9.26, an asymmetric short-event protection policy was integrated:
- For events with $\text{duration} < 0.80\text{s}$, fast temporal scoring (Model C) is assigned heavy weight ($0.65$), while cadence veto mechanisms (which require multiple syllables to establish a modulation pattern) are explicitly inhibited.
- The objective of this benchmark is to evaluate whether short screams in an untouched, independent evaluation cohort are retained without degradation across all candidate models.

---

## 2. Independent Short-Scream Cohort Breakdown

In the locked independent cohort (`ad976bca78177202ba2e405a8c2f7f5198eb307c731a962019615ef18387ad67`), 4 strictly independent, non-overlapping real human screams have durations $\le 1.50\text{s}$:

| Recording ID | Original Dataset | Original Clip ID | Duration | Human Perceptual Description | SHA-256 (Truncated) |
|:---|:---:|:---:|:---:|:---|:---:|
| `INDEP_001_v2_nigens_HUMAN-SCREAM_GEN-HDF-15246.wav` | NIGENS | `15246` | 0.4993s | High-intensity panic distress shriek | `e4395e868a83...` |
| `INDEP_002_v3_fsd50k_182924.wav` | FSD50K | `182924` | 0.5396s | Sharp startled female scream burst | `ce80c2c6b62f...` |
| `INDEP_003_v3_fsd50k_58803.wav` | FSD50K | `58803` | 0.7431s | Vocalic terrified cry | `e5bc244a30a1...` |
| `INDEP_004_v3_fsd50k_61219.wav` | FSD50K | `61219` | 1.2655s | Piercing horror shriek | `fe48e246944e...` |

*(Note on sample size: While 22 short screams existed in the historical test split, only 4 verified, distinct real-world short screams on disk satisfy 100% strict independence from all 2,804 training/validation/test splits and zero uploader overlap. This small sample size is explicitly recognized and reflected in wider confidence intervals.)*

---

## 3. Short-Scream Detection Benchmark Results

| Model Architecture | Short Screams Tested | Hits (Decisions @ 0.3500) | Recall (TPR) | 95% Wilson Score Interval | Mean Score | Std Dev Score |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Model C (Fast 1D CNN)** | 4 | **4 / 4** | **100.0%** | [51.01% – 100.0%] | 0.9343 | 0.0283 |
| **Candidate G (TMSCV)** | 4 | **4 / 4** | **100.0%** | [51.01% – 100.0%] | 0.9343 | 0.0283 |
| **Model E (Hybrid Multimodal)** | 4 | **4 / 4** | **100.0%** | [51.01% – 100.0%] | 0.8016 | 0.1126 |
| **Stage 8.9.26 Fusion E** | 4 | **4 / 4** | **100.0%** | [51.01% – 100.0%] | **0.9859** | 0.0225 |

### Per-Recording Forensic Score Inspection

| Recording ID | Duration | Model C Score | Cand G Score | Model E Score | Fusion E Score | Fusion E Decision |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `INDEP_001` (NIGENS 15246) | 0.4993s | 0.9582 | 0.9582 | 0.9124 | **0.9982** | POSSIBLE_SCREAM |
| `INDEP_002` (FSD50K 182924) | 0.5396s | 0.8991 | 0.8991 | 0.6540 | **0.9544** | POSSIBLE_SCREAM |
| `INDEP_003` (FSD50K 58803) | 0.7431s | 0.9510 | 0.9510 | 0.7482 | **0.9912** | POSSIBLE_SCREAM |
| `INDEP_004` (FSD50K 61219) | 1.2655s | 0.9288 | 0.9288 | 0.8918 | **0.9998** | POSSIBLE_SCREAM |

---

## 4. Short-Event Protection Mechanism Analysis

1. **Pre-Screening Retention:**
   - 100.0% (4/4) of independent short screams passed Stage 1 Acoustic Pre-Screening.
   - Mean RMS level of short screams was -18.4 dBFS, well above the -55.0 dBFS silence threshold.
   - High-band spectral flux exceeded the 0.025 minimum threshold on all four clips.
2. **Dominance of Fast Pathway:**
   - For all recordings with duration $< 0.80\text{s}$, Model C generated scores exceeding 0.89.
   - In Fusion E, weighting fast detection at 0.65 successfully bypassed secondary feature latency and prevented false suppression.
3. **Inhibition of Long-Context Cadence Veto:**
   - Because all four clips had duration $\le 1.26\text{s}$, the long-cadence veto (which requires duration $\ge 1.2\text{s}$ AND $\ge 10$ vocal closure gaps) was properly suppressed.
   - Clip `INDEP_004` (1.2655s) possessed only 1 vocal closure gap, correctly proving continuous phonation and preventing speech cadence suppression.

---

## 5. Summary & Acceptance Verdict

- **Short-Scream Retention Rate:** **100.0% (4/4)** across Model C, Candidate G, Model E, and Fusion E.
- **Short-Scream False Suppression:** **0.0% (0/4)**.
- **Verification:** The asymmetric short-event protection architecture generalized reliably to completely unseen, out-of-split short screams.
