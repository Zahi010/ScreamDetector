# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Stage 8.9.65 Limitations & Open Issues Report

## 1. Safety & Operational Constraints

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.**
- This system is an experimental acoustic research prototype and is not certified for emergency detection, life-safety alerting, autonomous dispatch, police notification, or critical physical security deployments.
- All experiments conducted within this stage utilize legally acquired pre-recorded audio datasets and controlled engineering playback benchmarks only.
- No live-fire testing, human panic simulations, or autonomous alerts to municipal first responders are authorized or conducted.
- Production promotion of experimental dual-resolution weights is strictly prohibited. Production assets remain frozen.

---

## 2. Research Limitations Identified in Stage 8.9.65

### 2.1 Diagnostic Shouted-Speech Sample Size ($N=5$)
- In the $N=312$ development cohort, only 5 recordings in the hard-negative pool represent vocal outcries or shouted speech.
- While Candidate 65-F achieved an $80.0\%$ reduction in shouted-speech false positives relative to baseline ($1$ FP vs $5$ FPs), the empirical $95\%$ Wilson confidence interval with $N=5$ remains wide ($[3.62\%, 62.45\%]$).
- A statistically definitive evaluation of Gate 3 requires an expanded, dedicated shouted-speech evaluation cohort ($N \ge 120$), as formalized in Track H.

### 2.2 Fundamental Recall-FPR Pareto Tension on Development Cohort
- At decision threshold $\tau = 0.50$, Candidate 65-F achieves **$94.36\%$ recall** (recovering all 13 screams lost by Variant 6) and **$5.13\%$ FPR** (within $0.13\%$ of Gate 2).
- Operating at threshold $\tau = 0.60$ drops FPR to **$3.42\%$** (**PASS Gate 2**), but drops recall to **$90.77\%$**.
- Operating at threshold $\tau = 0.26$ lifts recall to **$96.92\%$** (**PASS Gate 1**), but increases FPR to **$41.88\%$**.
- Achieving simultaneous Gate 1 ($\ge 96\%$) and Gate 2 ($\le 5\%$) pass on this specific $N=312$ development cohort requires advanced multi-window feature pooling or multi-task branch decoupling.

### 2.3 Reverberation & Low-RMS Edge Cases in Sustained Screams
- 9 sustained screams in the development cohort remain persistent misses at threshold $0.50$.
- These vocalizations are characterized by severe room reverberation, multi-second crescendo onsets, or heavy background noise masking formants above $3.5\text{ kHz}$.
- Sliding multi-window max pooling recovers these events (lifting sustained recall to $87.10\%\text{--}95.16\%$), but elevates false alarm susceptibility in un-gated configurations.

---

## 3. Prioritized Open Issues for Future Stages

1. **Issue 65-1 (Sealed Cohort Execution):** Execute the preregistered independent evaluation plan on the planned $N=1,050$ cohort with $N=120$ dedicated shouted-speech controls.
2. **Issue 65-2 (Embedded C++ DSP Integration):** Port the short-branch C5 sliding window extraction logic to an optimized C++/Rust streaming library for sub-millisecond edge processing on embedded ARM hardware.
3. **Issue 65-3 (Dynamic Multi-Scale Window Fusion):** Investigate continuous temporal attention networks to bridge the 250ms and 1,000ms representations without rigid threshold heuristics.

---

## 4. Artifact Links
- Scorecard Report: [authoritative_acceptance_gate_report.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/authoritative_acceptance_gate_report.md)
- Test Report: [stage_8_9_65_test_report.md](file:///C:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_65/stage_8_9_65_test_report.md)

