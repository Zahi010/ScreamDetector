# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Sustained-Scream Recall Failure Analysis: Acoustic Properties of Borderline Sustained Events

## 1. Executive Summary

In the development cohort ($N=312$), 62 recordings are positive screams with duration $\ge 1.00$s. In the Baseline Dual-Resolution Model and Candidate 65-F, 53 of these screams are correctly detected ($85.48\%$ sustained recall), leaving 9 persistent sustained scream misses. In contrast, Variant 6 suffered an additional 7 sustained misses (dropping sustained recall to $74.19\%$).

This report analyzes the acoustic etiology of the 9 persistent sustained scream misses to identify why 1-second sustained models struggle with these specific vocalizations.

---

## 2. Inventory of Persistent Sustained Scream Misses

The 9 sustained screams missed by both Baseline and Candidate 65-F at threshold $0.50$ are:

| Recording ID | Source Group ID | Duration (s) | Class / Subcategory | Model Prob | Acoustic Signatures & Missing Attributes |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `s60_rec_0428` | `s49_sg_dev_pos_001` | 1.834 | `screaming_female` | 0.4412 | Distant room reverberation; energy diffused above 4 kHz. |
| `s60_rec_0442` | `s49_sg_dev_pos_006` | 2.112 | `screaming_female` | 0.3891 | Late onset vocal fry; peak scream occurs in second half of recording. |
| `s60_rec_0461` | `s49_sg_dev_pos_012` | 1.450 | `screaming_male` | 0.4620 | Deep gutteral shout-scream; low F0 ($280\text{ Hz}$) near speech boundary. |
| `s60_rec_0478` | `s49_sg_dev_pos_019` | 3.200 | `screaming_female` | 0.3105 | Low acoustic volume ($\text{RMS} = 0.012$), heavy background hiss. |
| `s60_rec_0485` | `sg_s60_NIGENS_12891` | 1.250 | `scream` | 0.4789 | Borderline score just below 0.50 threshold. |
| `s60_rec_0504` | `sg_s60_NIGENS_24911` | 1.780 | `scream` | 0.4120 | Modulated pitch sweep; energy split across multiple subbands. |
| `s60_rec_0705` | `s49_sg_dev_pos_026` | 1.620 | `screaming_male` | 0.4350 | Rough vocal rasp with intermittent phonation gaps. |
| `s60_rec_0719` | `s49_sg_dev_pos_033` | 2.850 | `screaming_female` | 0.3620 | Multi-phrase vocalization; center 1s window lands on breath pause. |
| `s60_rec_0741` | `s49_sg_dev_pos_042` | 1.950 | `screaming_female` | 0.4510 | Gradual crescendo; energy peaks at the very end of the file. |

---

## 3. Forensic Acoustic Etiology

Three primary mechanisms account for sustained scream misses:

1. **Center-Window Misalignment (Temporal Slicing Artifact):**
   - For audio recordings lasting $1.5\text{--}3.2$ seconds, extracting only the center 1,000 ms chunk (`audio[len//2 - 8000 : len//2 + 8000]`) frequently samples an inhalation or breath pause (`s60_rec_0719`), or captures the quiet onset before a dramatic crescendo (`s60_rec_0442`, `s60_rec_0741`).
2. **Sub-Threshold Energy Near Decision Boundary:**
   - 5 of the 9 missed screams (`s60_rec_0428`, `s60_rec_0461`, `s60_rec_0485`, `s60_rec_0705`, `s60_rec_0741`) produced predicted probabilities between $0.43$ and $0.48$. They are near-misses that cross the threshold when the decision boundary is calibrated to $0.42\text{--}0.46$.
3. **Low-Pitch / Heavy Phonation Jitter:**
   - Male screams with low fundamental frequencies ($< 350\text{ Hz}$) generate acoustic subband profiles closely mirroring loud speech, causing the sustained branch neural head to output conservative logits.

---

## 4. Architectural Solutions

1. **Sliding Multi-Window Max Pooling:**
   - Rather than fixing the sustained branch to the single center window, evaluating multiple overlapping 1-second windows across longer files captures peak acoustic power regardless of when the scream begins.
2. **Confidence-Aware Dual-Branch Max Pooling:**
   - Short screams frequently maintain sharp 250ms transients even inside sustained events; decoupling branch decisions allows the short branch to rescue the sustained event.

---

## 5. Artifact Links
- Sustained Ablation CSV: [sustained_branch_ablation.csv](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/sustained_branch_ablation.csv)
- Sustained Branch Report: [sustained_branch_ablation_report.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/sustained_branch_ablation_report.md)

