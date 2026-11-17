# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.65 — Gate 3 Shouted-Speech False-Positive Rate Audit Report

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

This report documents the restoration and recording-level evaluation of **Gate 3: Shouted-Speech False Positive Rate ($\le 15.0\%$)** across the development cohort.

The recording-level data and physical audio attributes are cataloged in [`gate_3_shouted_speech_audit.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/gate_3_shouted_speech_audit.csv) and summary statistics in [`gate_3_shouted_speech_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/gate_3_shouted_speech_metrics.csv).

---

## 2. Shouted-Speech Definition & Development Cohort Inventory

In the Stage 8.9.63/64 development manifest ($N=312$), non-target vocalizations that trigger scream detector false alarms consist of two accounting subsets:

### 2.1 Nominal Shouted Speech ($N=1$)
- `s60_rec_0332` (`sg_s60_NIGENS_13575`): An isolated victim gasping and non-scream vocal outcry, labeled `target_category == 'shouted_speech'` in manifest metadata.

### 2.2 Forensically Audited Vocal Outcries & Shouted Speech ($N=5$)
Cross-referencing the underlying Freesound/NIGENS annotations revealed four additional high-effort vocal recordings labeled under `environmental_noise`:
1. `s60_rec_0054` (`sg_s60_162880`): Infant crying and loud child vocal outcries ($3.0\,\text{s}$).
2. `s60_rec_0100` (`sg_s60_196156`): Intense sobbing with breath gasps ($1.5\,\text{s}$).
3. `s60_rec_0231` (`sg_s60_350438`): Young children chorus shouting and loud singing ($3.5\,\text{s}$).
4. `s60_rec_0236` (`sg_s60_350452`): Young children group shouting and energetic singing ($4.2\,\text{s}$).
5. `s60_rec_0332` (`sg_s60_NIGENS_13575`): Adult gasping and non-scream vocal outcry ($1.2\,\text{s}$).

Each of these five recordings represents a distinct, unexposed source group ($5$ independent source groups).

---

## 3. Baseline Dual-Resolution Gate 3 Performance

```
Baseline Dual-Resolution Performance on Shouted Speech
┌──────────────────────────────────────┬─────────┬──────────────┬────────┬────────┬──────────┬──────────────────┬────────────┐
│ Accounting Definition                │ Clips   │ SourceGroups │ FP     │ TN     │ FPR      │ 95% Wilson CI    │ Gate Stat  │
├──────────────────────────────────────┼─────────┼──────────────┼────────┼────────┼──────────┼──────────────────┼────────────┤
│ Nominal Manifest (target_category)   │ 1       │ 1            │ 1      │ 0      │ 100.00%  │ [20.6%, 100.0%]  │ FAIL       │
│ Forensically Audited Outcries (N=5)  │ 5       │ 5            │ 5      │ 0      │ 100.00%  │ [56.5%, 100.0%]  │ FAIL       │
└──────────────────────────────────────┴─────────┴──────────────┴────────┴────────┴──────────┴──────────────────┴────────────┘
```

### Forensic Analysis of Baseline Gate 3 Failure:
The Baseline Dual-Resolution model produced false alarms on all five shouted speech recordings ($\text{FPR} = 100.0\%$).
- Mean predicted probability: **$0.8496$** (range: $0.6603$ to $0.9990$).
- Mean short-branch gating weight: **$0.5361$**.
- **Acoustic Mechanism:** High vocal effort during shouting creates severe vocal-fold turbulence, elevated $F_0$ ($> 500\,\text{Hz}$), and nonlinear subharmonics that bypass simple spectral band energy checks.
- Meeting Gate 3 ($\le 15.0\%$) requires active harmonicity discrimination and contrastive negative training.

