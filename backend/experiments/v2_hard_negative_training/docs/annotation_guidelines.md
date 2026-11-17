# Acoustic Annotation Guidelines: Experimental Dataset v2 (Stage 8.9.7 Revision)

**Document Reference:** `EXP-V2-ANN-002` (Supersedes `EXP-V2-ANN-001`)  
**Target Application:** Festival Scream Detector  
**Scope:** Dataset Acquisition, Forensic Relabeling, and Leakage-Resistant Dataset Preparation  
**Effective Date:** 2026-10-29  

---

## 1. Objective and Principles

These revised annotation guidelines establish explicit, acoustically grounded criteria for annotating audio recordings in the `backend/experiments/v2_hard_negative_training/` workspace. 

The primary objective is to separate true human emergency screams from high-energy acoustic confounders (shouted speech, unison crowd chants, countdown roars, referee whistles, pyrotechnic screeches, sirens, and infant crying) without contaminating the ground-truth boundary.

### Core Principles
1. **Acoustic Evidence Over File Names:** Metadata tags, file names, and automated triage labels are hints, never ground truth. Annotation decisions must be based on auditory inspection and spectrogram/formant features.
2. **Preservation of Uncertainty:** Ambiguous vocalizations (e.g., groans, mixed laughter/screams, smothered shrieks) must **never** be forced into binary positive or negative categories. They are designated `AMBIGUOUS` and quarantined from binary training.
3. **Phonetic vs Non-Phonetic Articulation:** The boundary between screaming and shouted speech is defined primarily by linguistic vowel/consonant articulation versus non-linear vocal fold saturation.
4. **Holistic Acoustic Context Over Rigid Frequency Cutoffs:** Fundamental frequency ($F_0$) is **supporting evidence**, not a mandatory inclusion or exclusion threshold.

---

## 2. Fundamental Frequency ($F_0$) Rule Correction

> [!IMPORTANT]
> **REVISION TO FUNDAMENTAL FREQUENCY GUIDELINE:**
> The earlier draft suggested $F_0 > 600\text{ Hz}$ as a hallmark of screams. Validation testing during Stage 8.9.6 demonstrated that low-register adult male screams frequently exhibit fundamental frequencies between $350\text{ Hz} - 550\text{ Hz}$ while generating intense acoustic roughness and energy in the upper formant regions ($1.5 - 3.5\text{ kHz}$).
> 
> **Rule:** An $F_0 > 600\text{ Hz}$ cutoff must **never** be used as a mandatory filter to reject legitimate screams. High pitch is supporting evidence for female and child screams, but low-register screams must be recognized through non-linear acoustic phenomena and vocal tract saturation.

---

## 3. Seven-Class Taxonomic Decision Criteria

```
                        Acoustic Input
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
       Human Vocalization            Non-Vocal Sound
               │                             │
       ┌───────┴───────┐             ┌───────┴───────┐
       ▼               ▼             ▼               ▼
Single Voice      Crowd / Choir  Acoustic Confounder Environmental
       │               │             │               │
  ┌────┴────┐     CROWD_CHANT   NON_VOCAL_SOUND  GENERAL_ENV
  ▼         ▼     (Countdown,   (Whistle, Siren, (Music, Wind,
Scream    Speech   Applause)     Fireworks, SFX)  Foliage, Room)
```

### Class 1: `CLEAR_HUMAN_SCREAM` (Binary Label: `scream`)
- **Definition:** An unconstrained, high-intensity non-verbal human vocalization produced during intense fear, pain, panic, surprise, or physical distress.
- **Acoustic Hallmarks:**
  - Rapid acoustic attack time ($< 100\text{ ms}$).
  - Evidence of vocal fold non-linear phenomena: subharmonics, deterministic chaos, biphonation, or acoustic roughness ($30 - 150\text{ Hz}$ modulation rate).
  - Open vocal tract formant dispersion (widened F1/F2 resonant bandwidths extending into $1.5 - 3.5\text{ kHz}$).
  - Absence of articulated phonetic speech (words or syllables).
  - $F_0$ typically elevated relative to speaker baseline ($350 - 550\text{ Hz}$ for adult males; $600 - 2500\text{ Hz}$ for females/children), but pitch alone does not define the class.
- **Inclusion Criteria:** Clean solo screams, screams masked by background crowd or music where the scream transient is audibly perceptible, and fear/panic screams.

### Class 2: `SHOUTED_SPEECH` (Binary Label: `non_scream`)
- **Definition:** High-effort, high-amplitude vocalization produced to project speech across distance or in noisy environments (e.g., stage calls, gaming rage, sports commands).
- **Acoustic Hallmarks:**
  - Clear phonetic articulation: discrete consonants (plosives, fricatives) and vowel transitions forming recognizable words.
  - Periodic harmonic pitch contours ($F_0$ typically between $200\text{ Hz} - 450\text{ Hz}$).
  - Cadence and prosody consistent with spoken language rather than continuous vocal fold saturation.
- **Critical Distinction:** Even if shouted with extreme vocal strain and elevated pitch (e.g., "GET OFF ME!", "WHAT ARE YOU DOING!"), if discrete words are articulated, the clip is classified as `SHOUTED_SPEECH`, **not** `CLEAR_HUMAN_SCREAM`.

### Class 3: `CROWD_CHANT_OR_COUNTDOWN` (Binary Label: `non_scream`)
- **Definition:** Collective unison shouting or vocalization from sports crowds, stadium audiences, or concertgoers (e.g., countdown chants "5, 4, 3, 2, 1!", unison chorus singing, roaring applause).
- **Acoustic Hallmarks:**
  - Diffuse, reverberant acoustic energy with high spatial spread.
  - Summed multi-voice speech formants and collective linguistic cadence without an isolated individual scream transient.
- **Audit Case Study (`fsd50k_349401`):** In the Stage 8.9.3 human review, this recording ("The crowd shouted Countdown") was labeled `SCREAM_PRESENT`. Stage 8.9.4 acoustic forensics confirmed it consists of dozens of voices shouting numbers in unison with hall reverberation, activating YAMNet `Speech` (0.54) and `Crowd` (0.04), with `Screaming` activation at only 0.0059. In the versioned experimental manifest, this recording is reclassified as `CROWD_CHANT_OR_COUNTDOWN` (`non_scream`). The original SQLite review database remains unaltered.

### Class 4: `INFANT_CRYING` (Binary Label: `non_scream`)
- **Definition:** Vocalizations of infants or toddlers (< 2 years) expressing discomfort, hunger, fatigue, or temper tantrums.
- **Acoustic Hallmarks:**
  - Repetitive, cyclic inspiratory/expiratory rhythm (cry bursts separated by sharp inhalation gasps).
  - High pitch ($F_0 \approx 400 - 800\text{ Hz}$), occasionally exhibiting subharmonic screeching.
- **Edge Case Resolution:** If an infant produces continuous, non-rhythmic shrieking that cannot be differentiated from general distress screaming without visual confirmation, flag as `OTHER_DISTRESS_VOCALIZATION` (`AMBIGUOUS`).

### Class 5: `OTHER_DISTRESS_VOCALIZATION` (Binary Label: `ambiguous` — Quarantined)
- **Definition:** Non-scream vocal distress or borderline vocalizations including groans, moans, heavy sobbing, retching, or smothered cries.
- **Handling:** Assigned review status `AMBIGUOUS`. Quarantined from binary training loss and evaluation until consensus review.

### Class 6: `NON_VOCAL_SOUNDS` (Binary Label: `non_scream`)
- **Definition:** Mechanical, synthetic, pyrotechnic, or acoustic non-vocal sounds that mimic high-frequency scream formants.
- **Subtypes:**
  - *Whistles & Squeaks:* Narrowband sinusoids ($1.5 - 4\text{ kHz}$) with rapid transients (pea whistles, brake squeals).
  - *Sirens & Alarms:* Periodic frequency-modulated sweeps.
  - *Fireworks:* Whistling rocket screeches followed by detonations.
  - *Synthesizers:* Resonant electronic leads with portamento.

### Class 7: `GENERAL_ENVIRONMENTAL` (Binary Label: `non_scream`)
- **Definition:** Baseline festival ambiance: music, wind, low rumble, footsteps, engine noise, and general outdoor noise.

---

## 4. Masked and Distant Scream Augmentation Protocol

To evaluate and train against the crowd-masking failure mode:
- **Source Material:** Only verified `CLEAR_HUMAN_SCREAM` recordings and authentic crowd noise beds (`CROWD_CHANT_OR_COUNTDOWN` or `GENERAL_ENVIRONMENTAL`).
- **Mixing Protocol:**
  $$y(t) = s(t) + \alpha \cdot n(t)$$
  Where $\alpha$ achieves controlled Signal-to-Noise Ratios: $+12\text{ dB}$, $+6\text{ dB}$, $0\text{ dB}$, and $-6\text{ dB}$.
- **Source Tracking:** Each synthesized mix inherits the `source_group_id` of the parent scream to guarantee zero leakage between partitions.

---

## 5. Audit Trail and Versioned Relabeling Log

| Recording ID | Original Database Label | Experimental Label | Rationale | Audit Trail Reference |
| :--- | :--- | :--- | :--- | :--- |
| `fsd50k_349401` | `SCREAM_PRESENT` (Original DB intact) | `crowd_chant_cheering` (`non_scream`) | Forensically verified collective unison crowd countdown shouting; lacks individual scream transient. | Stage 8.9.4 Section 3; Stage 8.9.5 Manifest v2 |
| `fsd50k_343949` | `AMBIGUOUS` (Original DB intact) | `ambiguous` (Quarantined) | Muffled shout / groan overlapping let's play video audio. | Stage 8.9.5 Manifest v2 |
| `fsd50k_343960` | `AMBIGUOUS` (Original DB intact) | `ambiguous` (Quarantined) | Vocal grunting / strained effort without clear panic scream. | Stage 8.9.5 Manifest v2 |
| `fsd50k_349386` | `AMBIGUOUS` (Original DB intact) | `ambiguous` (Quarantined) | Low-fidelity vocal shriek in background noise. | Stage 8.9.5 Manifest v2 |
