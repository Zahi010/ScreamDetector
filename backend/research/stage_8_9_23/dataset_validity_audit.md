# Dataset and Label Validity Audit

## Executive Summary

This audit evaluates the integrity, source independence, licensing compliance, and acoustic representativeness of the dataset used throughout the Festival Scream Detector project. 

The audit analyzed all **2,246 recording entries** across the primary train, validation, and test splits documented in `dataset_manifest_v3.json` alongside raw audio files and provenance records.

### Summary of Audit Verdicts

| Dimension | Audited Metric / Finding | Status / Evaluation |
|---|---|---|
| **Source Group Leakage** | 669 Train, 144 Val, 142 Test source groups. Intersection = $\emptyset$. | **100% CLEAN (0% Leakage)** |
| **Audio File Hash Duplication** | SHA-256 computed per audio file. 0 cross-split duplicates found. | **100% CLEAN** |
| **Historical Stage 5 Isolation** | Stage 5 test set sources remain completely isolated from training. | **100% CLEAN** |
| **Short-Scream Sample Adequacy** | Primary test set contains only **22 short screams** ($\le 1.0 \text{ s}$). | **INSUFFICIENT (High Margin of Error)** |
| **Shouting Sample Diversity** | 84 shouting samples dominated by 4 online sound-effects actors. | **SUBOPTIMAL (Actor-Skewed)** |
| **Licensing Integrity** | Only **37.9%** of audio is commercially permissible (CC0, CC BY). **62.1%** is restricted under Academic / NC licenses. | **RESTRICTED FOR COMMERCIAL USE** |

---

## 1. Source Group Isolation and Leakage Audit

To prevent speaker-specific overfitting, recordings are tagged with `source_group_id` (representing individual uploaders, actors, or acoustic recording sessions).

```
==================================================
DATASET SOURCE GROUP ISOLATION ANALYSIS
==================================================
Train Source Groups:       669
Validation Source Groups:  144
Test Source Groups:        142

Pairwise Overlap:
Train ∩ Validation:        0
Train ∩ Test:              0
Validation ∩ Test:         0

Leakage Rate:              0.000%
```

Every recording in the primary held-out test split is strictly isolated from the training and validation sets. No speaker or acoustic environment is shared across splits.

---

## 2. Audio Content Duplication Audit

We audited the SHA-256 hashes of all underlying `.wav` files across splits:
- **Total Unique Audio Hashes**: 2,246
- **Cross-Split Duplicates**: 0
- **Within-Split Duplicates**: 0
There is no identical or renamed audio leakage across the splits.

---

## 3. Licensing and Provenance Audit

A comprehensive licensing review was conducted across all dataset sources. Results are summarized below and fully detailed in `backend/research/stage_8_9_23/dataset_source_integrity.csv`.

| License Category | Number of Recordings | Percentage | Deployment Authorization |
|---|---|---|---|
| **CC0 / Public Domain** | 312 | 13.9% | Fully Permissible |
| **CC BY (Attribution 3.0 / 4.0)** | 538 | 24.0% | Commercial Permissible with Attribution |
| **CC BY-NC (Non-Commercial)** | 894 | 39.8% | **Research / Academic Only** |
| **CC BY-NC-ND (No Derivatives)** | 286 | 12.7% | **Strict Research Only** |
| **Unverified / Fair Use Research** | 216 | 9.6% | **Research Only** |
| **Total** | **2,246** | **100.0%** | **37.9% Commercial Permissible** |

### Critical Finding on Commercial Readiness
Over **62.1%** of the project's audio corpus is licensed under Non-Commercial (NC) or Unverified research terms (originating primarily from FSD50K, NIGENS, and Freesound CC-BY-NC tags). While fully compliant with academic and internal research, **this dataset cannot be packaged or monetized in a commercial festival security product** without replacing NC recordings with CC0 / CC-BY or custom-recorded festival audio.

---

## 4. Acoustic Diversity & Short-Scream Adequacy

### 4.1 Short-Scream Sample Scarcity
In the primary test split ($N = 462$):
- Sustained Screams ($> 1.0 \text{ s}$): 56
- Short Screams ($\le 1.0 \text{ s}$): **22**

With only 22 short-scream test samples, each individual recording accounts for **4.55%** of the short-scream recall metric. Achieving 19/22 gives 86.36%, but a single additional missed scream drops recall to 81.81%. This sample size is too small to provide confidence intervals narrower than $\pm 14.5\%$.

While the supplementary set provides $N = 68$ short screams, it is a positive-only set lacking matched short negative transients (e.g., short vocal gasps, sneezes, sudden cheers, door slams). Validating short-scream robustness requires an independent balanced benchmark of short acoustic bursts.

### 4.2 Shouting Diversity Limitations
The 84 shouting test samples originate predominantly from 4 sound effects contributors (`xtrgamr`, `liamg_sfx`, `ericsueiro`, `reitanna`). These recordings represent dramatic, isolated studio shouting for video games and theatrical sound effects rather than realistic ambient shouting recorded at a crowded music festival.
