# STAGE 8.9.34 — TEMPORAL FEATURE ANALYSIS & ENVELOPE DYNAMICS REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.34 — Temporal Context Modeling, Infant-Cry Discrimination & SNR-Adaptive Scream Detection  
**Operating Mode:** Offline-First Machine Learning Research & Signal Processing Analysis  
**Production Status:** STRICTLY FROZEN (Production Threshold: `0.3500`)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** November 2, 2026  

---

## 1. INVESTIGATION OBJECTIVE

In single 975 ms analysis windows, human screams and pediatric vocal distress (infant crying) share overlapping fundamental frequencies ($F_0 \in [450, 900]\text{ Hz}$), high harmonicity, and acoustic roughness. Consequently, frame-level static classifiers struggle to differentiate them without false alarms.

This phase audited the hypothesis that **temporal organization across extended observation windows ($1\text{--}5\text{ s}$) exhibits measurable differences** in burst continuity, silence intervals, and envelope periodicity between screams and confusers.

---

## 2. STATISTICAL DISTRIBUTIONS ACROSS CATEGORIES

Features were extracted across 200 empirical audio recordings (60 screams, 60 infant cries, 40 shouting, 40 crowd cheering) using 10 ms hop RMS energy envelope profiling and envelope autocorrelation:

| Acoustic Metric | Genuine Screams ($N=60$) | Infant Crying ($N=60$) | Shouted Speech ($N=40$) | Crowd Cheering ($N=40$) |
|---|---:|---:|---:|---:|
| **Burst Continuity Ratio** | **0.465** $\pm 0.182$ | **0.161** $\pm 0.084$ | 0.321 $\pm 0.125$ | 0.340 $\pm 0.151$ |
| **Envelope Periodicity Score** | **0.277** $\pm 0.126$ | **0.357** $\pm 0.163$ | 0.264 $\pm 0.142$ | **0.470** $\pm 0.193$ |
| **Mean Active Burst Duration** | **1.240 s** $\pm 0.610$ | **0.420 s** $\pm 0.195$ | 0.580 s $\pm 0.210$ | 0.950 s $\pm 0.440$ |
| **Mean Inter-Burst Silence** | 0.180 s $\pm 0.110$ | **0.485 s** $\pm 0.220$ | 0.310 s $\pm 0.140$ | 0.120 s $\pm 0.080$ |
| **Repetition Modulation Frequency** | 2.41 Hz (Aperiodic) | **2.22 Hz (Periodic)** | 1.79 Hz (Syllabic) | **2.86 Hz (Rhythmic)** |

---

## 3. KEY ACOUSTIC DISCRIMINANTS

### 3.1 Burst Continuity vs Periodic Phonation
- **Screams:** Exhibit sustained open-quotient vocal fold vibration without respiratory pauses for the duration of the event (mean burst duration $= 1.24\text{ s}$, continuity ratio $= 0.465$). True screams rarely break into regular periodic pauses unless uttered as multiple distinct panic events.
- **Infant Crying:** Constrained by pediatric lung volume and the physiological respiratory-phonatory cycle (gasp $\to$ vocal burst $\to$ inspiratory pause $\to$ vocal burst). Mean burst duration is short ($0.42\text{ s}$), separated by significant silence intervals ($0.485\text{ s}$), producing a distinctly periodic envelope pattern ($\approx 2.22\text{ Hz}$).

### 3.2 Crowd Cheering Modulation
- Stadium cheering and crowd chants exhibit the highest overall envelope periodicity (**0.470**), driven by synchronized collective clapping and cadenced shouting (*"Let's Go!"*).

---

## 4. ARCHITECTURAL IMPLICATION FOR PHASE TWO

Static frame-level models are blind to inter-burst silence and repetition frequency because a single 975 ms window captures only a single slice of phonation. 
A **Causal Recurrent Aggregator (GRU)** or **Temporal Convolutional Network (TCN)** with a receptive field of $2\text{--}3\text{ seconds}$ can learn to suppress periodic burst trains with inter-burst pauses (infant crying) while triggering rapidly on sustained, unbroken vocal energy (screams).
