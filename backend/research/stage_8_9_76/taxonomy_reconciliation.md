# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Taxonomic Category Reconciliation & Formal Alignment Report

**Stage:** 8.9.76 — Independent Audio Acquisition, Double-Blind Annotation & Label Adjudication  
**Project:** Festival Scream Detector  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Author:** Research Data Curator & Annotation Protocol Specialist  

---

## 1. Executive Summary & Problem Formulation

In Stage 8.9.75, an apparent numerical discrepancy was noted between documentation stating:
- *"Six scream subcategories, seventeen negative categories, and one ambiguous category (totaling 24 categories)"*
and the Draft-07 JSON Schema (`annotation_schema.json`) stating:
- *"The schema defines 19 primary categories."*

This reconciliation audit was executed to determine whether the handbook and schema possessed semantic divergence, missing labels, or conflicting enums.

### Core Audit Finding:
The difference is purely architectural:
1. **Tier-1 (Primary Classification):** The schema defines **19 primary categories** (`primary_label`): 1 positive (`SCREAM`), 17 mutually exclusive negative classes, and 1 uncertainty class (`AMBIGUOUS_VOCALIZATION`).
2. **Tier-2 (Subcategory Specialization):** For any recording where `primary_label == "SCREAM"`, a mandatory second-tier property (`subcategory`) is populated with 1 of **6 positive subcategories** (`ADULT_HIGH_INTENSITY`, `ADULT_LOW_INTENSITY`, `CHILD_HIGH_PITCH`, `SHORT_STARTLE_UNDER_1S`, `SUSTAINED_DISTRESS`, `MASKED_DISTANT`).
3. **Flattened Canonical Leaf Count:** If the two-tier hierarchy is flattened into leaf classes (6 scream subcategories + 17 non-scream categories + 1 ambiguous category), there are **exactly 24 canonical leaf classes**.

There is zero semantic conflict between the handbook and schema. The canonical taxonomy has been formalized in [`canonical_taxonomy.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_76/canonical_taxonomy.json).

---

## 2. Comprehensive Category Reconciliation Matrix

| # | Flattened Leaf Class | Primary Schema Label (`primary_label`) | Schema Subcategory (`subcategory`) | Handbook Section | Acoustic Discriminant |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | `SCREAM__ADULT_HIGH_INTENSITY` | `SCREAM` | `ADULT_HIGH_INTENSITY` | Section 2.1 | $F_0 \in [350, 1000]$ Hz, roughness $> 0.025$, extreme chaos |
| 2 | `SCREAM__ADULT_LOW_INTENSITY` | `SCREAM` | `ADULT_LOW_INTENSITY` | Section 2.2 | $F_0 \in [300, 750]$ Hz, lower volume, moderate roughness |
| 3 | `SCREAM__CHILD_HIGH_PITCH` | `SCREAM` | `CHILD_HIGH_PITCH` | Section 2.3 | $F_0 \in [500, 2000]$ Hz, roughness $\in [0.010, 0.025]$ |
| 4 | `SCREAM__SHORT_STARTLE_UNDER_1S` | `SCREAM` | `SHORT_STARTLE_UNDER_1S` | Section 2.4 | Duration $< 1.0$s, attack $< 80$ms, abrupt startle |
| 5 | `SCREAM__SUSTAINED_DISTRESS` | `SCREAM` | `SUSTAINED_DISTRESS` | Section 2.5 | Duration $\ge 1.2$s, sustained subharmonic phonation |
| 6 | `SCREAM__MASKED_DISTANT` | `SCREAM` | `MASKED_DISTANT` | Section 2.6 | Embedded in crowd/noise (SNR $-6$ to $+6$ dB), Lombard pitch shift |
| 7 | `INFANT_CRY` | `INFANT_CRY` | `NONE` | Section 3.1 | Repetitive cry bursts (1.0–2.5 Hz cadence), cyclic pitch glide |
| 8 | `ADULT_CRY` | `ADULT_CRY` | `NONE` | Section 3.2 | Low-to-moderate trembling $F_0$ (150–350 Hz), sobbing breath |
| 9 | `SHOUTED_SPEECH` | `SHOUTED_SPEECH` | `NONE` | Section 3.3 | Intelligible lexical phonemes/formants ($F_1, F_2$), roughness $< 0.018$ |
| 10 | `THEATRICAL_SHOUT` | `THEATRICAL_SHOUT` | `NONE` | Section 3.4 | Dramatic stage projection, controlled closure, vibrato |
| 11 | `EXCITED_CHEER` | `EXCITED_CHEER` | `NONE` | Section 3.5 | Upward pitch contour, celebration, shared harmonics |
| 12 | `CROWD_CHANT` | `CROWD_CHANT` | `NONE` | Section 3.6 | Stadium unison cadence ($0.5$–$1.5$ Hz), low roughness |
| 13 | `SINGING` | `SINGING` | `NONE` | Section 3.7 | Musical pitches, high harmonicity ($HNR > 15$ dB), vibrato |
| 14 | `LAUGHTER` | `LAUGHTER` | `NONE` | Section 3.8 | Rhythmic exhalations ($4$–$6$ Hz burst rate), falling pitch |
| 15 | `GASP` | `GASP` | `NONE` | Section 3.9 | Unvoiced inspiratory airflow, duration $< 0.5$s |
| 16 | `WHISTLE` | `WHISTLE` | `NONE` | Section 3.10 | Narrow-band tonal peak (2.0–4.5 kHz), roughness $< 0.005$ |
| 17 | `SIREN` | `SIREN` | `NONE` | Section 3.11 | Swept electronic/mechanical FM tones (500–1800 Hz) |
| 18 | `ANIMAL_VOCALIZATION` | `ANIMAL_VOCALIZATION` | `NONE` | Section 3.12 | Dogs barking, birds screeching, animal cries |
| 19 | `ENVIRONMENTAL_ALARM` | `ENVIRONMENTAL_ALARM` | `NONE` | Section 3.13 | Smoke alarms, industrial buzzers, intrusion beeps |
| 20 | `MECHANICAL_SOUND` | `MECHANICAL_SOUND` | `NONE` | Section 3.14 | Fairground rides, machinery squeals, metal friction |
| 21 | `MUSIC` | `MUSIC` | `NONE` | Section 3.15 | Heavy bass, drums, stage instruments, synth audio |
| 22 | `AMBIENT_NOISE` | `AMBIENT_NOISE` | `NONE` | Section 3.16 | Wind, rain, festival crowd murmur, background rumble |
| 23 | `OTHER_NON_SCREAM` | `OTHER_NON_SCREAM` | `NONE` | Section 3.17 | Other non-scream sounds not falling in above categories |
| 24 | `AMBIGUOUS_VOCALIZATION` | `AMBIGUOUS_VOCALIZATION` | `NONE` | Section 4.0 | Unresolvable boundary case, heavy distortion, mixed traits |

---

## 3. Operational Annotation Rules

1. **Mandatory Primary Selection:** Annotators must first select exactly one of the 19 primary categories.
2. **Conditional Subcategory Assignment:**
   - If `primary_label == "SCREAM"`, the annotator **MUST** select one of the 6 positive scream subcategories.
   - If `primary_label != "SCREAM"`, `subcategory` automatically defaults to `"NONE"`.
3. **Explicit Ambiguity Rule:** Borderline theatrical shouts, half-gasp vocalizations, or heavily clipped recordings must be marked `AMBIGUOUS_VOCALIZATION` with `ambiguity_flag = True` and a mandatory `uncertainty_reason`.

