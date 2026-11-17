# STAGE 8.9.31 — RESEARCH BASELINE REPRODUCTION & ENVIRONMENT VERIFICATION

**Project:** Festival Scream Detector  
**Stage:** 8.9.31  
**Operating Mode:** Offline-First Research & Systems Engineering  
**Production Status:** STRICTLY FROZEN (Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Date:** November 2, 2026  

---

## 1. RESEARCH ENVIRONMENT & ARTIFACT RECOVERY

All 6 short-scream recordings from Stage 8.9.30 and Stage 8.9.30.2 have been recovered and validated:

| Recording ID | Original Source ID | Uploader | Duration (s) | Samples (16 kHz) | Audited Label | Stage 30 Reported Prob | Stage 30.2 Padded Prob |
|---|---|---|---|---|---|---|---|
| `S8930_FS_686340` | 686340 | trim8361 | 0.395 s | 6,316 | GENUINE_SCREAM | 0.0000 | 0.2882 |
| `S8930_FS_222582` | 222582 | queen_westeros | 0.719 s | 11,496 | GENUINE_SCREAM | 0.0000 | 0.2809 (Cand G: 0.5008) |
| `S8930_FS_382990` | 382990 | JúliaLN | 0.421 s | 6,736 | GENUINE_SCREAM | 0.0000 | 0.2594 (Cand G: 0.3691) |
| `S8930_FS_547188` | 547188 | MrFossy | 0.766 s | 12,255 | GENUINE_SCREAM | 0.0000 | 0.3381 (Cand G: 0.4009) |
| `S8930_FS_788867` | 788867 | riippumattog | 0.650 s | 10,403 | GENUINE_SCREAM | 0.0000 | **0.7578 (POSSIBLE_SCREAM)** |
| `S8930_NIGENS_15246` | HDF-15246 | nigens_zenodo | 0.499 s | 7,988 | GENUINE_SCREAM | 0.0000 | 0.2808 (Cand G: 0.3725) |

---

## 2. REPRODUCED BASELINE LIMITATIONS

1. **Ingestion Underflow:** The baseline ring buffer discarded all files shorter than 15,600 samples, reporting 0.0000 probability.
2. **Padding Dilution in Model C:** When zero-padded to 0.975s, 50-60% of temporal frames are silence, dropping Model C 1D-CNN confidence below 0.06.
3. **Asymmetric Fusion Disagreement Penalty:** Fusion E heavily penalized Model C's silence-induced low score, dragging the fused score below the 0.3500 threshold on 5 of 6 files despite Candidate G scoring positive (> 0.3500) on 5 files.
4. **Hard-Negative Vulnerability:** False alarms on stadium cheering (78.6%) and infant crying (85.7%) persist in the baseline.

---

## 3. PRODUCTION FREEZE INTEGRITY

All 4 authoritative production hashes were verified byte-for-byte identical to their locked reference signatures. No production files have been modified.
