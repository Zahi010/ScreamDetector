# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.62 — Blinded Human Annotation Review Protocol for Short Distress Vocalizations

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Protocol Objective and Purpose

Stage 8.9.61 revealed that short-scream recall remained severely depressed across all evaluated models: Candidate E1 Rolling achieved only 39.13% (27/69), Candidate B Baseline achieved 39.13% (27/69), and Candidate E1 Static achieved 36.23% (25/69). Over 57.97% (40/69) of all short screams were missed by every single candidate.

To determine whether these persistent false negatives stem from algorithmic representation failures or acoustic ambiguity in the ground-truth annotations, this blinded review protocol defines the methodology for human acoustic review of all 69 short-scream recordings ($< 1.0$s duration).

---

## 2. Blinding and Governance Rules

1. **Reviewer Blinding:** Reviewers must not have access to model identity, predicted probabilities, classification labels, or candidate false-negative status during acoustic review.
2. **Audio Randomization:** The 69 short-scream recordings must be presented in a pseudo-randomized sequence intermixed with 30 filler distractors (short non-scream vocalizations such as coughs, laughter, and shouts).
3. **Label Preservation:** Original ground-truth labels (`binary_label = 1`) must never be modified, overwritten, or discarded based on reviewer scores. Reviewer judgments must be recorded in an independent auxiliary audit ledger (`short_scream_human_audit.csv`).
4. **Playback Calibration:** Playback must occur over calibrated studio-monitor headphones at safe, standardized listening volumes (nominally 65–70 dBA).

---

## 3. Acoustic Review Taxonomy and Scoring Schema

For each reviewed recording, the human auditor assigns scores across five standardized dimensions:

### Dimension 1: Auditory Distress Confidence (Primary Categorization)
- **Class 1 — High-Confidence Panic/Pain Scream:** Unmistakable, intense human distress shriek with elevated vocal effort and acoustic roughness.
- **Class 2 — Startle / Surprise Vocalization:** Genuine sudden vocalization (e.g., jump-scare gasp, brief shriek) of brief duration ($< 500$ ms).
- **Class 3 — Exertion / Athletic Grunt or Shout:** Brief high-effort vocalization without panic or distress affect.
- **Class 4 — Playful / Non-Emergency Shriek:** High-pitch vocalization produced during play, laughter, or cheering.
- **Class 5 — Ambiguous / Borderline Vocalization:** Muffled, heavily reverberant, or low-SNR sound where vocal source cannot be verified.
- **Class 6 — Non-Human / Corrupted Audio:** Mechanical squeal, synthetic sound, or unusable corrupted audio.

### Dimension 2: Perceived Duration & Onset Salience
- **Rating 1:** Ultra-short burst ($< 300$ ms).
- **Rating 2:** Short burst ($300 - 600$ ms).
- **Rating 3:** Extended brief vocalization ($600 - 999$ ms).
- **Rating 4:** Sustained tail present ($> 1000$ ms).

### Dimension 3: Acoustic Masking & Background Interference
- **Rating 1 (Clean):** Isolated vocalization with clean silence or minimal background.
- **Rating 2 (Moderate Noise):** Audible environmental ambience (traffic, rain, room reverb) with vocalization distinctly foregrounded.
- **Rating 3 (Heavy Masking):** Vocalization competes with intense music, crowd chatter, or machinery.

### Dimension 4: Recording Dynamic Artifacts
- Binary flags: `Is_Clipped`, `Is_Heavily_Compressed`, `Microphone_Rumble_Present`, `High_Frequency_Attenuated`.

---

## 4. Audit Reporting Deliverables

Upon completion of the blinded listening session, the audit emits:
- `short_scream_human_audit.csv`: Row-level auditor scores for all 69 recordings.
- `short_scream_annotation_agreement.md`: Inter-rater agreement statistics (Fleiss' Kappa) and cross-tabulation against model predictions.
- Identification of "Hard Biological Distress" vs "Acoustic Ambiguity" error proportions.

