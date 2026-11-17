# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — Contrastive Hard-Negative Curation & Governance Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report documents the curation, acoustic property analysis, and governance compliance of the contrastive hard-negative development pool for Stage 8.9.64 Track E.

The complete manifest of 117 curated hard-negative development recordings is recorded in [`contrastive_hard_negative_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/contrastive_hard_negative_metrics.csv).

---

## 2. Dataset Curation & Partition Governance

To prevent benchmark degradation and data leakage:
1. **Zero Sealed-Cohort Leakage:** Every candidate recording was checked against the 700 recordings in the sealed evaluation cohort (`backend/research/stage_8_9_61/sealed_cohort_predictions.csv`). **Zero matches** were found (100% quarantine compliance).
2. **Source-Group Isolation:** All curated hard negatives originate from unexposed development partitions, preserving cluster independence.
3. **Permissive Licensing:** All clips originate from verified CC0, CC-BY, and Freesound-permissive sources.

---

## 3. Acoustic Profile of Contrastive Hard Negatives

The curated development cohort comprises 117 challenging non-scream recordings:

```
Contrastive Negative Profile by Error Class (N = 117)
┌───────────────────────────┬─────────┬───────────────┬──────────────────────┬──────────────────────┐
│ Acoustic Error Class      │ Count   │ Mean HNR (dB) │ Mean Spectral Flat   │ Mean Spectral Flux   │
├───────────────────────────┼─────────┼───────────────┼──────────────────────┼──────────────────────┤
│ environmental_noise       │ 92      │ +0.18 dB      │ 0.01182              │ 1599.34              │
│ friction_squeak           │ 6       │ -0.84 dB      │ 0.00642              │ 2.41                 │
│ chimes_bells_metallic     │ 5       │ +2.45 dB      │ 0.00910              │ 3.82                 │
│ shouted_speech_vocal      │ 5       │ +1.12 dB      │ 0.01420              │ 1.89                 │
│ whistle_pure_tone         │ 4       │ +8.15 dB      │ 0.00755              │ 0.0018               │
│ vehicle_horn_siren        │ 3       │ +3.80 dB      │ 0.00840              │ 0.0042               │
│ environmental_transient   │ 2       │ -1.20 dB      │ 0.01350              │ 4.15                 │
└───────────────────────────┴─────────┴───────────────┴──────────────────────┴──────────────────────┘
```

---

## 4. Weighting & Contrastive Mining Formulation

During contrastive loss optimization, hard negatives belonging to high-risk categories (`whistle_pure_tone`, `shouted_speech_vocal`, `friction_squeak`) are assigned a loss penalty multiplier:
$$w_i = \begin{cases} 2.50 & \text{if candidate } i \in \{\text{whistle, shout, friction squeak}\} \\ 1.00 & \text{otherwise} \end{cases}$$

This asymmetric penalty forces the dual-resolution network's representation manifold to push non-scream transients away from the decision boundary, reducing false alarms without diminishing sensitivity to genuine brief screams.

