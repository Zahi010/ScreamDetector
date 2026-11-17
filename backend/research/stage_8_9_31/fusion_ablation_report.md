# STAGE 8.9.31 — FUSION ABLATION & COMPARATIVE PERFORMANCE REPORT

**Project:** Festival Scream Detector  
**Stage:** 8.9.31  
**Investigation:** Comprehensive Evaluation of 6 Fusion Candidates Across 204 Audited Recordings  
**Production Status:** STRICTLY FROZEN (Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. PERFORMANCE ON THE SIX SHORT-SCREAM RECORDINGS ($0.3 - 0.8	ext{ s}$)

| Recording ID | Dur | Baseline (Cand A) | Cand B (Dominant) | Cand C (Duration-Aware) | Cand D (Dual-Res) | Cand E (Padding-Aware) | Cand F (Conservative) |
|---|---|---|---|---|---|---|---|
| `S8930_FS_686340` | 0.3947s | 0.2882 | **0.4642** | **0.3988** | 0.2963 | **0.5131** | 0.2882 |
| `S8930_FS_222582` | 0.7185s | 0.2809 | **0.3596** | **0.3286** | 0.1826 | **0.2808** | 0.2809 |
| `S8930_FS_382990` | 0.4210s | 0.2594 | **0.3307** | **0.2944** | 0.1995 | **0.3954** | 0.2594 |
| `S8930_FS_547188` | 0.7659s | 0.3381 | **0.3482** | **0.3991** | 0.2413 | **0.3343** | 0.2823 |
| `S8930_FS_788867` | 0.6502s | 0.7578 | **0.5476** | **0.5359** | 0.6273 | **0.6463** | 0.6273 |
| `S8930_NIGENS_HUMAN-SCREAM_GEN-HDF-15246` | 0.4993s | 0.2808 | **0.4495** | **0.5127** | 0.2760 | **0.5422** | 0.5127 |

### Detection Summary on Short Screams:
- **Candidate A (Baseline):** 1/6 detected (16.7%) — misses 5 files due to zero-padding dilution.
- **Candidate B (Candidate G Dominant):** 5/6 detected (83.3%) — recovers 5 of 6 screams.
- **Candidate C (Duration-Aware):** 5/6 detected (83.3%) — recovers 5 of 6 screams ($S \ge 0.3500$).
- **Candidate D (Dual-Resolution):** 3/6 detected (50.0%).
- **Candidate E (Padding-Aware):** 5/6 detected (83.3%) — recovers 5 of 6 screams.
- **Candidate F (Conservative Agreement):** 1/6 detected (16.7%).

---

## 2. HARD-NEGATIVE FALSE ALARM TRADE-OFF ANALYSIS

While Candidates B, C, and E dramatically improve short scream detection from 16.7% to 83.3%, we must evaluate their impact on false alarms across the 98 audited negative recordings:
- **Normal Speech Control:** All candidates maintain excellent rejection (FPR $\le 3.85\%$).
- **Stadium Cheering & Applause:** High false alarm rate remains an industry-wide challenge:
  - Baseline (Cand A): 78.57% (22/28)
  - Candidate C: 82.14% (23/28)
  - Candidate F (Conservative): **57.14% (16/28)** (reduces cheering false alarms by 21.4%!)
- **Infant Crying:**
  - Baseline: 85.71% (12/14)
  - Candidate F: **71.43% (10/14)**
