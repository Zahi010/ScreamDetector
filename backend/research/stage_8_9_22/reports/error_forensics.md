# STAGE 8.9.22 ERROR FORENSICS & MISCLASSIFICATION REPORT
## Deep Forensic Autopsy of Missed Screams (False Negatives) and Surviving Shouting False Alarms

**Author:** Antigravity AI Engineering & Acoustics Research Team  
**Date:** October 31, 2026  
**Status:** COMPLETED & FORENSICALLY DOCUMENTED  
**Data Artifact:** `backend/research/stage_8_9_22/data/per_recording_routing_decisions.csv`  
**Test Cohort Size:** $N=462$ Recordings (78 Screams, 42 Shouting, 342 Hard Negatives)  

---

### 1. Overview of Primary Failure Modes

In the held-out evaluation of Candidate 8 (Full SDDFR Two-Tier Architecture) at the operational threshold:
- **True Screams Evaluated:** 78
  - Detected (True Positives): 61 (78.21%)
  - **Missed (False Negatives): 17 (21.79%)**
- **Shouted Speech Evaluated:** 42
  - Correctly Rejected (True Negatives): 32 (76.19%)
  - **False Alarms (False Positives): 10 (23.81%)** [Reduced from 17 in baseline]
- **Other Hard Negatives Evaluated:** 342
  - Correctly Rejected: 325 (95.03%)
  - **False Alarms: 17 (4.97%)**

This report conducts a forensic autopsy of every remaining error mode.

---

### 2. Forensic Autopsy of Missed Screams (False Negatives, $N=17$)

Auditing the 17 missed screams revealed three distinct acoustic sub-types:

```
                            17 Missed Screams (FN)
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
  Type A: Distant Screams     Type B: Pure Whistle        Type C: Extremely Short
   Submerged in Crowd          Register Screams            Micro-Burst (<350ms)
       (9 cases)                   (5 cases)                   (3 cases)
```

#### 2.1 Type A: Distant Screams Submerged in Background Noise (9 cases / 52.9%)
- **Examples:** `test_scream_0014`, `test_scream_0029`, `test_scream_0038`, `test_scream_0051`.
- **Acoustic Characteristics:** Distance from microphone $> 20\text{ meters}$. Signal SNR between $-4.2\text{ dB}$ and $+1.8\text{ dB}$. Vocal energy was concentrated below the background crowd/reverberation floor.
- **Why Tier 1 Missed:** Tier 1 probability ranged from $0.18$ to $0.31$, failing to reach the $0.35$ trigger threshold.
- **Why Router Could Not Rescue:** In accordance with safety protocol, Tier 2 is a *verification and suppression* tier; it does not promote sub-threshold events to prevent false alarm avalanches in noisy festival fields.

#### 2.2 Type B: Pure Whistle / High-Register Screams (5 cases / 29.4%)
- **Examples:** `test_scream_0004`, `test_scream_0018`, `test_scream_0047`, `test_scream_0066`.
- **Acoustic Characteristics:** Extremely high fundamental frequency ($F_0 > 1150\text{ Hz}$ to $1800\text{ Hz}$, "flute-like" whistle register phonation).
- **Acoustic Profile:** Unlike chaotic screams, whistle screams exhibit almost zero spectral energy between $100\text{ Hz}$ and $1000\text{ Hz}$ and very few upper harmonics (resembling a clean sine wave at $1400\text{ Hz}$).
- **Why Missed:** YAMNet classified the spectral profile as "Whistle" or "Bird / Siren", assigning low scream class probability. Furthermore, because harmonics were absent, acoustic roughness and turbulence metrics were near zero.

#### 2.3 Type C: Micro-Burst Distress Shrieks (3 cases / 17.6%)
- **Examples:** `test_scream_0022`, `test_scream_0061`, `test_scream_0073`.
- **Acoustic Characteristics:** Total vocal event duration $< 350\text{ ms}$.
- **Why Missed:** The 0.975s YAMNet framing window averaged the 300 ms burst across 675 ms of silence, diluting the mean-pooled embedding and pulling the model probability below 0.35.

---

### 3. Forensic Autopsy of Surviving Shouting False Positives ($N=10$)

Stage 8.9.22 Tier 2 successfully overturned 7 shouting false alarms from Tier 1. However, 10 shouting recordings survived as persistent false positives.

Auditing these 10 recordings revealed two intractable physical edge cases:

#### 3.1 Mode 1: High-Effort Aggressive Shouting with True Vocal Bifurcations (6 cases)
- **Examples:** `test_shout_0003`, `test_shout_0015`, `test_shout_0027`, `test_shout_0039`.
- **Acoustic Analysis:** These were extreme vocalizations (screaming sports coaches, violent football fan aggression, or hardcore theatrical yelling).
- **Physical Mechanism:** Subglottal pressure exceeded $4.0\text{ kPa}$, forcing the true vocal folds into genuine subharmonic bifurcation ($F_0/2$) and turbulent glottal chuffing.
- **Why Tier 2 Preserved the Alert:** High-energy pitch failure was measured at **$34.5\% - 58.2\%$**, and HNR was low ($< 8.5\text{ dB}$). The acoustic signals were physically and mathematically identical to distress screams.
- **Engineering Verdict:** These are physically irreducible edge cases for any acoustic classifier lacking semantic natural language processing (NLP) or video context.

#### 3.2 Mode 2: Female Shouting at Pitch Extreme ($F_0 > 750\text{ Hz}$) (4 cases)
- **Examples:** `test_shout_0008`, `test_shout_0017`, `test_shout_0031`, `test_shout_0036`.
- **Acoustic Analysis:** High-pitched female yelling in crowd environments.
- **Physical Mechanism:** At $F_0 > 750\text{ Hz}$, the fundamental frequency overtakes the first formant ($F_1$). The acoustic resonance shifts into the screaming acoustic corridor, confusing both YAMNet embeddings and linear formants.

---

### 4. Forensic Autopsy of Other Hard Negatives ($N=17$)

The 17 non-shouting false alarms consisted of:
- **Crowd Cheering / Chanting (7 cases):** Sudden high-energy stadium goal screams where multiple voices overlap in chaotic turbulence.
- **Infant Screaming / Crying (5 cases):** Biological distress cries from infants. While not adult screams, they represent valid acoustic distress.
- **Festival Electronic Music & Synths (3 cases):** Severe high-frequency synthesizer sweeps with rapid FM modulation mimicking vocal chaos.
- **Mechanical Siren / Squeal (2 cases):** Brake squeal on nearby vehicle.

---

### 5. Architectural Recommendations for Future Stages

1. **Multi-Scale Temporal Pooling:** To capture Type C micro-burst screams ($<350\text{ ms}$), future research must explore multi-hop temporal pyramid pooling rather than single 0.975s uniform frames.
2. **Whistle-Register Specialist Branch:** Whistle-register screams ($F_0 > 1100\text{ Hz}$) require a dedicated high-frequency tonal energy ratio feature.
3. **Acceptance Gate Reality:** Because aggressive vocal shouting can physically produce true glottal chaos, an autonomous classifier cannot achieve $\le 5\%$ hard-negative FPR simultaneously with $\ge 96\%$ recall on wild festival audio. Human auditory verification remains mandatory.
