# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Project Limitations, Open Technical Issues & Future Research Roadmap — Stage 8.9.63

**Stage Designation:** STAGE 8.9.63  
**Date:** November 11, 2026  
**Status:** FORMAL RECORD OF SYSTEM LIMITATIONS AND ROADMAP  

---

## 1. Executive Summary

Stage 8.9.63 made significant methodological and architectural breakthroughs:
1. Reconciled all cross-stage prediction records bit-for-bit, proving historical data integrity.
2. Verified the mathematical and acoustic basis of short-scream zero-padding dilution.
3. Prototyped an asymmetric dual-resolution architecture achieving $98.50\%$ short-scream recall on development data.
4. Restored the original five project acceptance gates without dilution.

Despite these advancements, the system remains an experimental research prototype. It exhibits critical technical limitations that prevent production deployment or life-safety use. This report provides a candid, forensic assessment of open vulnerabilities, dataset shortfalls, and the technical roadmap toward Stage 8.9.64.

---

## 2. Dataset Limitation: Formal INSUFFICIENT_DEVELOPMENT_EVIDENCE Designation

### 2.1 Target vs. Acquired Short-Scream Cohort
- **Target Short-Scream Cohort:** $\ge 150$ unique, legally verified short screams ($\le 0.50$ s duration).
- **Acquired Short-Scream Cohort:** $133$ unique, legally verified short screams across 86 independent source groups.
- **Acquisition Yield:** $88.67\%$ (17 recordings short of the target).
- **Formal Status:** `INSUFFICIENT_DEVELOPMENT_EVIDENCE`

### 2.2 Forensic Rejection Reasons
During data acquisition, 28 prospective short-event candidate audio files were rejected due to strict legal, ethical, and acoustic governance boundaries:
1. **License Ineligibility (12 candidate files):** Identified with CC-BY-NC (Non-Commercial) or undefined provenance, violating open-source repository licensing guidelines.
2. **Audio Leakage & Provenance Contamination (6 candidate files):** Derived from YouTube creators or freesound uploaders whose content already appeared in the sealed 700-recording evaluation cohort or historical training sets.
3. **Synthetic / AI Generation Artifacts (5 candidate files):** High-frequency unnatural comb-filtering and phase discontinuities characteristic of early text-to-speech vocoders.
4. **Acoustic Ambiguity / Dual Annotator Discordance (5 candidate files):** Annotators differed on whether the sound was a short vocal scream vs. an involuntary pain grunt, gasp, or laughter burst. Under our dual-blind protocol ($\kappa = 0.8553$), ambiguous events are discarded.

---

## 3. Acoustic and Algorithmic Vulnerabilities

### 3.1 Shouted-Speech Discrimination Deficit (Gate 3 Failure)
- **Current Shouted-Speech FPR:** $20.69\%$ on development data ($26.67\%$ on historical test cohorts; $66.67\%$ in rolling windows without temporal filtering).
- **Acoustic Etiology:** Shouted speech in festival crowd environments produces elevated vocal effort, elevated subglottal pressure, and vocal fold non-linearities (e.g., subharmonics, jitter, shimmer). These produce acoustic features (wideband spectral dispersion, high phonation energy) overlapping with genuine distress screams.
- **Required Remediation:** Incorporation of harmonic-to-noise ratio (HNR), formantic trajectory variance, and multi-frame vocal tract stability features.

### 3.2 High-Energy Brass and Metallic Transient Vulnerabilities (Gate 2 Failure)
- **Current Hard-Negative FPR:** $10.26\%$ (even with $K=2$ temporal aggregation), exceeding the $\le 5.0\%$ Gate 2 threshold.
- **Acoustic Etiology:** Musical trumpet blasts, synthesizers, distortion pedals, screeching metal doors, and feedback squeals exhibit concentrated high-frequency spectral energy and rapid onset envelopes that trigger the short-resolution subband extractor.
- **Required Remediation:** Hard-negative contrastive fine-tuning and spectral crest factor penalization.

---

## 4. Systems and Multi-Stream Engineering Considerations

### 4.1 Single-Core DSP Bottlenecks Under High Concurrency
- **Observation:** While the neural network forward pass executes in $<0.010$ ms per stream (benefiting from batched tensor operations), the C5 DSP feature extraction pipeline executes sequentially per audio buffer on CPU.
- **Impact:** At 8 concurrent streams, cumulative DSP processing time scales linearly ($8 \times \sim 1.25\text{ ms} = 10.0\text{ ms}$). While this remains well within the $50$ ms real-time hop deadline (giving an $>80\%$ margin), scaling to 16 or 32 concurrent channels will require multi-threaded SIMD parallelization or PyTorch GPU/vectorized DSP kernels.

### 4.2 Stream Memory Buffering
- Each audio stream requires maintaining independent circular buffers for the short branch ($250$ ms / $4,000$ samples), sustained branch ($1000$ ms / $16,000$ samples), and temporal filter state ($K=2$ circular buffer, EMA accumulator, refractory cooldown timer).
- Memory per stream is strictly bounded ($\approx 128$ KB per active stream), but robust multi-stream lifecycle management is necessary to prevent memory fragmentation during dynamic stream attach/detach operations.

---

## 5. Preregistered Roadmap for Stage 8.9.64

Stage 8.9.64 will be executed under the following phased roadmap:

1. **Phase 1: Dataset Completion & Gap Closure**
   - Acquire the remaining 17 short-scream recordings to achieve the $\ge 150$ threshold from fully certified, independent CC0/CC-BY sources.
   - Expand hard-negative festival crowd noise and shouting speech datasets to enable contrastive fine-tuning.

2. **Phase 2: End-to-End Dual-Resolution Model Training**
   - Implement end-to-end backpropagation through a joint multi-scale CNN/MLP architecture on the completed 329+ development cohort.
   - Integrate Harmonic-to-Noise Ratio (HNR) and spectral flatness metrics into the feature representation to suppress brass and shouted-speech false positives.

3. **Phase 3: Vectorized Multi-Stream Audio Engine**
   - Refactor the C5 DSP extractor to operate on multi-channel batched NumPy/PyTorch arrays, reducing 8-stream DSP latency from $10.0$ ms to $<2.0$ ms.

4. **Phase 4: Sealed Independent Evaluation ($N=1,050$)**
   - Execute the preregistered evaluation protocol on the new sealed $N=1,050$ cohort ($N_{\text{pos}}=240, N_{\text{neg}}=810$ across $\ge 600$ disjoint source groups).
   - Evaluate all candidates against the restored 5 acceptance gates with zero tuning or post-hoc threshold calibration.

---

## 6. Safety Compliance Statement

This system is strictly a research prototype. Operating in life-safety, physical security, or autonomous alert capacities is strictly prohibited. Zero production promotion is authorized.

