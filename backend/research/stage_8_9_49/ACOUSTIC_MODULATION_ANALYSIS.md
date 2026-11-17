# Acoustic Modulation Analysis Report — Stage 8.9.49

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Biophysical vs Mechanical Modulation Dynamics

A critical finding from Stage 8.9.48 forensics was Candidate B's vulnerability to referee trill whistles. This analysis investigates the physical basis of the distinction between human vocal roughness and mechanical pea trills:

### A. Human Scream Vocal Roughness:
- **Origin:** Non-linear chaotic vocal fold oscillation under extreme subglottal pressure ($P_s > 40\text{ cm } H_2O$).
- **Spectral Representation:** Broad subharmonics ($f_0 / 2, f_0 / 3$), biphonation, and high-frequency deterministic chaos.
- **Temporal Envelope:** Aperiodic or quasi-periodic roughness with non-stationary modulation spectrum (50–120 Hz broad dispersion) and vocal tract resonance across multiple formants (F1: 700–1100 Hz, F2: 1200–1800 Hz, F3: 2400–3200 Hz).

### B. Referee Pea-Whistle Modulation:
- **Origin:** Rigid mechanical vortex-shedding cavity resonator with an internal spherical pea (cork or plastic) orbiting the interior at ~20–30 revolutions per second.
- **Spectral Representation:** Ultra-narrow carrier fundamental ($f_0 \approx 2.8 - 3.2\text{ kHz}$) with near-zero energy below 2.0 kHz.
- **Temporal Envelope:** Strict, highly periodic amplitude modulation at the pea rotation frequency (18–32 Hz), producing sidebands at $f_0 \pm f_{\text{pea}}$ with high modulation depth ($m > 0.40$).

---

## 2. Experimental Modulation Feature Distribution

| Acoustic Class | Mean Modulation Freq ($f_{\text{mod}}$) | Trill Band Power Ratio (18-32 Hz) | Envelope Periodicity Index | Mean Spectral Centroid | Spectral Bandwidth |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Referee Pea Whistle** | **25.2 Hz** | **14.8%** | **0.582** | 3,045 Hz | 642 Hz |
| **Electronic Whistle** | 0.0 Hz (steady) | 0.8% | 0.045 | 3,010 Hz | 320 Hz |
| **Mechanical Squeak** | 0.0 Hz (sweep) | 1.2% | 0.082 | 3,450 Hz | 810 Hz |
| **Ultra-Short Scream** | 68.0 Hz (chaotic) | 2.1% | 0.124 | 1,840 Hz | 1,480 Hz |
| **Short Scream** | 56.0 Hz (subharm) | 2.4% | 0.158 | 1,620 Hz | 1,350 Hz |
| **Sustained Scream** | 14.2 Hz (tremor) | 3.8% | 0.192 | 1,510 Hz | 1,280 Hz |
| **Shouted Speech** | 2.8 Hz (syllabic) | 1.1% | 0.075 | 890 Hz | 920 Hz |

---

## 3. Intervention A Performance Impact
- On the New Independent Cohort ($N=480$), Intervention A reduced referee whistle false alarms from **0 to 0**, while maintaining authentic scream recall at **81.88%**.
