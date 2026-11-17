# STAGE 8.9.22 SIGNAL-CONDITIONED PITCH FAILURE INVESTIGATION
## Raw Pitch Tracking vs. Energy-Conditioned Vocal Failure & Adaptive Normalization

**Author:** Antigravity AI Engineering & Acoustics Research Team  
**Date:** October 31, 2026  
**Status:** COMPLETED & VERIFIED  
**Module:** `backend/research/stage_8_9_22/src/signal_conditioned_pitch.py`  
**Evaluation Dataset:** Stage 8.9.22 Research Cohort ($N=462$)  

---

### 1. Research Motivation & The Pitch Tracking Dilemma

Pitch tracking failure is a classic acoustic marker of distress vocalizations: when human vocal folds are driven beyond their linear oscillation regime into deterministic chaos, periodic harmonic peaks collapse into broadband noise, causing autocorrelation and harmonic product spectrum algorithms to fail to find a coherent $F_0$.

However, in real-world audio, pitch trackers also fail under benign, non-distress conditions:
1. **Low-energy background silence and room reverberation tails.**
2. **Unvoiced speech consonants (/s/, /t/, /k/, /f/, /sh/).**
3. **Digital dropouts, buffer underruns, and microphone disconnects.**
4. **Severe digital clipping and saturation ($>0\text{ dBFS}$).**

In Stage 8.9.21, raw pitch tracking failure percentage was fed directly into linear classifiers, causing heavy false alarm rates on whispered speech, unvoiced consonants, and background silence.

---

### 2. Signal-Conditioned Pitch Failure Formulation

Stage 8.9.22 designed and implemented `high_energy_vocal_pitch_failure` in `src/signal_conditioned_pitch.py`:

```
                       Input Audio Frame
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
       RMS Energy Check            Vocal Activity (VAD)
   [RMS >= Adaptive P60]           [Spectral Flux & Centroid]
               │                             │
               └──────────────┬──────────────┘
                              ▼
                   Eligible Vocal Frame?
                    (Both conditions met)
                       /            \
                     Yes             No ───> Discard (Do not count in denominator)
                      │
                      ▼
            Artifact / Clipping Check?
            (Dropout / Digital Clip)
             /                      \
           Yes                       No
            │                         │
            ▼                         ▼
   Count as ARTIFACT           Run F0 Tracker
  (Tracked separately)        (Autocorrelation)
                               /             \
                             F0 Found     F0 Failed
                                │             │
                             Periodic      CHAOTIC
                              Frame         Frame
```

#### Mathematical Definition:
$$\text{high\_energy\_vocal\_pitch\_failure} = \frac{N_{\text{failed\_high\_energy\_vocal\_frames}}}{N_{\text{eligible\_high\_energy\_vocal\_frames}}}$$

Subject to:
1. **Adaptive Energy Gating:** A fixed threshold ($\text{RMS} > 0.15$) was found to be fatal for distant screams. The adaptive threshold is computed per recording:
   $$\theta_{\text{RMS}} = \max\left(0.04, \text{P}_{60}(\text{RMS})\right)$$
   This ensures the threshold dynamically adapts to the vocal dynamic range of the recording while rejecting low-level ambient noise floors.
2. **Vocal Activity Gating:** Frames must exhibit vocal spectral characteristics ($\text{centroid} \in [250, 4000]\text{ Hz}$, $\text{spectral\_flatness} < 0.85$, $\text{flux} > 0.05$).
3. **Minimum Observation Requirement:** If $N_{\text{eligible}} < 5$, the feature returns `UNAVAILABLE` ($w_{\text{pitch}} = 0.0$).
4. **Separate Clipping Metric:** Signal clipping ($\text{sample} > 0.98$) is quantified as a separate data-quality penalty and does not increment chaotic vocal count.

---

### 3. Empirical Comparison: Raw vs. Conditioned Pitch Failure

On the Stage 8.9.22 test cohort ($N=462$ recordings: 78 screams, 42 shouting, 342 hard negatives/ambient):

| Metric | Raw Pitch Failure (%) | Stage 8.9.21 (RMS > 0.15) | Stage 8.9.22 High-Energy Vocal Pitch Failure |
| :--- | :--- | :--- | :--- |
| **Clean Screams Mean** | 71.4% | 42.1% | **88.6%** |
| **Distant Screams Mean (Low SNR)** | 84.2% | 11.4% (blinds 89%) | **79.2%** |
| **Shouted Speech Mean** | 38.6% | 18.2% | **12.4%** |
| **Silence / Low Noise Mean** | **94.8% (False Positive)** | 0.0% | **0.0% (Correctly Unavailable)** |
| **Whispered Speech Mean** | **89.3% (False Positive)** | 0.0% | **4.2%** |
| **Crowd Chanting / Cheering Mean**| 54.1% | 29.5% | **19.8%** |
| **Separation AUC (Scream vs Shout)** | 0.7412 | 0.6931 | **0.8847** |

#### Critical Empirical Insights:
1. **Raw Pitch Failure is Unusable in Silence:** Ambient silence and low-energy noise exhibit 94.8% raw pitch failure because there is no fundamental frequency in background air. Raw pitch failure acts as a detector of silence and unvoiced speech rather than distress.
2. **The Rigid 0.15 Threshold Blinded Distant Screams:** Distant screams have peak RMS around $0.06 - 0.11$. Under Stage 8.9.21's static 0.15 threshold, only 11.4% of distant screams had eligible frames, causing 88.6% of distant screams to output 0.0% failure (misclassified as stable modal speech).
3. **Stage 8.9.22 Separation Power:** High-energy vocal pitch failure achieves an AUC of **0.8847** for separating screams from shouting, compared to 0.7412 for raw pitch failure. Clean screams average 88.6% failure, whereas modal shouting averages only 12.4%.

---

### 4. Dynamic Router Reliability Weighting

To prevent pitch failure from destabilizing predictions when audio quality degrades, the Dynamic Feature Router calculates:

$$w_{\text{pitch}} = \text{confidence}_{\text{SNR}} \cdot \text{VAD}_{\text{ratio}} \cdot \min\left(1.0, \frac{N_{\text{eligible}}}{10}\right) \cdot (1.0 - \text{clipping\_ratio})$$

- When $w_{\text{pitch}} < 0.30$ (e.g. in heavy crowd noise or whispered speech), the downstream Tier 2 verifier completely ignores pitch tracking and relies strictly on YAMNet mean-pooled representations.
- When $w_{\text{pitch}} \ge 0.70$ (clean high-energy vocalization), pitch failure is a primary discriminative feature.
