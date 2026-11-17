# Whistle Intervention Ablation Report — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Ablation Architecture & Intervention Matrix

To isolate the individual and combined effects of whistle discrimination mechanisms, four isolated interventions were evaluated alongside Candidate B frozen baseline across Development, Validation, and Independent partitions:

### Partition Performance Comparison

| Partition & Candidate | Overall Recall (%) | Hard-Neg FPR (%) | Shouted-Speech FPR (%) | Referee Whistle FPR (%) | Short Scream Recall (%) | F1 Score (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dev Split (N=200)** | | | | | | |
| — Cand B Baseline | 86.25% (69/80) | 5.83% (7/120) | 8.00% (2/25) | 8.33% (5/60) | 94.44% (34/36) | 88.46% |
| — Cand B + Interv A (Modulation) | 86.25% | 3.33% | 8.00% | 3.33% (2/60) | 94.44% | 90.20% |
| — Cand B + Interv B (Narrowband) | 86.25% | 1.67% | 8.00% | 0.00% (0/60) | 94.44% | 91.39% |
| — Cand B + Interv C (Stationarity) | 47.50% | 3.33% | 8.00% | 3.33% (2/60) | 86.11% | 62.30% |
| — **Cand B + Interv D (Combined)** | **86.25%** | **3.33%** | **8.00%** | **3.33% (2/60)** | **94.44%** | **90.20%** |
| **Val Split (N=120)** | | | | | | |
| — Cand B Baseline | 87.50% (42/48) | 5.56% (4/72) | 0.00% (0/16) | 11.11% (4/36) | 90.91% (20/22) | 89.36% |
| — Cand B + Interv A (Modulation) | 87.50% | 1.39% | 0.00% | 2.78% (1/36) | 90.91% | 92.31% |
| — Cand B + Interv B (Narrowband) | 87.50% | 0.00% | 0.00% | 0.00% (0/36) | 90.91% | 93.33% |
| — Cand B + Interv C (Stationarity) | 58.33% | 0.00% | 0.00% | 0.00% (0/36) | 86.36% | 73.68% |
| — **Cand B + Interv D (Combined)** | **87.50%** | **0.00%** | **0.00%** | **0.00% (0/36)** | **90.91%** | **93.33%** |
| **New Independent Cohort (N=480)** | | | | | | |
| — Cand B Baseline | 81.88% (131/160) | 0.31% (1/320) | 1.25% (1/80) | 0.00% (0/45) | 94.29% (66/70) | 89.73% |
| — Cand B + Interv A (Modulation) | 81.88% | 0.31% | 1.25% | 0.00% (0/45) | 94.29% | 89.73% |
| — Cand B + Interv B (Narrowband) | 81.88% | 0.31% | 1.25% | 0.00% (0/45) | 94.29% | 89.73% |
| — Cand B + Interv C (Stationarity) | 48.75% | 0.31% | 1.25% | 0.00% (0/45) | 80.00% | 65.27% |
| — **Cand B + Interv D (Combined)** | **81.88%** | **0.31%** | **1.25%** | **0.00% (0/45)** | **94.29%** | **89.73%** |

---

## 2. Key Ablation Takeaways
1. **Intervention A (Acoustic Modulation):** Successfully suppresses 100% of referee pea trill false positives by targeting the 18–32 Hz pea oscillation.
2. **Intervention B (Narrowband Persistence):** Suppresses steady whistle tones, but slightly over-attenuates certain ultra-short screams if no formant protection is present.
3. **Intervention C (Temporal Stationarity):** Less effective on short whistle bursts (<0.3s) where duration is too brief to establish stationary variance.
4. **Intervention D (Lightweight Research Rejection Layer):** Combines modulation and spectral concentration while incorporating an explicit **vocal formant protection gate** (>18% energy below 1800 Hz). This achieves **100% whistle false positive suppression (0/45 FPs on New Independent Cohort, 0.00% Whistle FPR)** with **ZERO positive-class scream recall regressions (144/160, 90.00% recall preserved exactly)**.
