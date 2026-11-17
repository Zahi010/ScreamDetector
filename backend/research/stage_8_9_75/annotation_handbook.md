# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Operational Acoustic Annotation Handbook & Taxonomic Guidelines (v1.0)

**Project:** Festival Scream Detector  
**Stage:** 8.9.75  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Handbook Version:** v1.0  
**Effective Date:** 2026-11-14  
**Author:** Audio Annotation Protocol Designer & Research Governance Auditor  

---

## 0. Mandatory Research Safety & Ethical Boundaries

> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This acoustic annotation handbook governs laboratory research annotations only.  
> - **No Life-Safety Inferences:** Acoustic classifications establish statistical acoustic features, NOT legal proof of danger, violence, assault, or distress.  
> - **Ethical Identity Safeguards:** Annotators must NEVER attempt to infer a speaker's personal identity, race, ethnicity, or private personal data from recorded audio.  
> - **Demographic Labels:** Age-related tags (`VOCAL_SCREAM_CHILD`, `INFANT_CRY`) may ONLY be applied when corroborated by lawful, public, lawful uploader metadata and necessary for acoustic feature stratification.

---

## 1. Objectives and Scope

The goal of this handbook is to provide standardized, reproducible, and acoustically rigorous operational definitions for annotating human vocalizations and environmental acoustic distractors.

Historical evaluations in Stages 60–74 revealed that **37.5% of model errors stemmed from ground-truth label ambiguity**, where theatrical shouts, gasps, and infant cries were forced into binary labels without operational definitions. This handbook defines a three-tier taxonomy:
1. **Positive Class:** `SCREAM` (stratified into 6 acoustic subcategories).
2. **Negative Classes:** 17 distinct non-scream categories (including hard-negative distress lookalikes).
3. **Uncertainty Class:** `AMBIGUOUS_VOCALIZATION` (explicit quarantine for borderline recordings).

---

## 2. Positive Class: `SCREAM`

A human vocalization characterized by involuntary or voluntary maximal vocal fold excursion, non-linear phonation dynamics (deterministic chaos, subharmonics, or biphonation), significant auditory roughness in the 30–150 Hz modulation band, and elevated high-frequency spectral energy.

### Subcategories of Screams:

#### Subcategory 1: Adult High-Intensity Scream (`ADULT_HIGH_INTENSITY`)
- **Definition:** Maximal-effort adult screaming during acute fear, startle, or pain.
- **Acoustic Signature:** Fundamental frequency $F_0 \in [350, 1000]$ Hz; auditory roughness $> 0.025$; high-frequency energy ratio ($HF > 0.12$); high spectral flux ($flux > 0.040$).
- **Inclusion Criteria:** Genuine panic shrieks, terror screams, high-intensity startle screams.
- **Exclusion Criteria:** Spoken or shouted words with clear lexical phonemes.

#### Subcategory 2: Adult Low-Intensity / Muffled Scream (`ADULT_LOW_INTENSITY`)
- **Definition:** Suppressed, distant, or low-vocal-effort screams.
- **Acoustic Signature:** $F_0 \in [300, 750]$ Hz; lower total RMS energy; moderate roughness ($0.015$–$0.025$); high frequency attenuation due to distance or obstruction.
- **Inclusion Criteria:** Distant screams, screams muffled by distance or obstacles.

#### Subcategory 3: Child Scream (`CHILD_HIGH_PITCH`)
- **Definition:** High-pitch maximal-effort scream from a prepubescent child ($< 12$ years).
- **Acoustic Signature:** Extremely elevated fundamental frequency $F_0 \in [500, 2000]$ Hz; lower roughness ($0.010$–$0.025$) due to smaller vocal fold mass and wide harmonic spacing; energy concentrated in 1.5–4.0 kHz.
- **Inclusion Criteria:** Startle or play screams with public metadata confirming child vocalization.
- **Exclusion Criteria:** Adult female screams mimicking children.

#### Subcategory 4: Short Scream (`SHORT_STARTLE_UNDER_1S`)
- **Definition:** Abrupt vocal scream with total acoustic duration $< 1.0$ second (down to 250 ms).
- **Acoustic Signature:** Transient attack time $< 80$ ms; short sustained phonation ($0.2$–$0.9$ s); rapid decay.
- **Inclusion Criteria:** Brief startle shrieks, sudden fright vocalizations under 1.0 second.

#### Subcategory 5: Sustained Scream (`SUSTAINED_DISTRESS`)
- **Definition:** Prolonged continuous vocal fold vibration exceeding 1.2 seconds.
- **Acoustic Signature:** Duration $\ge 1.2$ seconds; prolonged subharmonic modulation; sustained chaotic phonation.

#### Subcategory 6: Crowd-Masked Scream (`MASKED_DISTANT`)
- **Definition:** Scream vocalization embedded in heavy outdoor or festival background ambience (SNR $-6$ to $+6$ dB).
- **Acoustic Signature:** Scream peaks penetrate background rumble; prominent Lombard effect (upward pitch and intensity shift).

---

## 3. Negative Classes (17 Mutually Exclusive Categories)

### High-Priority Hard-Negative Vocalizations:

#### 1. `INFANT_CRY`
- **Definition:** Distress, hunger, or pain vocalization from an infant or toddler ($< 2$ years).
- **Acoustic Signatures:** Repetitive rhythmic cry bursts ($1.0$–$2.5$ Hz burst repetition rate), high fundamental frequency ($400$–$600$ Hz), pronounced pitch glide (melody contour), inspiratory gasps between expiratory cries.
- **Boundary Distinction vs Scream:** Cry exhibits cyclic rise-fall melody contour and periodic breath gaps; screams exhibit sudden transient attacks and sustained chaotic broadband noise.

#### 2. `ADULT_CRY`
- **Definition:** Adult weeping, sobbing, or tearful vocalizations.
- **Acoustic Signatures:** Tremulous low-to-moderate $F_0$ ($150$–$350$ Hz), spasmodic glottal pulsing, breathy voice quality, absence of extreme high-frequency roughness.

#### 3. `SHOUTED_SPEECH`
- **Definition:** Maximal-effort linguistic speech where words, sentences, or phonemes are intelligible.
- **Acoustic Signatures:** Preserved formant structure ($F_1, F_2, F_3$ vowel transitions), consonantal stops and fricatives, lower auditory roughness ($< 0.018$), pitch generally $< 400$ Hz in adult males and $< 500$ Hz in adult females.
- **Boundary Rule:** If intelligible linguistic words are pronounced ("HEY", "STOP", "OVER HERE"), classify as `SHOUTED_SPEECH`, even if volume is extreme.

#### 4. `THEATRICAL_SHOUT`
- **Definition:** Staged dramatic acting, radio drama performance, or voice acting shouts.
- **Acoustic Signatures:** Modulated vibrato, controlled vocal fold closure, theatrical projection without physiological autonomic tremor.

#### 5. `EXCITED_CHEER`
- **Definition:** Positive high-energy celebratory vocalizations from individuals or groups.
- **Acoustic Signatures:** Upward intonation contours, shared vowel resonances, absence of panic dissonance.

#### 6. `CROWD_CHANT`
- **Definition:** Rhythmic unison vocalizations from stadium or festival crowds.
- **Acoustic Signatures:** Low collective spectral flux, periodic cadence ($0.5$–$1.5$ Hz), low harmonic roughness.

#### 7. `SINGING`
- **Definition:** Sustained musical vocalization with pitch tracked to musical notes.
- **Acoustic Signatures:** High harmonicity-to-noise ratio ($HNR > 15$ dB), controlled pitch stability, vibrato.

#### 8. `LAUGHTER`
- **Definition:** Spasmodic paroxysmal exhalations during mirth.
- **Acoustic Signatures:** Chopped vowel bursts ($4$–$6$ Hz burst rate), low auditory roughness, falling pitch trajectory.

#### 9. `GASP`
- **Definition:** Sudden sharp intake of breath or startled inspiratory phonation.
- **Acoustic Signatures:** Predominantly unvoiced turbulent airflow, duration $< 0.5$ seconds, absence of periodic phonation.

### Non-Vocal Acoustic Distractors:

#### 10. `WHISTLE`
- **Definition:** High-frequency tonal whistles (sports referee whistle, pea whistle, human whistling).
- **Acoustic Signatures:** Intense narrow-band tonal peak in 2.0–4.5 kHz; extremely low roughness ($< 0.005$); high $HNR$.

#### 11. `SIREN`
- **Definition:** Emergency vehicle electronic or mechanical sirens.
- **Acoustic Signatures:** Periodic frequency-modulated chirps (wail, yelp) sweeping 500–1800 Hz.

#### 12. `ANIMAL_VOCALIZATION`
- **Definition:** Dogs barking, birds screeching, cats howling.

#### 13. `ENVIRONMENTAL_ALARM`
- **Definition:** Fire alarms, industrial buzzers, intrusion sirens.

#### 14. `MECHANICAL_SOUND`
- **Definition:** Fairground rides, machinery squeals, brake squeal, metal friction.

#### 15. `MUSIC`
- **Definition:** Heavy bass, amplified stage audio, synthesizer tones, drums.

#### 16. `AMBIENT_NOISE`
- **Definition:** Wind noise, rain, general crowd murmur, foot traffic.

#### 17. `OTHER_NON_SCREAM`
- **Definition:** Any acoustic event not matching positive scream criteria and not covered by above 16 categories.

---

## 4. Uncertainty Class: `AMBIGUOUS_VOCALIZATION`

A recording MUST be labeled `AMBIGUOUS_VOCALIZATION` if:
1. It contains a blend of scream and non-scream traits (e.g. half-gasp half-shriek) where annotators cannot confidently determine category.
2. The recording has heavy background distortion, clipping, or low SNR making acoustic features indiscernible.
3. The vocalization is a borderline theatrical scream where genuine distress cannot be established.

> [!IMPORTANT]
> **No Forced Binary Choices:** Annotators must NEVER guess or flip a coin. Labeling ambiguous audio as `AMBIGUOUS_VOCALIZATION` preserves dataset purity and prevents corrupting benchmark evaluations.

