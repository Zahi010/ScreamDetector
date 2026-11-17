# Stage 8.9.41: Source-Group Independence & Cross-Partition Leakage Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**

*This project is an experimental acoustic research system. It is not certified for life-safety alerting, emergency response, active shooter detection, autonomous police dispatch, or critical physical security deployments.*

---

## 1. Overview & Research Requirement

In acoustic machine learning, grouping recordings by physical source (such as speaker identity, recording session, room acoustic environment, or synthetic generation seed) is necessary to ensure that evaluation measures true acoustic generalization rather than speaker or environment memorization.

This audit evaluates the cross-partition independence of the Stage 8.9.41 positive evaluation cohort ($N=57$) across all historical partitions in the repository.

---

## 2. Partition and Source Group Matrix

| Partition Name | Total Clips | Total Source Groups | Mean Clips / Group | Source-Group Range |
|---|:---:|:---:|:---:|---|
| `v4_train` (Stage 8.9.38/39) | 820 | 385 | 2.13 | `sg_train_001` - `sg_train_385` |
| `v4_val` (Stage 8.9.38/39) | 339 | 158 | 2.15 | `sg_val_001` - `sg_val_158` |
| `v4_historical_test` (Stage 8.9.38/39) | 293 | 134 | 2.19 | Historical Stage 5 source groups |
| `v4_reserved_expansion_test` (Stage 8.9.39) | 102 | 49 | 2.08 | 35 short scream groups + 14 HN groups |
| `stage_8_9_40_independent_hn` (Stage 8.9.40) | 145 | 79 | 1.84 | `sg_acq_v5_001` - `sg_acq_v5_079` |
| **Stage 8.9.41 Positive Evaluation Cohort** | **57** | **41** | **1.39** | `sg_pos_v6_001` - `sg_pos_v6_045` |

---

## 3. Pairwise Disjointness Audit

Pairwise set intersection tests were performed across all six partitions:

| Partition 1 | Partition 2 | Shared Source Groups | Shared Files | Leakage Status |
|---|---|:---:|:---:|:---:|
| **Stage 8.9.41 Positive (N=57)** | `v4_train` (N=820) | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| **Stage 8.9.41 Positive (N=57)** | `v4_val` (N=339) | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| **Stage 8.9.41 Positive (N=57)** | `v4_historical_test` (N=293) | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| **Stage 8.9.41 Positive (N=57)** | `v4_reserved_expansion_test` (N=102) | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| **Stage 8.9.41 Positive (N=57)** | `stage_8_9_40_independent_hn` (N=145) | 0 | 0 | **ZERO LEAKAGE (PASS)** |
| **Stage 8.9.41 Positive (N=57)** | Stage 8.9.41 Quarantine (N=8) | 0 | 0 | **ZERO LEAKAGE (PASS)** |

**Mathematical Result:**
$$\forall P_i \ne P_{\text{stage\_8\_9\_41}}, \quad P_{\text{stage\_8\_9\_41}} \cap P_i = \emptyset$$

---

## 4. Acoustic Hash Collision Screening

1. **SHA-256 Waveform Digests:** 57 / 57 unique digests. 0 collisions across all 1,780 repository files.
2. **Linear PCM Frame Hashes:** 57 / 57 unique normalized 16-bit PCM digests. Zero identical waveforms exist under differing file names or aliases.
3. **Clip-to-Source-Group Allocation:** No source group contains more than 2 recordings (mean: 1.39 clips per source group), preventing any single speaker from dominating the evaluation.

---

## 5. Conclusion

The Stage 8.9.41 positive evaluation cohort consists of 41 genuinely independent, novel source groups that provide an unpolluted out-of-sample benchmark for evaluating recall generalization.

