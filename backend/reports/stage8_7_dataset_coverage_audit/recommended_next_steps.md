# Recommended Next Steps: Minimal Actionable Data-Collection Plan

**Project:** AI-Powered Festival Scream Detection System (`festival-scream-detector`)  
**Date:** October 24, 2026  
**Author:** Senior Machine Learning & Audio Signal Processing QA Lead  
**Scope:** Stage 8.7 — Actionable Hard-Negative Expansion Strategy  

---

## 1. Executive Strategy: High-Leverage Minimal Data Collection

The Stage 8.7 audit confirmed that the current training set of 1,045 non-scream clips is heavily dominated by clean studio nonverbal vocalizations (OpenSLR 99) and domestic Foley sound effects (NIGENS). Critical festival acoustic phenomena—such as **rave whistles**, **crowd cheering**, and **EDM synthesizers**—are virtually **absent** (only 1 cheering clip and 1 human whistle exist in training).

Rather than indiscriminately scraping thousands of noisy YouTube clips from AudioSet, the most effective, lawful, and reproducible strategy is to collect a **targeted batch of 80 to 125 high-quality, human-reviewed audio recordings**.

```
Targeted 80-125 Clip Collection Plan:
├── 25-35 Whistle & Squeak Recordings (Direct Stage 5 FP Remediation)
├── 30-50 Crowd Cheering & Applause Recordings (Primary Festival Background)
└── 25-40 EDM Synthesizer Risers & Bass Drops (Electronic Music Ambience)
```

---

## 2. Top Three Highest-Priority Next Actions

### Priority Action 1: Whistles & High-Pitched Acoustic Squeaks (25–35 Clips)
- **Why It Matters:**  
  Stage 5 false positive analysis proved that whistles and squeaks represent the highest-confidence false alarms in the entire system:
  - `ZipCartoon+HB02_55_8.wav` (slide whistle): **0.9328 probability** (+0.5828 margin over threshold).
  - `Toy+6080_61_2.wav` (squeaky dog toy): **0.8703 probability** (+0.5203 margin over threshold).
- **Current Training Representation:**  
  Only 1 human mouth whistle and 0 squeaky toys exist in the Stage 4 training set.
- **Recommended Source:**  
  - 15 physical whistle and squeak recordings captured locally using Stage 8.6 [`record_evaluation_audio.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/record_evaluation_audio.py).
  - 15 curated Creative Commons Zero (`CC0`) clips from Freesound.org (rave whistles, referee whistles, dog toys).
- **Target Count:** **25–35 independent source recordings**.

---

### Priority Action 2: Festival Crowd Cheering & Stadium Applause (30–50 Clips)
- **Why It Matters:**  
  Crowd cheering is ubiquitous at live music events. Currently, the training set contains **exactly ONE cheering clip** (`CHEERING-ARENA_GEN-HDF-07312.wav`) and **ZERO applause clips**. A festival scream detector will inevitably produce false alarms at stage drops and set climaxes without negative examples of dense crowd cheering.
- **Current Training Representation:**  
  1 single arena cheer clip out of 1,045 training negative clips (0.09%).
- **Recommended Source:**  
  - Freesound.org: Search tags `crowd-cheer`, `applause-stadium`, `concert-crowd` under `CC0` and `CC BY 4.0`.
- **Target Count:** **30–50 independent source recordings**.

---

### Priority Action 3: EDM Synthesizers, Bass Drops & Pitch Risers (25–40 Clips)
- **Why It Matters:**  
  Electronic festival music features sawtooth lead synths, pitch-bending risers, and aggressive frequency sweeps that climb into the 1,500–3,500 Hz vocal formant range. Currently, the dataset contains **zero electronic music** (only 42 solo piano notes and 3 acoustic guitar loops).
- **Current Training Representation:**  
  0 EDM, 0 synthesizers, 0 bass drops.
- **Recommended Source:**  
  - Royalty-free music production stem packs and Freesound synth leads (`CC0` / `CC BY`).
- **Target Count:** **25–40 independent source recordings**.

---

## 3. Operational Workflow for Ingestion & Review

All new recordings must flow strictly through the existing Stage 6 and Stage 8.6 verification pipelines before any future retraining experiment:

```powershell
# Step 1: Place candidate WAV files into the Stage 6 ingestion directory
# Path: backend/dataset/raw/hard_negatives/

# Step 2: Run Stage 6 Ingestion & Duplicate Auditing
cd C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend
.\.venv\Scripts\python.exe scripts\ingest_hard_negatives.py

# Step 3: Launch Human Listening & Review CLI
.\.venv\Scripts\python.exe scripts\review_hard_negatives.py --interactive

# Step 4: Verify that all approved clips carry explicit licensing tags
# (CC0 1.0 or CC BY 4.0; non-commercial must be flagged)
```

---

## 4. Strict Protocol Reminders

1. **No Model Retraining in This Stage:**  
   The Stage 5 baseline model (`scream_classifier.joblib`), metadata, and threshold (`0.35`) remain completely frozen.
2. **Untouched Historical Test Split:**  
   New recordings must reside strictly in the Stage 6 candidate pool or Stage 8.6 evaluation cohort. They must never be injected into historical Stage 4 split manifests or historical evaluation reports.
3. **No Automatic Ingestion:**  
   Every audio file must undergo human listening verification using [`review_hard_negatives.py`](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/scripts/review_hard_negatives.py) to prevent label noise and class leakage.
