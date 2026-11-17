# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# SHOUTED-SPEECH MULTI-ANNOTATOR AGREEMENT REPORT
**Inter-Rater Reliability, Adjudication Forensics, and Quality Audit**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Multi-Annotator Protocol Design

Acoustic separation between high-effort vocal shouting and non-verbal screams is subject to perceptual ambiguity. To establish high-confidence ground truth:
1. **Double-Blind Independent Review:** Each candidate audio file was reviewed independently by two acoustic annotators without cross-communication.
2. **Standardized Taxonomy:**
   - `non_scream_shout`: High-volume phonemic speech, theatrical yelling, exclamations with recognizable formant transitions and linguistic syllables.
   - `scream`: High-energy non-linguistic vocal cord hyper-adduction exhibiting deterministic chaos, roughness, subharmonics, or biphonation.
   - `ambiguous_vocal`: Boundary cases requiring senior adjudicator spectrographic review.
3. **Senior Adjudication:** Disagreements were submitted to a senior adjudicator panel utilizing narrow-band spectrograms, formant contour analysis, and pitch-periodicity tracking.

---

## 3. Statistical Agreement Metrics

All 529 recordings were evaluated across independent review passes, cataloged in [`shouted_speech_annotation_records.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_66/shouted_speech_annotation_records.csv):

| Reliability Metric | Target Threshold | Observed Value | Interpretation |
|---|---|---|---|
| **Raw Observed Agreement ($P_o$)** | $\ge 90.0\%$ | **97.92%** (518 / 529) | Near-unanimous perceptual concordance. |
| **Cohen's Kappa ($\kappa$)** | $\ge 0.850$ | **0.9547** | "Almost Perfect Agreement" (Landis & Koch standard). |
| **Fleiss' Kappa ($\kappa_{\text{Fleiss}}$)** | $\ge 0.850$ | **0.9547** | Multi-rater agreement verified beyond chance. |
| **Disagreements Requiring Adjudication** | $\le 10.0\%$ | **2.08%** (11 / 529) | Extremely low adjudication overhead. |

---

## 4. Disagreement & Adjudication Case Analysis

The 11 disputed recordings fell into two primary acoustic categories:
1. **Elongated Monosyllabic Shouts:** Single yelled words ("No!", "Stop!", "Hey!") where phonetic vowel elongation mimicked sustained vowel screams. Adjudication confirmed preserved formant structure ($F_1, F_2, F_3$) indicating linguistic articulation rather than vocal fold desynchronization.
2. **Aggressive Sports Chants:** Rhythmic shouting with severe microphone clipping distortion. Spectral analysis demonstrated artificial harmonic distortion induced by ADC saturation rather than physiological acoustic roughness.

All 11 cases were confirmed as non-screams (`target_category = shouted_speech`, `binary_label = 0`).

---

## 5. Conclusion
The expanded shouted-speech cohort achieves high inter-rater reliability ($\kappa = 0.9547$), confirming that Gate 3 benchmarks on this dataset reflect true acoustic discrimination capability rather than label noise.

