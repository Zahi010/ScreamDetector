# Stage 8.9.14: Event Annotation and Short-Vocalization Protocol

**Document Version:** 1.0.0  
**Status:** Preregistered Safety-Critical Protocol  
**Author:** Independent Safety-Critical Evaluation Auditor & Senior Acoustic ML Research Engineer  
**Workspace:** `backend/experiments/v2_hard_negative_training/v4_temporal_research/stage8_9_14_acoustic_discriminability/`  

---

## 1. Purpose and Operational Scope

This document establishes the formal annotation standard for human vocal distress events, brief startle screams, and confounding acoustic hard negatives in the Festival Scream Detector benchmark.

In safety-critical edge detection, evaluating models solely on arbitrary whole-file boundaries creates artificial distortions. A 10-second file may contain a 400 ms startle scream followed by 9.6 seconds of quiet reverberation. This protocol provides deterministic, acoustically grounded criteria for:
1. Ground-truth event start ($t_{\text{start}}$) and end ($t_{\text{end}}$) boundary labeling.
2. Fine-grained vocalization taxonomy.
3. Ambiguity classification and binary quarantine.
4. Masking severity and background condition categorization.
5. Independent source-group provenance and license eligibility verification.

---

## 2. Event Boundary Annotation Standards

### 2.1 Acoustic Onset ($t_{\text{start}}$)
The ground-truth event start timestamp $t_{\text{start}}$ is defined as the earliest point where:
- The instantaneous RMS energy exceeds the pre-event noise floor by at least **+6.0 dB** AND
- Vocalization formant energy appears in the spectrogram above 800 Hz.
- For startle shrieks with rapid attack, $t_{\text{start}}$ is marked at the first prominent pressure excursion of the transient wavefront.

### 2.2 Acoustic Offset ($t_{\text{end}}$)
The ground-truth event end timestamp $t_{\text{end}}$ is defined as the point where:
- Formant energy drops below the local noise floor OR
- Vocal energy falls by **-18.0 dB** relative to the peak event energy for a continuous duration $\ge 150$ ms.
- Room reverberation tails and acoustic echoes exceeding 250 ms post-phonation are excluded from the core event duration.

### 2.3 Event Duration Brackets
- **Ultra-Short (< 0.50 s):** Startle shrieks, gasp-screams, brief sudden vocal bursts.
- **Short (0.50 s – 0.99 s):** Brief terror shrieks, acute fright vocalizations, acute pain screams.
- **Moderate (1.00 s – 1.99 s):** Standard distress screams, prolonged fright yells.
- **Sustained ($\ge 2.00$ s):** Extended wailing, panic screams, siren-like vocal cries.

---

## 3. Fine-Grained Vocal Event Taxonomy

All acoustic recordings in the evaluation dataset are classified into deterministic categories:

```
                                  Acoustic Event
                                        |
                 +----------------------+----------------------+
                 |                                             |
             Vocal Signal                              Non-Vocal Sound
                 |                                             |
         +-------+-------+                             +-------+-------+
         |               |                             |               |
    Scream-Like       Non-Scream                    Tonal           Transient
         |               |                             |               |
   +-----+-----+   +-----+-----+                 +-----+-----+   +-----+-----+
   |     |     |   |     |     |                 |           |   |           |
Startle Terror Mask  Shout Cheer Infant            Siren      Synth Whistle Impact
```

### 3.1 Positive Class (Scream Category)
1. **Startle Shriek (`startle_shriek`):**
   - High fundamental frequency jump ($F_0 > 550$ Hz for adult female/child; $F_0 > 400$ Hz for adult male).
   - Extremely rapid attack time ($\le 40$ ms).
   - Duration $< 0.65$ s.
   - Non-linguistic; high spectral turbulence and roughness.
2. **Brief Terror Scream (`brief_terror_scream`):**
   - Duration between 0.65 s and 1.00 s.
   - Distinct subharmonic bifurcation ($F_0/2$, $F_0/3$) and deterministic chaos (vocal turbulence).
   - Prominent resonance band between 1.5 kHz and 3.5 kHz.
3. **Sustained Scream (`sustained_scream`):**
   - Duration $\ge 1.00$ s.
   - Continuous vocal fold desynchronization or severe hyperphonation.
4. **Masked Brief Scream (`masked_brief_scream`):**
   - Genuine scream vocalization embedded in real-world ambient background (festival crowd, music, or stadium reverberation).

### 3.2 Negative Class (Non-Scream Categories)
1. **Shouted Exclamation (`shouted_exclamation`):**
   - Intentional linguistic utterance (e.g. "HEY!", "STOP!", "NO!").
   - Duration $< 0.80$ s.
   - Harmonic regularity; preserved vowel formant tracks; low subharmonic chaos.
2. **Excited Yelling (`excited_yelling`):**
   - Duration $\ge 0.80$ s; cheering or sporting vocalization with periodic pitch contour.
3. **Crowd Cheer Cadence (`crowd_cheer_cadence`):**
   - Synchronized group chanting, countdowns, stadium singing.
4. **Infant Cry Burst (`infant_cry_burst`):**
   - High pitch ($F_0 > 450$ Hz) but characterized by regular crying pauses, rhythmic respiration, and modal harmonics.
5. **Whistle Transient (`whistle_transient`):**
   - Narrowband spectral line ($Q > 10$), near-zero subharmonic energy, duration 50–500 ms.
6. **Siren Pulse (`siren_pulse`):**
   - Periodic harmonic series; continuous frequency modulation without turbulence.
7. **Environmental Transient (`environmental_transient`):**
   - Fireworks, glass breakage, microphone pops, metallic clangs.

---

## 4. Ambiguity Taxonomy & Binary Quarantine Rules

Safety-critical evaluation requires strict ground-truth purity. Mixed or ambiguous vocalizations degrade classifier calibration.

### 4.1 Ambiguity Categories
- `AMBIGUOUS_EXCITEMENT`: Vocalizations containing mixed joyous shrieking (e.g. roller coaster screams, victory yells) where fear vs. joy cannot be objectively determined.
- `AMBIGUOUS_LAUGHTER`: Convulsive high-pitched laughter transitioning into gasping vocalizations.
- `AMBIGUOUS_THEATRICAL`: Highly stylized stage or horror-movie acting without physiological vocal turbulence.

### 4.2 Quarantine Contract
Any recording assigned an `AMBIGUOUS_*` status is:
1. Retained in the audit log with full provenance and timestamp annotations.
2. **Strictly quarantined from primary binary acceptance gate computations** ($\text{Recall} \ge 96\%$, $\text{FPR} \le 5\%$).
3. Evaluated only in secondary "stress-test / sensitivity" reporting tables to observe model behavior under operational ambiguity.

---

## 5. Masking and Background Conditions

### 5.1 Masking Severity Levels
- `CLEAN_ISOLATED`: SNR $\ge +18$ dB. Target sound is dominant with negligible interfering noise.
- `PARTIAL_MASKED`: SNR between $0$ dB and $+18$ dB. Target sound is audible alongside recognizable ambient festival or crowd noise.
- `HEAVY_MASKED`: SNR $< 0$ dB. Target vocalization is submerged beneath loud music, stadium roars, or machinery; energy peaks barely cross the local threshold.

### 5.2 Background Condition Environment
- `STUDIO_CLEAN`: Anechoic or dry booth recording.
- `REVERBERANT`: Enclosed hall, gymnasium, or indoor venue ($RT_{60} > 1.2$ s).
- `CROWD_NOISE`: Open-air festival, carnival, fairgrounds, or street party.
- `STADIUM`: High-volume stadium, concert arena, or dense sporting venue.

---

## 6. Source-Group Disjointness and Provenance Contract

To prevent data leakage and inflated cross-validation metrics:
1. **Source Group Integrity:** A `source_group_id` represents an individual human speaker, unique recording session, or specific online uploader.
2. **Zero Cross-Split Leakage:** Every `source_group_id` must reside in **exactly one split** (`train`, `val`, or `test`). No uploader or recording session may appear across multiple partitions.
3. **Historical Test Isolation:** Historical Stage 5 test sources remain strictly partitioned in the held-out test cohort and must never enter feature selection, scaling, or training pipelines.
4. **License Compliance:** Every audio recording must possess a verifiable permissive commercial license (CC0 1.0, CC BY 3.0, CC BY 4.0, or Public Domain). No CC BY-NC, CC BY-NC-ND, or Sampling+ licenses are admitted.
