# Source-Group Statistical Independence & Resampling Audit — Stage 8.9.53

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Source Group Partition Topology

- **Total Unique Source Groups:** 140
- **Clips per Source Group (Mean):** 2.61
- **Clips per Source Group (Range):** 1 to 42

### Source Group Isolation Proof
$$\mathcal{SG}_{\text{test}} \cap \mathcal{SG}_{\text{train}} = \emptyset \quad (0 \text{ overlapping SGs})$$
$$\mathcal{SG}_{\text{test}} \cap \mathcal{SG}_{\text{val}} = \emptyset \quad (0 \text{ overlapping SGs})$$

---

## 2. Cluster Resampling Metric Distributions (1,000 Iterations)

Accounting for intra-source correlation yields realistic generalization intervals:

| Model | Metric | Cluster Bootstrap Mean | 95% Percentile Confidence Interval | Standard Deviation |
|---|---|---|---|---|
| **Candidate E** | Recall | 63.30% | [51.64%, 74.67%] | 5.95% |
| **Candidate E** | Hard-Neg FPR | 16.53% | [10.82%, 23.19%] | 3.28% |
| **Candidate E** | F1 Score | 61.29% | [50.59%, 71.13%] | 5.23% |
| **Candidate B Baseline** | Recall | 71.42% | [60.55%, 81.16%] | 5.16% |
| **Candidate B Baseline** | Hard-Neg FPR | 1.98% | [0.34%, 4.25%] | 1.04% |
| **Candidate B Baseline** | F1 Score | 80.86% | [72.48%, 87.83%] | 3.79% |
| **Candidate B + Interv D**| Recall | 71.42% | [60.55%, 81.16%] | 5.16% |
| **Candidate B + Interv D**| Hard-Neg FPR | 1.98% | [0.34%, 4.25%] | 1.04% |
| **Candidate B + Interv D**| F1 Score | 80.86% | [72.48%, 87.83%] | 3.79% |
