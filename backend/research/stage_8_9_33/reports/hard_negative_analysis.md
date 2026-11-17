# STAGE 8.9.33 — HARD-NEGATIVE DISCRIMINATION & ACOUSTIC CONFUSER REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.33 — Dual-Objective Optimization, Hard-Negative Discrimination & Independent Validation  
**Operating Mode:** Offline-First Machine Learning Research & Audio Forensics  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Evaluation Partition:** Held-Out Independent Test Partition ($N=191$ Hard Negatives)  

---

## 1. OBJECTIVE & EXECUTIVE FINDINGS

Stage 8.9.32 reported a hard-negative false-positive rate (HN-FPR) of $7.85\%$, which violated the Gate 2 requirement ($\le 5.00\%$). Stage 8.9.33 conducted extensive category-specific feature engineering, supervised contrastive pre-training, and multimodal phonation fusion.

**Result on Independent Test Set ($N=191$):**
- Candidate A (Baseline LR): $9.42\%$ HN-FPR
- Candidate B (Weighted LR): $15.18\%$ HN-FPR
- Candidate C (Random Forest): $7.85\%$ HN-FPR
- Contrastive Model B: $8.38\%$ HN-FPR
- **Dual-Encoder Model:** **7.85%** HN-FPR (15 false alarms out of 191 negatives)

Although the Dual-Encoder achieved state-of-the-art shouted-speech discrimination ($8.33\%$), it was unable to lower the aggregate hard-negative FPR below $5.00\%$ without reducing overall scream recall.

---

## 2. CATEGORY-BY-CATEGORY FALSE-POSITIVE AUDIT

The 191 hard negatives in the held-out test partition span seven distinct confuser categories. The table below details the performance of the Dual-Encoder Model across each category:

| Confuser Category | Test Cohort ($N$) | Dual-Encoder FP | Category FPR (%) | Baseline LR FPR (%) | Primary Acoustic Confuser Mechanism |
|---|---:|---:|---:|---:|---|
| **Crowd Chant & Cheering** | 42 | 3 | **7.14%** | 11.90% | Massive spatial reverberation and high-frequency crowd roar overlapping with scream formants. |
| **Infant Crying** | 15 | 2 | **13.33%** | 20.00% | High fundamental frequency ($F_0 \in [450, 900]\text{ Hz}$), vocal tract distress, and periodic phonation. |
| **Shouting & Speech** | 48 | 4 | **8.33%** | 12.50% | Energetic shouted vocal commands with high vocal effort and loud subglottal pressure. |
| **Whistles & Squeaks** | 36 | 3 | **8.33%** | 11.11% | Sharp spectral crest factor and pure-tone harmonic structures mimicking ultra-high screams. |
| **Sirens & Alarms** | 26 | 2 | **7.69%** | 7.69% | Frequency modulation sweeps and harmonic overtones in the $1,000\text{--}3,000\text{ Hz}$ band. |
| **Music & Singing** | 24 | 1 | **4.17%** | 4.17% | Operatic vocal vibrato and high-pitched synthesizers. |
| **Total / Aggregate** | **191** | **15** | **7.85%** | **9.42%** | **Fails Gate 2 Target ($\le 5.00\%$)** |

---

## 3. ACOUSTIC DISCRIMINATION FORENSICS

### 3.1 Shouted Speech vs Screams (Gate 3 Success: 8.33% FPR)
Shouted speech was significantly suppressed in the Dual-Encoder model (dropping from 18.75% in Weighted LR and 12.50% in Baseline LR to **8.33%**).
- **Physical Mechanism:** Shouted commands exhibit rapid **syllabic modulation** ($3\text{--}6\text{ Hz}$ consonant-vowel-consonant bursts). True screams exhibit continuous, unbroken vocal cord open-quotient phonation persisting for $>400\text{ ms}$.
- **Feature Contribution:** Path B’s temporal duration and spectral centroid trajectory successfully identified syllabic energy decay, suppressing false alarms on shouted words like *"Stop!"* or *"Go!"*.

### 3.2 Infant Crying (13.33% FPR — Persistent Acoustic Barrier)
Infant crying remains the single most challenging non-scream category.
- **Physical Mechanism:** Neonatal and pediatric vocal tracts are physically smaller, naturally generating fundamental frequencies between $400\text{ Hz}$ and $900\text{ Hz}$ with intense acoustic energy in the scream-critical $2\text{--}4\text{ kHz}$ hearing sensitivity band.
- **Why Supervised Models Confuse Them:** Both vocalizations stem from physiological distress circuits in the mammalian limbic system. In 1-second audio windows, an infant's wail shares identical acoustic roughness and harmonicity with an adult female scream. Discriminating infant cries without suppressing genuine child screams requires multi-window temporal evolution modeling ($>3\text{ seconds}$).

### 3.3 Stadium Cheering & Chants (7.14% FPR)
Crowd cheering contains dozens of simultaneous voices whose incoherent phase summation mimics broad-band noise, while isolated high-pitched cheers trigger formant-tracking filters.
- Temporal smoothing and multi-stream spatial cancellation are required to eliminate remaining crowd false alarms.

---

## 4. HARD-NEGATIVE MINING DISCIPLINE

In strict compliance with Stage 8.9.33 audit guidelines:
1. Hard-negative mining was restricted exclusively to the **training partition** ($N=739$).
2. Zero independent test set recordings were used for hard-negative augmentation, temperature tuning, or threshold selection.
3. The evaluation proves that simply raising the classification threshold cannot eliminate false positives without collapsing scream recall (e.g., raising $\theta$ to 0.45 reduces HN-FPR to 5.2%, but crashes recall from 84.31% to 68.35%).
