# Stage 8.9.19 Error Analysis: Forensic Breakdown of False Positives & False Negatives

**Status:** COMPLETE — RESEARCH EXPERIMENTATION STAGE  
**Candidate Status:** REJECTED — RESEARCH ONLY  
**Evaluation Cohort:** Independent Held-Out Test Set ($N=462$, 78 Screams, 384 Hard Negatives)  
**Author:** Senior Audio AI Researcher & Forensic Acoustics Specialist  

---

## 1. Global Confusion Matrix Breakdown

On the independent held-out test cohort ($N=462$), the primary high-sensitivity candidate **Model C (Multi-Scale Routing)** yielded:
- **True Positives (TP):** 72
- **False Negatives (FN):** 6 (Missed Screams)
- **True Negatives (TN):** 346
- **False Positives (FP):** 38 (Hard Negative Errors)

In comparison, the primary high-specificity candidate **Model E (Neural Attention Fusion)** yielded:
- **True Positives (TP):** 44
- **False Negatives (FN):** 34
- **True Negatives (TN):** 374
- **False Positives (FP):** 10 (Hard Negative Errors)

---

## 2. Forensic Breakdown of False Positives in Model C ($N=38$)

Of the 38 false positives produced by Model C:

```
+---------------------------------------------------------------------------------------------------+
|  Category                       | Total in Test Cohort | Model C False Positives | Category FPR   |
+---------------------------------+:--------------------:|:-----------------------:|:--------------:+
|  Shouting & Excited Speech      |          84          |           18            |     21.43%     |
|  Crowd Cheering                 |          56          |            6            |     10.71%     |
|  Crowd Chanting                 |          42          |            5            |     11.90%     |
|  Singing & Vocal Performances   |          30          |            1            |      3.33%     |
|  Whistles & Sirens              |          36          |            4            |     11.11%     |
|  Festival Music & Synthesizers  |          48          |            4            |      8.33%     |
|  Infant Crying                  |          22          |            0            |      0.00%     |
|  Digital Silence                |          28          |            0            |      0.00%     |
|  Quiet Room & Ambient Tone      |          38          |            0            |      0.00%     |
+---------------------------------+----------------------+-------------------------+----------------+
|  Total Hard Negatives           |         384          |           38            |      9.90%     |
+---------------------------------------------------------------------------------------------------+
```

### 2.1 Acoustic Mechanism of the 18 Shouting False Positives
Detailed spectrogram and temporal feature analysis of the 18 misclassified shouting files revealed two dominant failure modes:
1. **Sustained Vowel Vocalizations (61% of shouting errors):**
   - When speakers shout sustained interjections (e.g., *"NOOO!"*, *"HEYYY!"*, *"WOOO!"*), vocal fold phonation continues uninterrupted for $>600$ ms.
   - Because no consonant closure occurs during the vowel nucleus, the consonant closure detector counts zero closures ($N_{closure} = 0$).
   - This fools the medium- and long-scale branches into identifying unbroken phonation identical to a genuine scream.
2. **High-Arousal Vocal Strain (39% of shouting errors):**
   - Loud aggressive shouting induces non-linear subharmonic bifurcations in the vocal folds, generating sub-band turbulence and high spectral flux that mimics genuine panic phonation.

---

## 3. Forensic Breakdown of False Negatives in Model C ($N=6$)

Model C successfully detected 72 out of 78 screams (**92.31% recall**), achieving the lowest false-negative count in project history. However, 6 screams were missed ($\hat{P} < 0.24$):

### Case 1: Distant Environmental Scream (`test_scream_019`, $\hat{P} = 0.182$)
- **Acoustic Characteristics:** Female scream recorded outdoors at an estimated distance of $>40$ meters with heavy ambient wind noise.
- **Root Cause:** Atmospheric absorption attenuated frequencies above 4 kHz, reducing the high-frequency turbulence ratio below the trigger threshold.

### Case 2: Masked Festival Scream (`test_scream_041`, $\hat{P} = 0.214$)
- **Acoustic Characteristics:** Short distress scream (duration $\sim 650$ ms) occurring simultaneously with a heavy sub-bass electronic music drop.
- **Root Cause:** Low-frequency acoustic energy dominated the spectral envelope, driving down the relative crest factor and onset flux.

### Case 3: Reverberant Indoor Scream (`test_scream_058`, $\hat{P} = 0.198$)
- **Acoustic Characteristics:** Scream recorded in a large concrete stairwell.
- **Root Cause:** Long room reverberation ($RT_{60} > 2.1$s) smeared the onset energy attack, causing $\tau_{attack}$ to exceed 90 ms and mimicking the gradual attack of spoken syllables.

### Cases 4–6: Low-SNR Vocalizations (`test_scream_063, 071, 077`, $\hat{P} \in [0.170, 0.231]$)
- **Acoustic Characteristics:** Screams with $SNR < 3.0$ dB relative to foreground crowd cheering.
- **Root Cause:** Competing crowd cheering obscured the harmonic structure of the scream, preventing confidence accumulation across branches.

---

## 4. Recommendations for Stage 8.9.20

1. **Sub-Band Formant & Biphonation Modeling:** To distinguish sustained shouting vowels (*"NOOO!"*) from screams, analyze vocal tract formant shifts and pitch-period perturbations (jitter/shimmer). Screams exhibit profound chaotic desynchronization, whereas shouted vowels maintain stable vowel formants ($F_1, F_2$).
2. **Noise-Robust Spectral Subtraction:** Implement an adaptive spectral subtraction front-end to isolate weak scream onsets from background festival bass.
