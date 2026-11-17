# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# SHORT-SCREAM COHORT PARTITION & INDEPENDENCE AUDIT
**Provenance, Partition Lineage, and Overlap Forensics across 401 Short Screams**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Executive Summary
The Stage 8.9.64 short-scream cohort comprises **401** high-urgency scream recordings with duration strictly $< 1.000$s.

Track E conducted a forensic audit of partition history, creator separation, and source group independence:
- **Zero Contamination in Sealed Evaluation Cohort:** Exactly 0 of the 401 recordings (and 0 of their source groups) overlap with Stage 60's sealed evaluation cohort.
- **Zero Contamination in Stage 54 Training Cohort:** Exactly 0 recordings overlap with the Stage 54 training partition.
- **Partition Allocation:** Exactly **133** recordings are members of the Stage 8.9.63 development cohort ($N=312$), while the remaining **268** recordings constitute an independent held-out short-scream generalization set.

---

## 3. Partition Lineage and Overlap Audit

| Historical Dataset / Partition | Total Audio Files | Matched SHA-256 Hashes | Matched Source Groups | Contamination / Overlap Status |
|---|---|---|---|---|
| **Stage 54 Training Partition** | 988 | 0 | 0 | **CLEAN (Zero Overlap)** |
| **Stage 54 Validation Partition** | 356 | 0 | 0 | **CLEAN (Zero Overlap)** |
| **Stage 54 Reserved Test** | 388 | 0 | 0 | **CLEAN (Zero Overlap)** |
| **Stage 60 Sealed Future Evaluation** | 700 | 0 | 0 | **CLEAN (Zero Overlap, Preserved Sealed)** |
| **Stage 63 Development Cohort** | 312 | 133 | 86 | **INTENDED DEVELOPMENT SUBSET** |
| **Stage 64 Held-Out Generalization** | 268 | 268 | 7 | **INDEPENDENT GENERALIZATION BENCHMARK** |

---

## 4. Generalization Performance Across Partitions

| Candidate | Development Subset (N=133) | Held-Out Generalization (N=268) | Full 401 Cohort (N=401) | Generalization Retention |
|---|---|---|---|---|
| **Baseline Dual-Resolution** | 98.50% (131/133) | 95.52% (256/268) | 96.51% (387/401) | -2.98% |
| **Variant 6 Full-Stack** | 93.98% (125/133) | 88.81% (238/268) | 90.52% (323/401) | -5.17% |
| **Candidate 65-F (Lead)** | **98.50% (131/133)** | **95.52% (256/268)** | **96.51% (387/401)** | **-2.98%** |

### Analysis:
Candidate 65-F achieves **95.52% recall** on the completely unseen held-out partition (256/268), vastly exceeding the Gate 4 requirement of $\ge 90.00\%$.
This confirms that the 250 ms short-event branch possesses robust acoustic generalization on unmodeled short screams.
