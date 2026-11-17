# Historical Cohort Isolation Report — Stage 8.9.55

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Exclusion Boundary
Before acquiring or qualifying any candidate recording for the Stage 8.9.55 independent evaluation cohort, a comprehensive **Historical Exclusion Registry** was established.

Total historical records registered for permanent exclusion: **2213 unique recordings**.

### Historical Partition Inventory
1. **Stage 8.9.52/53/54 Expansion Cohort:** 1732 recordings (including 1,055 training, 311 validation, and 366 historical test recordings).
2. **Stage 8.9.47/49/50/51 Independent Cohort:** 480 recordings.
3. **Production Stage 5 Test Benchmark:** 243 recordings.

---

## 2. Cryptographic & Provenance Isolation Rules

Every candidate recording considered for Stage 8.9.55 must strictly satisfy:
1. **Zero SHA-256 Collision:** $\mathcal{H}_{\text{candidate}} \notin \mathcal{H}_{\text{exclusion}}$.
2. **Zero PCM Hash Collision:** $\mathcal{PCM}_{\text{candidate}} \notin \mathcal{PCM}_{\text{exclusion}}$.
3. **Zero Source-Group Overlap:** $\mathcal{SG}_{\text{candidate}} \notin \mathcal{SG}_{\text{train}} \cup \mathcal{SG}_{\text{val}} \cup \mathcal{SG}_{\text{hist\_test}}$.
4. **Permanent Quarantine of Stage 8.9.53 Cohort:** The 366 recordings in `expansion_reserved_test` are permanently barred from serving as a fresh holdout.

---

## 3. Isolation Verdict
The exclusion registry is cryptographically locked in `integrity/historical_exclusion_registry.csv`. Zero historical recordings or source groups may enter the Stage 8.9.55 cohort.
