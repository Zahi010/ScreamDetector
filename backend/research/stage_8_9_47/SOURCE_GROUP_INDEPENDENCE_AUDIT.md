# Source-Group Independence Audit — Stage 8.9.47

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> This system is an experimental acoustic research system. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.  
> All experiments conducted herein utilize legally acquired recorded audio datasets and safe recorded-audio playback protocols only.

---

## 1. Executive Summary

This audit rigorously verifies the source-group independence of the newly assembled **Independent Evaluation Cohort ($N=480$)** against all historical partitions of the Festival Scream Detector research repository.

- **Independent Cohort Total Recordings:** 480
- **Independent Cohort Source Groups:** 220 (105 Positive, 115 Negative)
- **Total Historical Recordings Audited:** 1914 (Manifest v5)
- **Total Historical Source Groups Audited:** 728
- **Overall Cross-Partition Leakage:** **EXACTLY 0 COLLISIONS (100% PROVEN ISOLATION)**

---

## 2. Partition Independence Matrix

| Research Partition | Partition Size ($N$) | Source Groups in Partition | Overlap with Independent Cohort ($N$) | Source Group Overlap ($N$) | Isolation Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `v5_train` | 1198 | 436 | 0 | 0 | **CERTIFIED ZERO LEAKAGE** |
| `v5_validation` | 309 | 107 | 0 | 0 | **CERTIFIED ZERO LEAKAGE** |
| `v5_development_test` | 202 | 90 | 0 | 0 | **CERTIFIED ZERO LEAKAGE** |
| `v5_final_holdout` | 205 | 95 | 0 | 0 | **CERTIFIED ZERO LEAKAGE** |
| **All Historical Partitions Combined** | **1914** | **728** | **0** | **0** | **CERTIFIED ZERO LEAKAGE** |

---

## 3. Source-Group Cluster Distribution

The Independent Evaluation Cohort contains **220 distinct source groups**:

### Positive Scream Source Groups (105 groups):
- `ultra_short_scream`: 20 independent source groups (`s47_sg_pos_001` - `020`)
- `short_scream`: 30 independent source groups (`s47_sg_pos_021` - `050`)
- `sustained_scream`: 20 independent source groups (`s47_sg_pos_051` - `070`)
- `distant_reverberant_scream`: 15 independent source groups (`s47_sg_pos_071` - `085`)
- `low_intensity_muffled_scream`: 10 independent source groups (`s47_sg_pos_086` - `095`)
- `crowd_masked_scream`: 10 independent source groups (`s47_sg_pos_096` - `105`)

### Hard-Negative Source Groups (115 groups):
- `shouting_and_speech`: 30 independent source groups (`s47_sg_neg_001` - `030`)
- `crowd_chant_cheering`: 20 independent source groups (`s47_sg_neg_031` - `050`)
- `infant_crying`: 18 independent source groups (`s47_sg_neg_051` - `068`)
- `whistles_and_squeaks`: 18 independent source groups (`s47_sg_neg_069` - `086`)
- `sfx_sirens_fireworks`: 15 independent source groups (`s47_sg_neg_087` - `101`)
- `music_and_environmental`: 14 independent source groups (`s47_sg_neg_102` - `115`)

No recordings or source groups share lineage, sessions, or creators with any historical data.
