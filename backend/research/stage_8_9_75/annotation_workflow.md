# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Multi-Annotator Workflow, Double-Blind Protocol & Review Architecture

**Project:** Festival Scream Detector  
**Stage:** 8.9.75  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Effective Date:** 2026-11-14  
**Author:** Audio Annotation Protocol Designer & Research Governance Auditor  

---

## 1. Overview and Core Principles

The integrity of machine learning benchmarks depends fundamentally on the independence and reliability of ground-truth annotations. 

Historical audits revealed that single-annotator labels or ad-hoc consensus review introduced severe systematic bias—most notably in Stage 74, where ambiguous voice-acting shouts (`reitanna`) and surprised gasps were arbitrarily forced into binary labels, distorting reported recall and FPR metrics.

Stage 8.9.75 establishes a formal **Multi-Annotator Double-Blind Protocol**:
1. **Double-Blind Independent Annotation:** Every audio recording must be evaluated by at least two independent, blinded human raters without communication or shared views.
2. **Total Model Isolation:** Annotators are strictly blinded from model predictions, probability scores, acoustic veto states, or prior candidate outputs.
3. **Immutable Raw Decisions:** Initial rater decisions are cryptographically recorded and never overwritten, mutated, or deleted during adjudication.
4. **Structured Escalation:** Disagreements automatically trigger third-party blinded review or senior panel adjudication.

---

## 2. Multi-Tier Annotation Lifecycle

```
[Raw Audio Candidate]
        │
        ├───> [Independent Rater 1 (Blinded)] ───> Annotation Record 1 (Immutable)
        │
        └───> [Independent Rater 2 (Blinded)] ───> Annotation Record 2 (Immutable)
                                                          │
                                                          ▼
                                             [Automated Agreement Engine]
                                                          │
                         ┌────────────────────────────────┴────────────────────────────────┐
                         ▼                                                                 ▼
                [Perfect Consensus]                                              [Discrepancy Detected]
             (Primary Labels Match)                                           (Label or Boundary Mismatch)
                         │                                                                 │
                         ▼                                                                 ▼
            [Status: DOUBLE_BLIND_COMPLETE]                                  [Status: FLAGGED_FOR_ADJUDICATION]
                         │                                                                 │
                         ▼                                                                 ▼
             [Gold Consensus Dataset]                                            [Blinded Rater 3 Review]
                                                                                           │
                                                                   ┌───────────────────────┴───────────────────────┐
                                                                   ▼                                               ▼
                                                          [Majority Consensus]                            [Persistent Dispute]
                                                                   │                                               │
                                                                   ▼                                               ▼
                                                    [Status: ADJUDICATED_FINAL]                      [Senior Adjudication Panel]
                                                                                                                   │
                                                                                                                   ▼
                                                                                                     [Resolved or Marked AMBIGUOUS]
```

---

## 3. Strict Blinding Rules

To prevent anchoring bias and confirmation bias, annotators must adhere to the following strict blinding mandates:

1. **No Algorithmic Visibility:** At no point during the primary labeling phase may annotators view Candidate 71-D predictions, YAMNet embeddings, roughness metrics, or detection heatmaps.
2. **No Peer Visibility:** Annotator A cannot see Annotator B's label, confidence score, notes, or boundary timestamps until both raters have formally submitted and locked their records.
3. **No Retrospective Relabeling:** If an error analysis is performed on Candidate 71-D predictions after prospective unsealing, ground-truth labels may NOT be altered to accommodate model predictions.

---

## 4. Annotation Process Step-by-Step

### Step 1: Listening and Acoustic Assessment
- The rater listens to the full clip at calibrated volume using reference headphones in a quiet environment.
- The rater identifies the onset and offset timestamps ($[t_{start}, t_{end}]$) of the primary acoustic event.

### Step 2: Operational Classification
- The rater consults [`annotation_handbook.md`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/annotation_handbook.md) to select the primary category.
- If the event is a scream, the rater specifies the appropriate subcategory (`ADULT_HIGH_INTENSITY`, `CHILD_HIGH_PITCH`, `SHORT_STARTLE_UNDER_1S`, etc.).
- If the rater observes secondary overlapping sounds (e.g. scream over loud siren), the secondary label is recorded.

### Step 3: Confidence and Ambiguity Scoring
- Rater assigns confidence (1 to 5).
- If confidence $< 3$ or traits conflict, `ambiguity_flag` is set to `True` with an explicit `uncertainty_reason`.

### Step 4: Submission & Verification
- The record is validated against [`annotation_schema.json`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_75/annotation_schema.json).
- The record is appended to the immutable database with UTC timestamp and rater hash.

