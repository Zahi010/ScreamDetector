# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Annotation Reliability, Label Ambiguity & Vocalization Taxonomy Audit

**Project:** Festival Scream Detector  
**Stage:** 8.9.74  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Date:** 2026-11-14  
**Subject:** Ground-truth label consistency, taxonomy boundary overlap, and error classification.

---

## 1. Executive Summary

A comprehensive investigation was conducted into the 40 total classification discrepancies produced by Candidate 71-D on the Stage 54 validation cohort ($N=311$): 17 false negatives, 10 hard-negative false positives, and 13 shouted-speech false positives.

The primary objective was to determine whether residual errors represent genuine machine learning limitations or underlying label ambiguity, inconsistent category boundaries, and forced binary labeling.

### Key Audit Findings:
1. **Error Breakdown:**
   - **`ACOUSTIC_CLASSIFICATION_ERROR`:** **25 cases (62.5%)**. Represents genuine model failure to extract discriminative features or handle heavy background noise (e.g. 8 synthetic crowd-masked screams, 2 whistle bursts, 2 sirens, 3 infant cries, 5 natural screams, 5 natural shouts).
   - **`ANNOTATION_UNCERTAINTY`:** **15 cases (37.5%)**. Represents ambiguous ground truth where non-scream vocalizations were forced into binary scream labels, or where theatrical screams were labeled as non-scream speech.
2. **Inter-Annotator Reliability Status:**
   - **Cannot Be Calculated for Validation Partition:** Unlike Stage 60 (which recorded independent votes from two blinded reviewers for 962 clips), the Stage 54 development cache (`val_features.npz`) preserves only consensus labels. Individual rater logs do not exist for this cohort; therefore, Cohen's Kappa ($\kappa$) cannot be computed.
3. **Severe Uploader Clumping in Ambiguity:**
   - Out of the 13 shouted-speech false alarms, **8 clips (61.5%)** originate from a single uploader session (`exp_sg_stage8_9_reitanna`). These clips consist of dramatic, high-effort voice-acting vocalizations that exhibit vocal fold chaos and scream-like formant contours.
   - Two of the 17 missed screams (`242607__reitanna__gasp-oooh` and `242644__reitanna__another-surprised-oooh`) are titled as vocal gasps, yet were annotated as ground-truth screams.

---

## 2. Forensic Analysis of Ambiguous Vocalization Categories

### A. Theatrical Voice-Acting Dramatic Screams vs Shouted Speech ($N=8$ FPs)
- **Acoustic Characteristics:** Mean roughness = 0.0805, mean HF ratio = 0.2372, mean flux = 0.1002.
- **Root Cause:** Freesound user `reitanna` recorded an extensive series of high-energy dramatic vocalizations for acting packs. Some clips were cataloged in sound libraries under "shout" while others from the exact same recording session were cataloged under "scream".
- **Taxonomic Problem:** The acoustic boundary between an enraged shouted curse, a theatrical death scream, and an authentic panic shriek is continuous, not discrete. Forcing these clips into a binary label creates artificial false positives.

### B. Surprise Gasps Labeled as Ground-Truth Screams ($N=2$ FNs)
- **Recordings:** `242607__reitanna__gasp-oooh` ($p = 0.3821$) and `242644__reitanna__another-surprised-oooh` ($p = 0.3824$).
- **Acoustic Characteristics:** Short vocal intake and voiced "oooh" exhalation ($duration \approx 1.3$–$1.5$s) with low spectral roughness ($0.0289$ and $0.0738$).
- **Taxonomic Problem:** A startled gasp is physiologically and acoustically distinct from an authentic scream. Labeling these as screams penalizes the model for correctly recognizing the absence of rough, chaotic vocal fold vibration.

### C. Infant Crying & Colic Distress ($N=3$ FPs)
- **Recordings:** `fsd50k_154428` ($p=0.5632$), `fsd50k_343976` ($p=0.5844$), `fsd50k_344030` ($p=0.6787$).
- **Acoustic Characteristics:** Mean roughness = 0.0365, mean flux = 0.0986, mean duration = 9.9s.
- **Root Cause:** Infant vocal folds possess small anatomical mass, oscillating at high frequencies with non-linear bifurcations (subharmonics, biphonation, and vocal chaos) during acute distress.
- **Taxonomic Problem:** While infant crying is not an adult scream, it represents genuine vocal distress. Binary models struggle to separate them without age-specific acoustic priors.

### D. Child Screams ($N=2$ FNs)
- **Recording:** `273153__hoerspielwerkstatt-hef__child-scream2` (2 segments, $p=0.1148$ and $p=0.1144$).
- **Acoustic Characteristics:** High fundamental frequency ($F_0 > 500$ Hz), very low auditory roughness ($0.0189 < 0.022$), and low high-frequency ratio ($0.0130 < 0.050$).
- **Root Cause:** The distress veto was tuned against adult vocalizations. Because child screams have lower roughness than adult screams, they are collaterally suppressed.

---

## 3. Ambiguity Summary & Distribution Ledger

| Error Category | False Negatives | Hard-Negative FPs | Shouted-Speech FPs | Total Cases | Primary Taxonomic Assignment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`ACOUSTIC_CLASSIFICATION_ERROR`** | 15 | 7 | 5 | **27 (67.5%)** | Synthetic Masked (8), Boundary Screams (5), Child Screams (2), Whistles (3), Sirens (2), Environmental (2), Natural Shouts (5) |
| **`ANNOTATION_UNCERTAINTY`** | 2 | 3 | 8 | **13 (32.5%)** | Surprise Gasps (2), Infant Distress Cries (3), Theatrical Acting Shouts (8) |
| **TOTAL ERROR AUDIT** | **17** | **10** | **13** | **40 (100%)** | Fully documented in `vocalization_label_review.csv` |

---

## 4. Recommendations for Dataset Curation

1. **Retain Original Ground-Truth Labels:** In strict compliance with scientific integrity, no annotations in the historical validation cache will be altered or relabeled.
2. **Review Queue Establishment:** The 40 audited files have been compiled into [`vocalization_label_review.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/vocalization_label_review.csv) for future multi-reviewer panel adjudication.
3. **Transition to Multi-Class Acoustic Taxonomy:** Replace binary labeling with a multi-level hierarchical taxonomy (see [`label_definition_proposal.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_74/label_definition_proposal.md)).

