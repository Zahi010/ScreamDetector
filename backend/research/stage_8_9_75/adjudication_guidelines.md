# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Adjudication Guidelines, Dispute Resolution & Consensus Protocols

**Project:** Festival Scream Detector  
**Stage:** 8.9.75  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Effective Date:** 2026-11-14  
**Author:** Audio Annotation Protocol Designer & Statistical Validation Engineer  

---

## 1. Executive Summary & Purpose

Adjudication is the formal governance process for resolving inter-annotator disagreements. 

In past stages, disagreements were often collapsed into ad-hoc binary labels or silently discarded, introducing label noise. This document establishes an objective, transparent, and auditable protocol for resolving label conflicts while permanently preserving raw rater decisions.

---

## 2. Disagreement Triggers & Classification

An annotation pair is flagged for adjudication (`FLAGGED_FOR_ADJUDICATION`) if any of the following triggers occur:

| Trigger Type | Description | Resolution Path |
| :--- | :--- | :--- |
| **Category Disagreement (Binary)** | Rater 1 classifies as `SCREAM`; Rater 2 classifies as a negative class (e.g. `SHOUTED_SPEECH` or `INFANT_CRY`). | **Tier 1 Escalation:** Blinded Third-Rater Review. |
| **Subcategory Disagreement** | Both raters agree on `SCREAM`, but disagree on subcategory (e.g. `CHILD_HIGH_PITCH` vs `SHORT_STARTLE_UNDER_1S`). | **Tier 2 Review:** Senior Adjudicator Review based on acoustic spectrogram metrics. |
| **Negative Multi-Class Conflict** | Raters disagree between two non-scream categories (e.g. `WHISTLE` vs `SIREN` or `EXCITED_CHEER` vs `LAUGHTER`). | **Consensus Mapping:** Resolves to dominant non-scream category; does not affect binary evaluation. |
| **Temporal Boundary Mismatch** | Raters agree on label, but temporal Intersection-over-Union ($IoU < 0.50$) indicates disparate event windowing. | **Boundary Harmonization:** Adjudicator inspects spectrogram energy envelope to set canonical boundaries. |
| **Confidence Divergence** | Raters assign identical labels, but one rater marks `ambiguity_flag=True` or `confidence <= 2`. | **Uncertainty Audit:** Review for acoustic degradation or borderline performance. |

---

## 3. Escalation Protocols

### Tier 1: Independent Third-Rater Tie-Breaker
1. A third independent annotator (`RATER_C`), completely blinded to both prior raters' labels and notes, independently evaluates the recording.
2. If Rater C agrees with either Rater A or Rater B, majority rule governs:
   $$\text{Final Label} = \text{Mode}(\text{Label}_A, \text{Label}_B, \text{Label}_C)$$
3. The adjudication status is set to `RESOLVED_BY_CONSENSUS`.

### Tier 2: Senior Adjudication Panel Arbitration
1. If Rater C introduces a third distinct label (e.g. Rater A = `SCREAM`, Rater B = `SHOUTED_SPEECH`, Rater C = `THEATRICAL_SHOUT`), or if the disagreement involves high-stakes boundary cases, the case escalates to the Senior Adjudication Panel.
2. The panel inspects calibrated spectrograms, fundamental frequency tracks ($F_0$), harmonic-to-noise ratio ($HNR$), and auditory roughness metrics.
3. The panel issues a binding written ruling containing:
   - Primary label assigned.
   - Acoustic justification referencing [`annotation_handbook.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/annotation_handbook.md).
   - Adjudicator pseudonymous ID and UTC timestamp.
4. The adjudication status is set to `RESOLVED_BY_ARBITRATOR`.

---

## 4. The Ambiguity Protocol: Permanent Quarantine

If an audio recording cannot be definitively resolved after Tier 2 acoustic analysis (for example, a highly distorted audio clip where a scream and a loud stadium cheer coincide, or an ambiguous acting exercise), the recording MUST NOT be forced into a positive or negative label.

**Mandatory Rule:**
- The recording is designated `AMBIGUOUS_VOCALIZATION`.
- Adjudication status is set to `DESIGNATED_PERMANENTLY_AMBIGUOUS`.
- The recording is **quarantined from benchmark evaluation splits**.
- It is cataloged in the diagnostic ambiguity registry for subsequent qualitative error audits.

> [!CAUTION]
> **Prohibition Against Model-Driven Relabeling:** Under NO circumstances may an adjudicator consult Candidate 71-D's classification output, activation logits, or veto triggers to break a tie. Ground truth must remain completely autonomous from the algorithms under test.

---

## 5. Audit Trail & Record Preservation

Every adjudication event must append an immutable record to the master adjudication audit log:
- `recording_id`
- `original_labels`: JSON array of raw rater submissions `[{"rater": "A", "label": "..."}, {"rater": "B", "label": "..."}]`
- `adjudicated_label`
- `adjudication_status`
- `adjudicator_id`
- `justification_notes`
- `timestamp_utc`

Raw rater submissions are permanently retained to allow calculating raw inter-rater agreement and kappa statistics across all stages.

