# HARD-NEGATIVE DATASET QUALITY REPORT
## Composition, Category Distribution, Acoustic Triage and Quality Control

**Project:** Festival Scream Detector  
**Stage:** 8.9.32 — Hard-Negative Engineering  
**Auditor:** Audio ML Research & Signal Processing Specialist  
**Manifest:** [`hard_negative_dataset_manifest.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_32/dataset/hard_negative_dataset_manifest.csv)  
**Total Hard Negative Recordings:** **926**  
**Total Source Groups:** **364**  
**Date:** November 2, 2026

---

## 1. Executive Summary & Dataset Composition

The Stage 8.9.32 hard-negative dataset consolidates 926 physically verified, permissive audio recordings specifically targeting the acoustic confusers that degrade the frozen production classifier.

### Category Breakdown ($N=926$):

| Category | Sample Count ($N$) | Total Duration (hours) | Primary Acoustic Mechanisms & Festival Context |
|---|---:|---:|---|
| **`STADIUM_CHEERING`** | **232** | 0.84 hrs | Multi-speaker vocal energy, high reverberation, sustained collective shrieks, crowd chanting |
| **`SHOUTED_SPEECH`** | **234** | 0.68 hrs | High vocal effort, commands, stage announcements, vocal fry, sudden conversational peaks |
| **`WHISTLE_SQUEAK`** | **141** | 0.38 hrs | Pure tonal whistles, referee whistles, high-frequency squeaks ($> 2.5\text{ kHz}$) |
| **`ENVIRONMENTAL_NON_VOCAL`** | **116** | 0.42 hrs | Stage bass rumbles, fireworks, pyrotechnics, door slams, generator hums |
| **`SIREN_ALARM`** | **91** | 0.35 hrs | Emergency vehicle sirens, electronic alarms, festival warning horns, sweep tones |
| **`BABY_CRYING`** | **75** | 0.24 hrs | Infant distress cries, high fundamental frequency ($F_0 > 500\text{ Hz}$), harsh harmonics |
| **`NORMAL_SPEECH`** | **26** | 0.11 hrs | Conversational dialogues, baseline non-elevated human speech |
| **`HARD_NEGATIVE_CONTROL`** | **14** | 0.05 hrs | NIGENS audited vocal benchmarks |
| **`NON_VOCAL_NOISE`** | **1** | 0.001 hrs | Ambient non-vocal transient |
| **TOTAL** | **926** | **3.07 hrs** | **364 independent source groups** |

---

## 2. Quality Control Protocol

1. **Signal Fidelity Verification:** Every file was inspected via SoundFile for non-corrupt headers, zero NaN values, float32 conversion bounds $[-1.0, 1.0]$, and sample rate conformity ($16\text{ kHz}$ mono resampling).
2. **Exclusion of Contaminated Files:** Any clip with ambiguous background screams or unverified provenance was excluded.
3. **Partition Isolation Rule:** All 364 source groups are assigned to isolated partition blocks. Zero cross-split speaker leakage is permitted.
