# Stage 6 Hard-Negative Expansion & Acoustic Robustness Plan

**AI-Powered Festival Scream Detection System — Strategy & Protocol Specification**

---

## 1. Executive Summary

In Stage 5, our lightweight scream classifier achieved strong baseline results on clean held-out test audio (ROC-AUC **0.9960**, PR-AUC **0.9644**, Recall **89.47%**, Precision **80.95%** at threshold $\tau = 0.35$). However, detailed error analysis identified four specific false positives:
1. High-intensity infant crying ($P = 0.9355$).
2. Cartoon slide whistle ($P = 0.9328$).
3. Squeaky dog toy transient ($P = 0.8703$).
4. Electronic phone ringing warble ($P = 0.4062$).

Furthermore, a euphoric joy vocalization (*"vocal joy and excitement"*) was missed as a false negative ($P = 0.0237$).

In a live festival setting, sound reinforcement systems produce sustained sound pressure levels exceeding 100 dB(A), punctuated by sharp whistles, celebratory crowd cheering, heavy bass drops, and acoustic reflections. 

This document defines the data collection protocol, acoustic taxonomy, licensing constraints, review criteria, and continuous streaming architecture required to harden the detector against real-world festival distractors.

---

## 2. Target Acoustic Distractor Taxonomy

We establish seven prioritized categories for targeted hard-negative collection:

| Priority | Category Name | Acoustic Description | High-Risk Festival Distractor Examples | Target Collection Goal |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | **`festival_whistle`** | Piercing, sustained or modulated sinusoidal tones (2.5 kHz – 4.5 kHz) | EDM rave whistles, referee whistles, vuvuzelas, party noisemakers | 100 clips across $\ge 10$ packs |
| **P2** | **`crowd_cheering`** | Dense, wideband choral vocal energy, euphoric shouting, applause | Stage drop cheers, drop countdowns, synchronized chanting | 80 clips across $\ge 8$ venues |
| **P3** | **`music_and_effects`** | Heavy sub-bass saturation, synthesizer frequency sweeps, distorted vocals | Dubstep bass drops, pitch-shifted MC shouts, PA feedback | 75 clips across $\ge 8$ genres |
| **P4** | **`vocal_non_scream`** | Non-distress human vocalizations sharing physical vocal tract features | Laughter, gasps, coughing, singing, speech yelling, infant crying | 60 clips across $\ge 10$ speakers |
| **P5** | **`sfx_transients`** | Sudden, high-energy acoustic onset without vocal harmonic resonance | Sirens, stage pyrotechnics, bells, car horns, squeaky toys | 50 clips across $\ge 5$ sound packs |
| **P6** | **`environmental_noise`**| Low-frequency turbulence and mechanical microphone artifacts | Wind buffeting on capsule, handling thumps, cable crackle | 40 clips across $\ge 5$ hardware types |
| **P0** | **`genuine_scream`** | Real distress vocalizations across varied ages, genders, distances | Distant screams, muffled screams, female/male panic vocalizations | 50 clips across $\ge 15$ new speakers |

---

## 3. Licensing, Provenance & Legal Constraints

### Existing Baseline Licenses (OpenSLR 99 & NIGENS)
* Both datasets were ingested under **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)**.
* **Legal Implications**:
  1. **NonCommercial (NC)**: Models trained on these datasets cannot be deployed in commercial products, sold to venue operators, or embedded in commercial security systems without direct commercial licensing.
  2. **NoDerivatives (ND)**: Redistribution of modified audio or derived datasets is restricted.
  3. **Derivative Model Ambiguity**: In many jurisdictions, whether a machine learning model weights file constitutes a derivative work of training data remains legally contentious.

### Ingestion Rules for New Audio
To build towards a legally deployable, open production system, all Stage 6 additions must enforce strict provenance tracking:
1. **Commercial-Safe Tier (Preferred)**:
   * **CC0 1.0 Universal** (Public Domain Dedication).
   * **Creative Commons Attribution 4.0 (CC BY 4.0)** / CC BY 3.0.
   * **Public Domain / US Government Works**.
   * Direct written permission / custom field recording releases.
2. **Research-Only Tier (Restricted)**:
   * **CC BY-NC 4.0** or **CC BY-NC-SA 4.0**.
   * When ingested, the pipeline automatically sets `"commercial_use_permitted": false`.

---

## 4. Human Review & Labeling Protocol

### Pitfalls of Blind Crowd Labeling
A continuous 30-minute festival field recording **must never be blindly labeled non-scream in bulk**. Crowds frequently contain genuine distress incidents, physical altercations, medical emergencies, or minor panic localized in small pockets of the audience. 

### Review Protocol
1. **Audio Slicing**: Long recordings are segmented into discrete 1.0s – 5.0s clips.
2. **Listening Verification**: A human reviewer listens to each candidate clip using `python backend/scripts/review_hard_negatives.py`.
3. **Four-Way Decision Matrix**:
   * `approved_non_scream`: 100% verified non-scream sound.
   * `approved_scream`: Verified genuine distress scream.
   * `rejected_ambiguous`: Acoustic intent is undecidable (e.g. scream buried under loud synth, or joyful scream indistinguishable from panic).
   * `pending_review`: Unreviewed clip. **Strictly excluded from training and validation**.

### Task-Definition Limitation: Valence Ambiguity
In auditory neuroscience, high-arousal negative vocalizations (terror screams) and high-arousal positive vocalizations (euphoric ecstasy shrieks) share overlapping fundamental frequencies ($F_0 > 1000\text{ Hz}$), rough temporal modulations (30–150 Hz roughness), and chaotic phonation. Without visual or semantic context, audio alone cannot guarantee separation between panic and ecstasy. The review protocol mandates tagging ambiguous high-arousal screams as `rejected_ambiguous` to protect ground truth integrity.

---

## 5. From Clip-Level Predictions to Continuous Real-Time Streaming

Evaluating isolated WAV files produces an incomplete picture of festival operational performance. A production festival scream detector operates as a continuous stream processor.

### Clip vs. Stream Discrepancy

| Parameter | Stage 5 Baseline (Clip Evaluation) | Stage 7/8 Target (Continuous Stream) |
| :--- | :--- | :--- |
| **Input Structure** | Isolated, pre-segmented files (1–16s) | Continuous microphone stream (16 kHz float32) |
| **Window Duration** | Full clip or discrete file | 0.975-second rolling window (15,600 samples) |
| **Hop Step** | None (one pooled feature per file) | 0.4875-second hop (7,800 samples, ~50% overlap) |
| **Inference Frequency** | On-demand (1 pass per recording) | **2.05 passes per second** (~7,385 passes / hour) |
| **Acoustic Environment** | Clean, isolated studio / sound effects | Dense acoustic mixture (Music + Crowd + Echo) |
| **False Positive Unit** | False positive count per batch | **False Alarm Events per Hour (FA/hr)** |

### Continuous Streaming Requirements for Stage 7
1. **Temporal Smoothing (Exponential Moving Average / Rolling Majority)**:
   * A single noisy transient frame (e.g. a 50ms microphone cable pop) must not trigger an emergency alert.
   * Require $P(\text{scream}) \ge \tau$ across $\ge 2$ consecutive overlapping frames (1.46 seconds of distress energy).
2. **Alert Cooldown & Debounce**:
   * When an alert is triggered, an event cooldown timer (default: **3.0 seconds**) suppresses duplicate alarms from the same physical vocalization.
3. **Adaptive Noise-Floor Estimation**:
   * Estimate background ambient SPL dynamically to adjust gain and avoid clipping on stage drops.

---

## 6. Prioritized Action Plan for Audio Acquisition

The following specific sound files are prioritized for addition to `data/raw/hard_negatives/`:

| Priority Rank | Sound Type | Suggested Search Terms / Sources | Target Source Groups |
| :--- | :--- | :--- | :--- |
| **1** | Rave & Referee Whistles | Freesound: `rave whistle`, `fox 40`, `stadium whistle` (CC0 / CC BY) | $\ge 5$ authors |
| **2** | Concert Crowd Cheering | Freesound / OpenSound: `festival crowd`, `stage drop cheer`, `applause outdoor` | $\ge 4$ festivals |
| **3** | Bass Drops & Synth Risers | Synthesized EDM drops, risers, white noise sweeps | $\ge 4$ producers |
| **4** | Human Laughter & Crying | Freesound: `baby crying`, `hysterical laughter`, `screaming joy` | $\ge 6$ individuals |
| **5** | Stage Pyrotechnics & Sirens | Freesound: `fireworks whistle`, `distant siren`, `alarm horn` | $\ge 4$ sound packs |
| **6** | Outdoor Wind Pop | Field recordings: `wind microphone pop`, `mic handling noise` | $\ge 3$ mic types |
