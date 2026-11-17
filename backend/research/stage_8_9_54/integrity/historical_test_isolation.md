# Historical Test Cohort Isolation & Generalization Preparation — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Isolation of Evaluated Historical Test Cohort

The 366-recording expansion test cohort (`expansion_reserved_test`, 140 source groups) was formally evaluated in Stage 8.9.53.

Per scientific evaluation governance rules:
- **No Test Tuning:** The Stage 8.9.53 cohort is permanently classified as an evaluated historical benchmark.
- **Strict Quarantine:** Zero recordings from `expansion_reserved_test` were used for model retraining, early stopping, hyperparameter tuning, or validation threshold selection in Stage 8.9.54.
- **Independence Proof:**
  $$\mathcal{SG}_{\text{expansion\_train}} \cap \mathcal{SG}_{\text{stage53\_test}} = \emptyset \quad (\text{0 overlapping SGs})$$
  $$\mathcal{SG}_{\text{expansion\_val}} \cap \mathcal{SG}_{\text{stage53\_test}} = \emptyset \quad (\text{0 overlapping SGs})$$
  Zero audio hashes or PCM frames collide with the training or validation sets.

---

## 2. Generalization Status
While expanded-data retraining (E0–E3) dramatically elevated validation metrics on `expansion_val` (PR-AUC: $0.7040 \rightarrow 0.9224$, HN-FPR: $11.79\% \rightarrow 4.72\%$), **generalization remains officially UNVERIFIED** until evaluated on a genuinely untouched, independent test cohort.

Validation improvements provide internal development evidence only.

---

## 3. Plan for New Independent Evaluation Cohort (Stage 8.9.55 Cohort)

To rigorously test whether Candidate E1 / E3's performance gains generalize, a newly acquired independent evaluation cohort must be curated under the following specifications:

### Target Cohort Specifications:
1. **Sample Size:** 400–500 authentic recordings across $\ge 150$ independent source groups.
2. **Class Balance:** Approximately 150 authentic scream-like positives and 300 difficult hard negatives.
3. **Mandatory Subtype Quotas:**
   - Low-intensity / muffled authentic screams: $\ge 30$ recordings.
   - Crowd-masked authentic screams: $\ge 40$ recordings.
   - Distant / reverberant authentic screams: $\ge 30$ recordings.
   - Short (<1.0s) and ultra-short (<0.5s) screams: $\ge 40$ recordings.
   - Difficult negative distractors: Shouted speech ($\ge 80$), stadium cheering ($\ge 60$), referee pea-whistles ($\ge 40$), sirens / fireworks ($\ge 40$).
4. **Licensing:** 100% verified permissive commercial licenses (CC0 1.0, CC-BY 3.0, CC-BY 4.0).
5. **Leakage & Duplicate Prevention:**
   - 0 source-group overlap with `expansion_train`, `expansion_val`, or any historical cohort.
   - 0 exact file SHA-256 or PCM hash collisions.
   - Temporal excerpt deduplication.
6. **Double-Blind Label Adjudication:** Dual-pass expert review with explicit adjudication tags.

