# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# 268-Clip Held-Out Short-Scream Provenance & Subgroup Performance Audit

**Mandatory Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.  
**Research Stage:** Stage 8.9.70  
**Evaluator:** Dataset Provenance & Acoustic Forensic Engine  
**Dataset Artifact:** Stage 64 Held-Out Short-Scream Evaluation Manifest ($N=268$)  
**Reference Results:** [short_scream_268_subgroup_results.csv](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_70/reports/short_scream_268_subgroup_results.csv)

---

## 1. Executive Summary & Provenance Trace

The Stage 64 held-out short-scream partition ($N=268$) was created in Stage 8.9.64 to evaluate model generalization on previously unseen short vocal distress bursts ($< 1.0$s duration). This audit verifies the lineage, source-group isolation, and acoustic performance gap observed between development and held-out short screams.

### 1.1 Lineage & Quarantine Verification
- **Source Manifest:** `stage_64_short_scream_manifest.csv` containing an initial pool of $N=401$ short scream clips.
- **De-duplication & Development Cohort Quarantine:** $N=133$ clips with identical audio SHA-256 hashes to the Stage 63 development set were strictly purged.
- **Net Held-Out Evaluation Pool:** Exactly $N=268$ clips ($401 - 133 = 268$).
- **Cross-Cohort Contamination Check:**
  - Overlap with Stage 54 Training Partition ($N=1,055$): **0 clips (0.0%)**
  - Overlap with Stage 54 Validation Partition ($N=311$): **0 clips (0.0%)**
  - Overlap with Stage 54 Reserved Test Partition ($N=445$): **0 clips (0.0%)**
  - Overlap with Stage 60 Sealed Evaluation Cohort ($N=700$): **0 clips (0.0%)**

---

## 2. Source-Group Composition ($N=268$)

The 268 recordings originate from seven distinct recording sources, ensuring geographic and acoustic device heterogeneity:

| Source Group ID | Clip Count | Percentage | Acoustic Environment Description |
| :--- | :--- | :--- | :--- |
| `sg_short_s49` | 164 | 61.19% | Outdoor festival and sports field crowd recordings with distant vocal bursts |
| `sg_short_s43` | 37 | 13.81% | Semi-open amphitheater acoustics with short transient screams |
| `sg_short_supp` | 34 | 12.69% | Low-SNR environmental recordings with high ambient masking |
| `sg_short_v3` | 19 | 7.09% | Indoor hall reverberant screams |
| `sg_short_acq` | 8 | 2.99% | Close-proximity mobile device acquisitions |
| `sg_short_v2` | 4 | 1.49% | High-pass filtered emergency drill recordings |
| `sg_short_pos` | 2 | 0.75% | Studio vocal distress simulations |
| **Total** | **268** | **100.0%** | **7 Independent Source Groups** |

---

## 3. Subgroup Performance Audit

The table below summarizes Candidate 69-D and Candidate 70-D performance stratified across event duration bins:

| Duration Subgroup | Clip Count | Candidate 69-D TP | Candidate 69-D FN | Candidate 69-D Recall | Candidate 70-D TP | Candidate 70-D FN | Candidate 70-D Recall |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0–250 ms** | 1 | 1 | 0 | **100.00%** | 1 | 0 | **100.00%** |
| **250–500 ms** | 67 | 49 | 18 | **73.13%** | 49 | 18 | **73.13%** |
| **500–1000 ms** | 200 | 106 | 94 | **53.00%** | 108 | 92 | **54.00%** |
| **Overall Held-Out** | **268** | **156** | **112** | **58.21%** | **158** | **110** | **58.96%** |

---

## 4. Root-Cause Analysis of the Generalization Gap

A key question in Stage 8.9.70 is why Candidate 69-D achieves **92.31% (36/39)** recall on Stage 54 validation short screams, but drops to **58.21% (156/268)** on this held-out cohort.

### 4.1 Neural Underconfidence vs. Veto Over-Suppression
To determine whether false negatives are caused by heuristic vetoes (whistle, flux, vocal distress) or neural representation failure, all 112 false negatives were examined at the raw model logit level:

- **Raw Pre-Veto Neural Probabilities:**
  - $p_{\text{raw}} < 0.4920$ (Neural Underconfidence): **94 clips (83.9%)**
  - $p_{\text{raw}} \ge 0.4920$ (Suppressed by Heuristic Veto): **18 clips (16.1%)**

**Empirical Conclusion:** Over **83.9%** of the false negatives in the held-out cohort fail before any heuristic suppression filter is evaluated. The dual-resolution network itself assigns low probabilities to these clips.

### 4.2 Acoustic Distribution Discrepancy
Comparing the Stage 54 validation screams against the held-out cohort reveals two critical domain shifts:
1. **Source Distance & Signal-to-Noise Ratio:**
   - In `sg_short_supp`, mean SNR is $\approx 2.4$ dB (compared to $\approx 8.6$ dB in Stage 54 Val). Mean $p_{\text{raw}}$ is only $0.386$, resulting in a recall of just 32.35% (11/34).
   - In `sg_short_s49`, mean $p_{\text{raw}}$ is $0.472$, near the operating threshold boundary, resulting in 56.71% recall (93/164).
2. **Spectral Tilt & Temporal Truncation:**
   - Shorter bursts (250–500 ms) often lack the sustained periodic phonation required to populate the sustained branch's 1,000 ms window, yielding lower branch cosine similarity ($\text{sim} < 0.50$).

### 4.3 Scientific Conclusion
The performance gap on the 268 held-out short screams is not an artifact of heuristic veto tuning. It represents a genuine acoustic limitation of the dual-resolution neural trunk when evaluating distant, low-SNR screams embedded in complex crowd noise. Future stages must focus on noise-robust subband representation learning rather than further heuristic veto relaxation.

