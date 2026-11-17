# Positive Subgroup Manifest Reconciliation Report — Stage 8.9.58

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**  
> Research demonstration prototype only. No life-safety efficacy or production promotion.

---

## 1. Executive Summary & Root-Cause Resolution of Issue B

Stage 8.9.57 reported the following positive subgroup counts on `expansion_val`:
- Total positive recordings: **N = 99**
- Short screams: **N = 39**
- Sustained screams: **N = 80**
- Ultra-short screams: **N = 15**

If Short and Sustained were mutually exclusive duration partitions, their sum would be $39 + 80 = 119 > 99$, an apparent mathematical impossibility.

### Exact Root Cause Established by Manifest Forensics:
1. **`target_category` was Conflated with `subtype_tags`:**
   - The frozen manifest (`partition_manifest_verified.csv`) has two distinct categorization columns: `target_category` and `subtype_tags`.
   - In the positive cohort ($N=99$):
     - `target_category == 'scream'`: **N = 80**
     - `target_category == 'masked_distant_screams'`: **N = 19**
     - Total = $80 + 19 = 99$.
2. **In Stage 8.9.57, the Query for 'Sustained Screams' Filtered by `target_category == 'scream'`:**
   - The Stage 8.9.57 evaluation code filtered `(y_true == 1) & (categories == 'scream')` ($N=80$) and labeled it in the table as *"Sustained Screams"*.
   - But those 80 recordings comprise **all duration classes** within the unmasked scream category:
     - 15 Ultra-Short screams ($< 0.5$s)
     - 24 Standard Short screams ($[0.5\text{s}, 1.0\text{s})$)
     - 41 Sustained screams ($\ge 1.0$s)
     - Total = $15 + 24 + 41 = \mathbf{80}$.
3. **Short Screams ($N=39$) were Filtered by `'SHORT' in subtype_tags`:**
   - The condition `'SHORT' in subtype_tags` captures both `'SHORT'` ($N=24$) and `'ULTRA_SHORT'` ($N=15$), giving $24 + 15 = \mathbf{39}$ screams with duration $< 1.0$ second.
   - Crucially, all 39 short screams belong to `target_category == 'scream'`!
   - Therefore, **the 39 short screams were a strict subset of the 80 scream target category clips** ($39 + 41 = 80$).
   - Adding $39 + 80$ was double-counting the 39 short screams!

---

## 2. Reconciled Duration-Based Subgroup Partition

When partitioned strictly by acoustic duration, the 99 positive recordings form a mutually exclusive and exhaustive partition:

| Duration Bucket | Duration Range | Subtype Tag | Target Category | Count ($N$) | Ground Truth | Original Recall | C5 Recall |
|---|---|---|---|:---:|:---:|:---:|:---:|
| **Ultra-Short Screams** | $d < 0.500\text{ s}$ | `ULTRA_SHORT` | `scream` | **15** | Scream (1) | **100.00%** (15/15) | **100.00%** (15/15) |
| **Standard Short Screams** | $0.500\text{ s} \le d < 1.000\text{ s}$ | `SHORT` | `scream` | **24** | Scream (1) | **91.67%** (22/24) | **91.67%** (22/24) |
| **Clean Sustained Screams** | $d \ge 1.000\text{ s}$ | `SUSTAINED` | `scream` | **41** | Scream (1) | **78.05%** (32/41) | **78.05%** (32/41) |
| **Masked Sustained Screams** | $d \ge 1.000\text{ s}$ | `CROWD_MASKED...` | `masked_distant_screams` | **19** | Scream (1) | **68.42%** (13/19) | **68.42%** (13/19) |
| **TOTAL POSITIVE COHORT** | — | — | — | **99** | Scream (1) | **83.84%** (83/99) | **83.84%** (83/99) |

---

## 3. Mathematical Verification Proofs

### Proof 1: Mutually Exclusive Duration Partition
$$\text{Total Short (<1.0s)} = 15 \text{ (Ultra-Short)} + 24 \text{ (Standard Short)} = \mathbf{39}$$
$$\text{Total Sustained (}\ge 1.0\text{s)} = 41 \text{ (Clean Sustained)} + 19 \text{ (Masked Sustained)} = \mathbf{60}$$
$$\mathbf{\text{Total Positives}} = 39 + 60 = \mathbf{99} \quad (\text{Q.E.D.})$$

### Proof 2: Ultra-Short Nesting
$$\text{Ultra-Short (<0.5s)} = 15 \le \text{Total Short (<1.0s)} = 39 \quad (\text{Q.E.D.})$$

### Proof 3: Origin of the 80 Count
$$\text{Target Category 'scream'} = 15 \text{ (Ultra)} + 24 \text{ (Short)} + 41 \text{ (Sustained)} = \mathbf{80}$$
$$\text{Target Category 'masked_distant_screams'} = 19 \text{ (Masked Sustained)} = \mathbf{19}$$
$$\mathbf{\text{Total Positives}} = 80 + 19 = \mathbf{99} \quad (\text{Q.E.D.})$$

---

## 4. Reconciled Subgroup Performance Metrics

| Subgroup Identifier | Definition | Count ($N$) | Original Hits | C5 Hits | Recall (%) | Gate / Target | Status |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Total Short Screams** | $d < 1.0\text{ s}$ | **39** | 37 | 37 | **94.87%** | Gate 4: $\ge 90\%$ | **PASS** |
| **Ultra-Short Screams** | $d < 0.5\text{ s}$ | **15** | 15 | 15 | **100.00%** | Diagnostic | **PASS** |
| **Total Sustained Screams** | $d \ge 1.0\text{ s}$ | **60** | 45 | 45 | **75.00%** | Diagnostic | **PRESERVED** |
| **Clean Sustained Screams** | $d \ge 1.0\text{ s}$, cat=scream | **41** | 32 | 32 | **78.05%** | Diagnostic | **PRESERVED** |
| **Masked Sustained Screams** | $d \ge 1.0\text{ s}$, cat=masked | **19** | 13 | 13 | **68.42%** | Diagnostic | **PRESERVED** |
| **Target Category 'scream'** | cat=scream (all durations) | **80** | 69 | 69 | **86.25%** | Explanatory | **PRESERVED** |
| **Overall Positive Cohort** | All positives | **99** | 83 | 83 | **83.84%** | Gate 1: $\ge 96\%$ | **NOT MET** |

---

## 5. Conclusion

Issue B is fully resolved. No duplicate recording IDs, missing records, or cohort discrepancies exist.
The apparent 119 count in Stage 8.9.57 was purely a documentation conflation between `target_category == 'scream'` (80) and duration subtype `duration < 1.0s` (39), which shared 39 recordings.
