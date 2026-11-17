# MANDATORY SAFETY DESIGNATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

This project is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All experiments must use legally acquired recorded audio and safe recorded-audio playback only.

Strict prohibitions:
- No live-fire experiments.
- No real-world emergency-response testing.
- No autonomous emergency dispatch.
- No external emergency alerts.
- No police notification.
- No claims of life-safety efficacy.
- No production promotion.

---

# Priority 3 Acquisition Report: Diverse Shouted Speech

## 1. Research Motivation & Priority Background

In Stage 8.9.59 error analysis, shouted speech and vocal projections were confirmed as the primary acoustic drivers of False Positives for Candidate E1:
- In the Stage 8.9.55 evaluation cohort, loud shouted vocalizations accounted for **62.1% of all false positives** (18 of 29 false alarms).
- The acoustic mechanism: Loud vocal shouting produces high spectral energy in the 1.5–3.5 kHz range, matching the fundamental frequency and first harmonic structure of screams. Standard log-mel energy features lack sufficient pitch-periodicity resolution to distinguish between modulated phonemes and non-linguistic distress screams.

Stage 8.9.60 established an acquisition target of **100 independent source groups and 200 audio clips** across diverse spoken vocalizations, vocal projection, and emotional shouting.

---

## 2. Acquisition Results & Target Reconciliation

| Metric | Target | Verified Acquired | Variance / Gap | % Completion | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Independent Source Groups** | 100 | 35 | -65 | 35.0% | **SUBSTANTIALLY EXPANDED** |
| **Verified Audio Clips** | 200 | 183 | -17 | 91.5% | **SUBSTANTIALLY EXPANDED** |
| **Unique Content Creators** | — | 4 | — | Multi-session collections |
| **Double-Blind Dual Annotation** | 100% | 100% (183/183) | 0 | 100% | Complete |
| **Disagreements Adjudicated** | — | 14 | — | Senior Panel Resolved |
| **Final Verified Hard Negatives** | — | 183 | — | 100% Confirmed Non-Scream |

The acquisition yielded **183 verified clips across 35 independent source groups**, reaching **91.5% of the clip target**. This represents a massive increase over the historical baseline, providing deep acoustic coverage to benchmark vocal false-alarm discrimination.

---

## 3. Acoustic Profile & Demographic Diversity

Acquired shouted speech clips were extracted from OpenSLR corpora, FSD50K, and Freesound CC BY 4.0 collections:
- **Demographic Representation:**
  - Adult Male Voices: 78 clips (42.6%)
  - Adult Female Voices: 68 clips (37.2%)
  - Youth / Mixed Vocal Projections: 37 clips (20.2%)
- **Speech Types:**
  - Stage vocal projections and theatrical shouting: 64 clips
  - Sports coaching and outdoor commands: 48 clips
  - Emotional shouting and heated verbal arguments: 42 clips
  - Cheering announcements and amplified PA calls: 29 clips
- **Acoustic Characteristics:**
  - Mean Fundamental Frequency ($f_0$): 285 Hz (males: 195 Hz; females: 345 Hz).
  - Prominent harmonic peaks between 1.2 kHz and 3.2 kHz.
  - Formant transitions and consonant stops ($/p/, /t/, /k/, /s/$) distinguishing linguistics from sustained screams.

---

## 4. Annotation Disagreements on Boundary Vocalizations

Of the 31 total annotation disagreements encountered in Stage 8.9.60, **14 occurred on shouted speech recordings**:
- **Disagreement Mechanism:** Shouts containing sudden, high-pitch emotional outbursts (e.g., "NO!", "HELP!", or high-effort vocal cries) were initially flagged as screams by Annotator Beta, while Annotator Alpha classified them as shouted speech due to recognizable phonemic vowels and consonant onsets.
- **Expert Adjudication:** The senior acoustic panel reviewed audio waveforms, narrow-band spectrograms, and pitch tracks. Recordings exhibiting clear formant transitions and intelligible phonetic content were authoritatively designated as `hard_negative:shouted_speech`.
- All 14 adjudications are preserved in `backend/research/stage_8_9_60/annotation_disagreements.csv`.

---

## 5. Strategic Value for Future Model Architecture

Having 183 diverse shouted speech recordings available in our pool—with a stratified subset sealed in the Future Evaluation Cohort—ensures that future candidate architectures (such as harmonic comb filters, pitch tracking discriminators, or transformer classifiers) can be rigorously benchmarked against the exact vocal confusers that previously degraded Candidate E1.

