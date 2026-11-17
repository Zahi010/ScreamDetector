# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Independent Human Reviewer Handbook & Acoustic Annotation Instructions

**Stage:** Stage 8.9.77 — Independent Human Annotation Execution, Agreement Analysis, Adjudication & Prospective Cohort Qualification  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audience:** Independent Human Audio Reviewers & Acoustic Adjudicators  
**Version:** 1.0 (Standardized Protocol)  

---

## 1. Reviewer Ethics, Safety & Listening Environment

> [!IMPORTANT]
> **Safety & Well-being Notice:** Reviewing intense vocalizations can induce auditory and mental fatigue.
> - Use calibrated, over-ear monitoring headphones set to a comfortable, non-injurious listening SPL ($60\text{--}70\text{ dBA}$).
> - Take mandatory 5-minute auditory rest breaks every 20 minutes of continuous listening.
> - Do not perform labeling tasks in noisy environments or using laptop/mobile speakers.

---

## 2. Core Operational Protocol

For each assigned audio clip:
1. **Initial Blinded Listen:** Listen to the entire audio clip without pause to assess overall acoustic scene.
2. **Detailed Analytical Listen:** Replay the clip, focusing on the focal acoustic event (onset, vocal effort, pitch stability, spectral roughness).
3. **Primary Category Selection:** Select exactly ONE primary category from the 19 standard classes.
4. **Scream Subcategorization (If Applicable):** If `primary_label == "scream"`, select the exact subcategory (Child, Adult High-Intensity, Adult Low-Intensity, Short, Crowd-Masked, Reverberant).
5. **Confidence Rating:** Assign a confidence score from `1` (Uncertain) to `5` (Definite).
6. **Acoustic Environment Tags:** Check all relevant acoustic modifiers (e.g., `distant_low_snr`, `crowd_masked`, `reverberant`).
7. **Free-Text Justification:** If confidence $< 4$ or if the signal is borderline, document the specific acoustic rationale.

---

## 3. Acoustic Discrimination Boundaries

Distinguishing genuine distress/fear screams from acoustically similar non-scream vocalizations is the central challenge of this evaluation. Follow these scientific boundary guidelines:

### 3.1 Scream vs. Shouted Speech
- **Genuine Scream:**
  - Characterized by extreme physiological lung pressure causing non-linear vocal fold dynamics: subharmonic generation, biphonation, frequency jumps, and deterministic chaos (acoustic roughness).
  - High fundamental frequency ($F_0$ typically $> 400$ Hz in adult females, $> 250$ Hz in adult males, $> 500$ Hz in children).
  - Vowel formants are blurred, smeared, or replaced by broadband energy.
- **Shouted Speech:**
  - High acoustic energy, but maintains discrete phonemic structure (clear vowel formants $F_1, F_2$ and consonantal closures / stop bursts).
  - Vocal fold vibration remains predominantly periodic (low chaotic roughness).
  - Semantic content (words, phrases) is discernible.
  - **Decision Rule:** If intelligible words are articulated without severe vocal fry/chaos, classify as `shouted_speech` ($0$), NOT `scream` ($1$).

### 3.2 Scream vs. Infant Crying
- **Infant Cry:**
  - Follows rhythmic, cyclic respiration patterns (respiratory phases: inspiratory gasp, cry phonation, expiratory release).
  - Harmonic pitch contours are melodic, falling-rising, or arc-shaped.
  - Fundamental frequency is elevated ($400\text{--}600$ Hz), but the temporal envelope is repetitive and pulsed.
- **Child / Infant Scream:**
  - Characterized by acute, sustained shrill vocal burst without cyclic infant crying rhythm.
  - **Decision Rule:** Repetitive, undulating infant distress is classified as `infant_cry` ($0$).

### 3.3 Scream vs. Vocal Joy & Athletic Cheering
- **Vocal Joy / Cheering:**
  - High-pitched vocalizations produced during celebrations, roller-coasters, or sports victories ("Woo-hoo!", "Yeah!").
  - Vocal tract is open, relaxed, and resonant without hyper-adduction of false vocal cords.
  - Spectrally clean harmonics without harsh roughness or panic tremors.
  - **Decision Rule:** Upbeat, harmonic celebratory shouts are classified as `cheering_crowd` or `laughter` ($0$).

### 3.4 Scream vs. Whistles, Sirens & Artificial Sounds
- **Whistle / Siren:**
  - Strictly non-vocal acoustic origin.
  - Characterized by narrow spectral bandwidth, pure sinusoidal tone, or mechanical frequency chirps.
  - Complete absence of vocal-tract formants or glottal pulse trains.
  - **Decision Rule:** Classify as `whistle` or `siren` ($0$).

---

## 4. Confidence Rating Definitions

| Score | Descriptive Label | Definition & Acceptance Criteria |
| :---: | :--- | :--- |
| **5** | **Definite / Unambiguous** | Pristine signal clarity; unambiguous acoustic signature matching all class criteria; zero competing interpretations. |
| **4** | **High Confidence** | Focal sound is clearly identifiable despite mild background noise, reverberation, or minor clipping. |
| **3** | **Probable** | Event is audible and identifiable, but moderate masking, distance, or acoustic overlap creates minor ambiguity. |
| **2** | **Low Confidence** | Severe background noise, distortion, or brief duration makes classification uncertain. Flagged for review. |
| **1** | **Uncertain / Ambiguous** | Acoustic identity cannot be determined with scientific confidence. Automatic escalation to adjudication. |

---

## 5. Reviewer Quality Assurance

- **Blinding Integrity:** Do not attempt to de-anonymize recording metadata, search for clips online, or discuss assignments with the second reviewer.
- **Objectivity:** Base decisions strictly on auditory acoustic evidence. Do not assume or extrapolate external danger or context.

