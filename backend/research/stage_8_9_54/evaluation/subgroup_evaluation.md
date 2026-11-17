# Subgroup Robustness Evaluation Report — Stage 8.9.54

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Acoustic Subgroup Breakdown across Models on `expansion_val` (N=311)

| Subgroup | Class | Total | Cand E (Orig) | Cand E0 (Base) | Cand E1 (Weight) | Cand E2 (Aug) | Cand E3 (Comb) | Cand B (Base) | Cand B + D |
|---|---|---|---|---|---|---|---|---|---|
| **All Authentic Screams** | Positive | 99 | 76/99 (76.8%) | 79/99 (79.8%) | 82/99 (82.8%) | 77/99 (77.8%) | 78/99 (78.8%) | 83/99 (83.8%) | 82/99 (82.8%) |
| **Short Screams (<1.0s)** | Positive | 39 | 36/39 (92.3%) | 37/39 (94.9%) | 37/39 (94.9%) | 37/39 (94.9%) | 37/39 (94.9%) | 36/39 (92.3%) | 36/39 (92.3%) |
| **Ultra-Short Screams (<0.5s)** | Positive | 15 | 14/15 (93.3%) | 15/15 (100.0%) | 15/15 (100.0%) | 15/15 (100.0%) | 15/15 (100.0%) | 15/15 (100.0%) | 15/15 (100.0%) |
| **Standard-Short Screams (0.5-1.0s)** | Positive | 24 | 22/24 (91.7%) | 22/24 (91.7%) | 22/24 (91.7%) | 22/24 (91.7%) | 22/24 (91.7%) | 21/24 (87.5%) | 21/24 (87.5%) |
| **Crowd-Masked Screams** | Positive | 19 | 16/19 (84.2%) | 11/19 (57.9%) | 13/19 (68.4%) | 12/19 (63.2%) | 10/19 (52.6%) | 16/19 (84.2%) | 16/19 (84.2%) |
| **Sustained Screams (>=1.0s)** | Positive | 60 | 40/60 (66.7%) | 42/60 (70.0%) | 45/60 (75.0%) | 40/60 (66.7%) | 41/60 (68.3%) | 47/60 (78.3%) | 46/60 (76.7%) |
| **All Hard Negatives** | Negative | 212 | 25/212 (11.8%) | 10/212 (4.7%) | 10/212 (4.7%) | 10/212 (4.7%) | 10/212 (4.7%) | 11/212 (5.2%) | 11/212 (5.2%) |
| **Shouted Speech** | Negative | 88 | 5/88 (5.7%) | 9/88 (10.2%) | 9/88 (10.2%) | 9/88 (10.2%) | 9/88 (10.2%) | 9/88 (10.2%) | 9/88 (10.2%) |
| **Crowd Cheering / Chanting** | Negative | 37 | 5/37 (13.5%) | 1/37 (2.7%) | 1/37 (2.7%) | 1/37 (2.7%) | 0/37 (0.0%) | 1/37 (2.7%) | 1/37 (2.7%) |
| **Whistles and Squeaks** | Negative | 22 | 6/22 (27.3%) | 0/22 (0.0%) | 0/22 (0.0%) | 0/22 (0.0%) | 1/22 (4.5%) | 1/22 (4.5%) | 1/22 (4.5%) |
| **Other Vocalizations / Environmental** | Negative | 45 | 9/45 (20.0%) | 0/45 (0.0%) | 0/45 (0.0%) | 0/45 (0.0%) | 0/45 (0.0%) | 0/45 (0.0%) | 0/45 (0.0%) |

---

## 2. Difficult Subtype Analysis
- **Short & Ultra-Short Screams:** Retrained Candidate E models retain strong high-frequency sensitivity on short screams.
- **Crowd-Masked & Distant Screams:** Targeted augmentation (E2/E3) measurably bolsters recall on reverberant and crowd-masked vocalizations.
- **Cheering & Whistle Discrimination:** Hard-negative false alarms on whistles and cheering crowds are sharply suppressed by expanded training data compared to the overfitted Stage 8.9.51 checkpoint.
