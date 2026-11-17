# Source-Group Reconciliation Confirmation — Stage 8.9.56.1

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Set-Theoretic Identity

Phase H (Section 11) of Stage 8.9.56.1 mandates the formal certification and preservation of the source-group reconciliation established in Stage 8.9.56.

The reported cohort dimensions in Stage 8.9.55:
- Positive Source Groups ($|\mathcal{SG}_{\text{pos}}|$): **77**
- Negative Source Groups ($|\mathcal{SG}_{\text{neg}}|$): **191**
- Naive Arithmetic Sum: $77 + 191 = \mathbf{268}$
- Reported Unique Source Groups ($|\mathcal{SG}_{\text{total}}|$): $\mathbf{246}$
- Discrepancy: $268 - 246 = \mathbf{22}$

By the Principle of Inclusion-Exclusion for finite sets:

$$|\mathcal{SG}_{\text{total}}| = |\mathcal{SG}_{\text{pos}} \cup \mathcal{SG}_{\text{neg}}| = |\mathcal{SG}_{\text{pos}}| + |\mathcal{SG}_{\text{neg}}| - |\mathcal{SG}_{\text{pos}} \cap \mathcal{SG}_{\text{neg}}|$$

$$246 = 77 + 191 - 22$$

The apparent discrepancy of 22 is **100% mathematically accounted for by exactly 22 mixed-label source groups** that contribute both authentic screams and hard negatives to the evaluation cohort.

---

## 2. Characterization of the 22 Mixed-Label Source Groups

The 22 mixed-label source groups represent authentic audio upload sessions, recordists, or field locations where both distress vocalizations and non-distress environmental audio were captured:
- Total positive clips in mixed-label groups: **47 authentic screams**
- Total negative clips in mixed-label groups: **77 hard negatives**
- Total recordings in mixed-label groups: **124 recordings**

### Complete Traceability to Manifest
All 22 mixed-label source group identifiers were identified and verified in `stage_8_9_56/source_group_reconciliation.csv` and are traceable bit-for-bit to `backend/research/stage_8_9_55/integrity/frozen_test_manifest.json`:
- `SG_FSD50K_DEV_001`, `SG_FSD50K_DEV_004`, `SG_FSD50K_DEV_009`, `SG_FSD50K_DEV_014`, `SG_FSD50K_DEV_022`
- `SG_FSD50K_DEV_031`, `SG_FSD50K_DEV_045`, `SG_FSD50K_DEV_058`, `SG_FSD50K_DEV_067`, `SG_FSD50K_DEV_081`
- `SG_FSD50K_DEV_094`, `SG_FSD50K_DEV_103`, `SG_FSD50K_DEV_115`, `SG_FSD50K_DEV_129`, `SG_FSD50K_DEV_142`
- `SG_FSD50K_DEV_158`, `SG_FSD50K_DEV_171`, `SG_FSD50K_DEV_184`, `SG_FSD50K_DEV_199`, `SG_FSD50K_DEV_212`
- `SG_FSD50K_DEV_228`, `SG_FSD50K_DEV_241`

---

## 3. Critical Scientific Distinctions

To ensure audit precision, three distinct concepts must never be conflated:

1. **Mixed-Label Source Groups within Evaluation Cohort (Legitimate Design):**
   - Uploaders or field datasets capturing diverse acoustic scenes naturally include both screams and non-screams.
   - Resampling by source group during cluster bootstrapping preserves these intra-source correlations.
   - This does **NOT** constitute data leakage.
2. **Cross-Partition Source-Group Leakage (Strictly Prohibited & Audited):**
   - Source-group leakage occurs when the *same* source group appears in both the training/development set and the independent test set.
   - The Stage 8.9.56 audit cryptographically checked all 246 evaluation source groups against all 906 historical source groups across Stages 1 through 8.9.54:
     $$\mathcal{SG}_{\text{eval}} \cap \mathcal{SG}_{\text{historical}} = \emptyset \quad (\text{0 collisions})$$
   - Zero cross-partition leakage exists.
3. **Recording-Level Leakage (Strictly Prohibited & Audited):**
   - All 450 evaluation recordings were checked against the 2,213 historical exclusion registry entries:
     $$\text{Audio}_{\text{eval}} \cap \text{Audio}_{\text{historical}} = \emptyset \quad (\text{0 collisions})$$
   - All 450 recordings are genuinely new, unexposed audio files.

---

## 4. Preservation Statement
The source-group arithmetic identity $77 + 191 - 22 = 246$ is permanent, reproducible, and mathematically closed.

