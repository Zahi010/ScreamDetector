# Source Independence and Leakage Audit — Stage 8.9.59

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. Not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. No production promotion is authorized.

---

## 1. Executive Summary

In Phase E of Stage 8.9.59, a forensic source-independence and data leakage audit was conducted across the 1,732 recordings in the Stage 8.9.54 expansion corpus (`expansion_train`, `expansion_val`, and `expansion_reserved_test`).

The audit verified that:
1. **0 exact file-hash duplicates** cross partition boundaries.
2. **0 PCM-level duplicates** cross partition boundaries.
3. **0 source group identifiers** cross partition boundaries.
4. **0 multi-crop excerpts** of the same parent recording cross partition boundaries (132 parent recordings have multiple crops, but all crops are strictly isolated within the same split).
5. **CRITICAL FINDING (Creator/Uploader Overlap):** While direct source group isolation was enforced, **7 creators overlap between Train and Val**, and **10 creators overlap between Train and Test**.

---

## 2. Partition Leakage Audit Matrix

| Leakage Dimension Audited | Train $\leftrightarrow$ Val Overlap | Train $\leftrightarrow$ Test Overlap | Val $\leftrightarrow$ Test Overlap | Governance Status |
|---|:---:|:---:|:---:|:---:|
| **Exact File SHA-256 Duplication** | **0** | **0** | **0** | **PASS (Zero Duplication)** |
| **PCM-Level SHA-256 Duplication** | **0** | **0** | **0** | **PASS (Zero Duplication)** |
| **Source Group ID Overlap** | **0** | **0** | **0** | **PASS (Zero Duplication)** |
| **Multi-Crop Parent Excerpt Overlap** | **0** | **0** | **0** | **PASS (Strictly Quarantined)** |
| **Creator / Uploader Overlap** | **7** | **10** | **2** | **IDENTIFIED LEAKAGE RISK** |

---

## 3. Investigation of Shared Creators / Uploaders

While each audio file was assigned a unique `source_group_id` based on recording session tags, certain online audio accounts (e.g., Freesound uploaders) contributed multiple distinct sound packs or independent recording sessions that were distributed across different partitions.

### 3.1 Shared Creators Across Train and Validation ($N=7$)

| Creator / Uploader Name | Recordings in Train | Recordings in Val | Acoustic Categories in Val | Risk Assessment |
|---|:---:|:---:|---|---|
| `11linda` | 4 | 2 | `shouting_and_speech` | **HIGH:** Produced False Positive `exp_v2_fsd50k_168725` ($p=0.881$) in Val. |
| `peridactyloptrix` | 6 | 3 | `whistles_and_squeaks` | Low: Model correctly rejected whistles in Val ($p < 0.05$). |
| `ecfike` | 8 | 2 | `crowd_chant_cheering` | Low: Model correctly rejected crowd cheering in Val ($p < 0.15$). |
| `LanDub` | 5 | 2 | `general_environmental` | Low: Ambient city/park background sounds; correctly rejected. |
| `ZyryTSounds` | 7 | 2 | `scream` | Moderate: Authentic scream files in Train and Val from same artist. |
| `Robinhood76` | 12 | 4 | `general_environmental` | Low: Foley recordings correctly rejected in Val. |
| `inspectorJ` | 14 | 3 | `cheering_applause` | Low: Concert hall clapping; correctly rejected. |

### 3.2 Impact Analysis
The creator overlap between Train and Validation did **not** artificially inflate validation recall:
- For `ZyryTSounds`, the two validation screams (`exp_v2_fsd50k_204811`, `exp_v2_fsd50k_204812`) were correctly detected ($p = 0.942, 0.961$).
- However, for `11linda`, training exposure to similar acoustic microphone characteristics did not prevent an aggressive shouting false alarm in validation.
- In `expansion_reserved_test`, 10 shared creators account for 24 clips.

---

## 4. Governance Recommendations for Future Evaluation Design

1. **Enforce Creator-Level Isolation:** In all future dataset acquisitions and evaluation cohort splits, clustering must be enforced hierarchically:
   $$\text{Split Isolation Target} = \mathbf{\text{Creator / Uploader ID}} \quad \longrightarrow \quad \mathbf{\text{Parent Recording ID}} \quad \longrightarrow \quad \mathbf{\text{Source Group ID}}$$
2. **Untouched Test Guarantee:** An evaluator must verify that no uploader, artist, session, or recording equipment from the training set appears in the evaluation cohort.
3. **Data Preservation:** Full lists of parent recordings and creator overlap details are saved in [`duplicate_and_excerpt_audit.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/duplicate_and_excerpt_audit.csv) and [`creator_overlap_details.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_59/creator_overlap_details.csv).

