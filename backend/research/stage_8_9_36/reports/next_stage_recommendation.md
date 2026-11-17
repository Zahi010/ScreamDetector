# Stage 8.9.36 — Evidence-Based Next-Stage Recommendation & Roadmap

**Stage:** 8.9.36 — Deep Error Forensics & Validation Audit  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Audit Dimension:** Scientific Justification for Next Research Priorities  
**Authoritative Recommendation:** **AUDIT COMPLETE — DATASET EXPANSION & TEMPORAL AGGREGATION REQUIRED BEFORE ARCHITECTURE DEVELOPMENT**  

---

## 1. Evidence-Based Determination

Based on the forensic findings of Stage 8.9.36:
- Building another neural network architecture is **NOT SCIENTIFICALLY JUSTIFIED AT THIS TIME**.
- The primary bottlenecks blocking the five acceptance gates are:
  1. **Severe Statistical Under-Sampling of Short Screams:** The test cohort contains only $N=5$ short screams (<1.0s). The 95% confidence interval spans $[56.6\%, 100.0\%]$. Validating Gate 4 ($\ge 90\%$) is statistically impossible with only 5 samples.
  2. **Harmonic Crowding in Cheering & Shouting:** 73.7% of all false alarms (14/19) are crowd cheering and shouted speech whose multi-talker harmonics activate the 2–3 kHz subband head.
  3. **Temporal Aggregation Defect (Mean Pooling Dilution):** Global average pooling over multi-second recordings dilutes brief scream bursts (e.g. `v3_fsd50k_29849` dropped to $P=0.0149$ because 7.4s of silence diluted 0.6s of screaming).
  4. **Ground-Truth Label Contamination:** 2 of the 11 missed screams (`gasp-oooh` and `surprised-oooh`) are soft gasps/sighs mislabeled as screams.

Therefore, the next research stage must prioritize **targeted dataset acquisition, label cleaning, and temporal aggregation engineering** before any further neural architecture development.

---

## 2. Ranked Research Roadmap

### Priority 1: Short-Scream Evidence Acquisition & Statistical Empowerment
- **Problem:** Gate 4 requires $\ge 90.00\%$ short-scream recall, but the test cohort contains only $N=5$ recordings, resulting in an unacceptably wide 95% Wilson confidence interval ($[56.55\%, 100.00\%]$).
- **Supporting Evidence:** Complete corpus audit identified only 23 short screams across all splits, with 0 in the $<0.5\text{s}$ test bracket.
- **Proposed Investigation:** Acquire and curate authentic, legally permissible (CC0 / CC BY) short screams of duration $0.2\text{--}0.9\text{ seconds}$ from verified public acoustic archives.
- **Required Data:** $\ge 80$ new independent short scream recordings ($\ge 35$ for the held-out test cohort to achieve statistical power).
- **Expected Outcome:** Narrow the 95% Wilson confidence interval to $\pm 8\%$, enabling rigorous statistical validation of Gate 4.
- **Risks:** Public repositories often contain clipped or synthetic scream snippets. Must verify natural acoustics and unclipped dynamic range.
- **Acceptance Criteria:** Held-out test set contains $\ge 35$ independent short screams with zero source-group overlap with training.

---

### Priority 2: Targeted Hard-Negative Collection (Festival Crowd Cheering & Chanting)
- **Problem:** Crowd cheering and chanted speech account for 36.8% of all Candidate D false alarms (7 FP, 16.67% FPR), directly breaching Gate 2 ($\le 5.00\%$).
- **Supporting Evidence:** Multi-talker acoustic summation in cheering produces aggregate vocal tract resonance in 1.5–3.0 kHz, causing the Subband head (Path C) to boost false alarm probabilities by $+0.1128$.
- **Proposed Investigation:** Curate targeted festival crowd noise, sports stadium cheering, concert applause, and synchronous group shouting under permissive licenses (CC0 / CC BY).
- **Required Data:** $\ge 150$ new independent multi-talker crowd recordings across varying acoustic densities.
- **Expected Outcome:** Provide negative contrastive training examples that penalize broad multi-voice spectral spread without suppressing isolated single-speaker scream formants.
- **Risks:** Over-penalizing cheering could inadvertently suppress screams occurring inside crowd noise.
- **Acceptance Criteria:** Multi-talker cheering FPR reduced below $8.00\%$ without reducing clean scream recall.

---

### Priority 3: Sliding-Window Temporal Max-Pooling Aggregation
- **Problem:** Mean-pooling YAMNet embeddings over full audio recordings severely penalizes short screams occurring within longer files.
- **Supporting Evidence:** `v3_fsd50k_29849` (8.0s duration with 0.6s scream) had model probability $0.0149$ because 7.4 seconds of silence diluted the embedding.
- **Proposed Investigation:** Implement a sliding temporal window aggregator (window size 975 ms, hop 200 ms) with max-pooling over hop probabilities, paired with persistence gating (requiring $\ge 2$ consecutive hops above threshold to trigger).
- **Required Data:** Existing corpus evaluated on window-level frames.
- **Expected Outcome:** Recover diluted short screams in long files, increasing overall recall by an estimated $+1.5\text{--}2.0\%$.
- **Risks:** Max-pooling can increase false positives on isolated acoustic transient clicks or coughs.
- **Acceptance Criteria:** Single-hop impulse false alarms suppressed while recovering diluted scream files.

---

### Priority 4: Test Cohort Label Sanitization
- **Problem:** 18.2% of Stage 8.9.35 false negatives (2/11) are gasps and surprised sighs that were mistakenly labeled as screams.
- **Supporting Evidence:** Files `v2_nigens_242607__reitanna__gasp-oooh` and `v2_nigens_242644__reitanna__another-surprised-oooh` have fundamental frequencies below 200 Hz and zero scream turbulence.
- **Proposed Investigation:** Audit all 102 test screams against an objective perceptual definition of human scream acoustics (sustained high vocal effort, $F_0 > 300\text{ Hz}$, nonlinear phonation, rough turbulence). Relabel non-screams as ambiguous or non-scream.
- **Expected Outcome:** Clean test cohort reflecting true scream detection performance. Candidate D recall immediately recalibrates to $91 / 100 = 91.00\%$.
- **Risks:** Must avoid test set bias or cherry-picking; relabeling must be audited by independent acoustic rules.

---

## 3. Summary Recommendation Status

The scientifically justified next stage is:

# **AUDIT COMPLETE — DATASET EXPANSION RECOMMENDED**
*(Targeting Short Screams, Multi-Talker Crowd Hard Negatives, and Sliding-Window Temporal Aggregation)*
