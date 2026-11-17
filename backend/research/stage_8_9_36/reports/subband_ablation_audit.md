# Stage 8.9.36 — Subband Pathway Contribution & Ablation Audit Report

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Target:** Quantitative Pathway Ablation & Feature Independence Analysis  
**Data Artifact:** `backend/research/stage_8_9_36/evaluation/pathway_ablation_results.csv`  

---

## 1. Executive Summary & Objective

Phase 5 investigated whether Candidate D's frequency-subband pathway contributes **genuine independent physical information** or merely duplicates acoustic representations already captured by YAMNet embeddings and vocal phonation features.

A systematic 4-way ablation was performed using the identical training ($N=739$), validation ($N=293$), and independent held-out test partitions ($N=293$):
- **Config A:** YAMNet Pathway Only (1024-d)
- **Config B:** YAMNet + Phonation Pathway (Dual-Encoder Baseline: 1024-d + 12-d)
- **Config C:** YAMNet + Subband Pathway (1024-d + 11-d)
- **Config D:** YAMNet + Phonation + Subband Pathways (Full Multi-Pathway Candidate D: 1024-d + 12-d + 11-d)

---

## 2. Quantitative Ablation Scorecard on Held-Out Test Cohort ($N=293$)

| Model Configuration | Active Pathways | Threshold | Scream Recall | HN-FPR | Shout-FPR | Precision | F1-Score | Specificity | ROC-AUC | PR-AUC | P95 Latency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Config A** | YAMNet Only | 0.38 | 70.59% (72/102) | 9.95% (19/191) | 18.75% (9/48) | 79.12% | 0.7461 | 90.05% | 0.8912 | 0.8145 | **18.20 ms** |
| **Config B** | YAMNet + Phonation (Baseline) | 0.35 | 84.31% (86/102) | **7.85% (15/191)** | **8.33% (4/48)** | **85.15%** | 0.8473 | **92.15%** | 0.9285 | 0.8717 | 18.57 ms |
| **Config C** | YAMNet + Subband | 0.29 | 86.27% (88/102) | 12.57% (24/191) | 25.00% (12/48)| 78.57% | 0.8224 | 87.43% | 0.9142 | 0.8490 | 18.95 ms |
| **Config D** | YAMNet + Phonation + Subband | 0.43 | **89.22% (91/102)** | 9.95% (19/191) | 14.58% (7/48) | 82.73% | **0.8585** | 90.05% | **0.9374** | **0.8762** | 19.31 ms |

---

## 3. Feature Orthogonality Audit: Subband vs. Phonation Features

To determine whether subband features duplicate phonation features, Pearson cross-correlations were measured across the entire test cohort ($N=293$):

| Subband Feature | Phonation Feature | Pearson Correlation ($r$) | Statistical Independence Verdict |
| :--- | :--- | :---: | :--- |
| `scream_band_to_vocal_ratio` | Fundamental Frequency ($F_0$) | **-0.0541** | **Orthogonal (No Correlation)** |
| `scream_band_to_vocal_ratio` | Harmonics-to-Noise Ratio (HNR) | **-0.0318** | **Orthogonal (No Correlation)** |
| `Band4_2000_3000Hz_rel_energy` | Voicing Probability | **+0.0193** | **Orthogonal (No Correlation)** |
| `Band4_2000_3000Hz_rel_energy` | Amplitude Perturbation (Shimmer)| **-0.0997** | **Orthogonal (No Correlation)** |

### **Acoustic Physics Explanation:**
- **Phonation Features (Path B)** measure the **glottal source**: vocal fold vibration frequency ($F_0$), micro-periodicity variation (jitter), amplitude instability (shimmer), and aspiration noise (HNR).
- **Subband Features (Path C)** measure the **supraglottal vocal tract filter**: acoustic standing-wave resonances (formants), singer's formant clustering in 2–3 kHz ($B_4$), and high-frequency friction ($B_5$).
- Because the vocal source and the vocal tract filter are physically decoupled (source-filter theory of acoustic phonetics), the features exhibit near-zero correlation ($|r| < 0.10$).

---

## 4. Key Scientific Inferences

1. **Subband Features Provide Genuine Recall Enhancement:**
   - Adding Subband features to YAMNet (Config C vs. Config A) increased recall from 70.59% to 86.27% (+15.68%).
   - Adding Subband features to Dual-Encoder (Config D vs. Config B) increased recall from 84.31% to 89.22% (+4.91%).
   - Subband energy ratios successfully rescue screams where semantic representations are weak.
2. **The Phonation Guardrail is Essential for Shouted Speech:**
   - In Config C (lacking phonation), Shouted-Speech FPR exploded to **25.00%** (12 false alarms).
   - In Config D, re-introducing the phonation head suppressed Shouted-Speech FPR back down to **14.58%** (7 false alarms), satisfying Gate 3 ($\le 15.00\%$).
   - **Conclusion:** Subband features cannot safely be deployed without phonation guardrails to prevent speech confusion.
3. **The Remaining Gate Gap:**
   - While Config D achieved the highest recall (89.22%) and best F1 (0.8585), it failed Gate 1 ($\ge 96\%$) and Gate 2 ($\le 5\%$).
   - The ablation proves that while each pathway contributes valuable and orthogonal signal, simple linear fusion cannot completely resolve the overlap between high-energy crowd cheering and screams in festival acoustics.
