# STAGE 8.9.31 — STRATEGIC DEVELOPMENT RECOMMENDATIONS & STAGE 8.9.32 ROADMAP

**Project:** Festival Scream Detector  
**Stage:** 8.9.31  
**Investigation:** Engineering Guidance & Strategic Architecture Roadmap  
**Production Status:** STRICTLY FROZEN (Threshold: 0.3500)  
**Safety Designation:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  

---

## 1. STRATEGIC CONTEXT

Stage 8.9.31 has achieved its core architectural and systems engineering objectives:
1. **End-of-stream underflow is solved:** `ResearchAudioRingBuffer` with `flush()` and right-padding guarantees that 100% of audio clips $\ge 200\text{ ms}$ are evaluated without sample loss.
2. **Dual-resolution streaming is validated:** 375 ms micro-branch captures brief startle shrieks with ~250 ms operational delay, while the 975 ms macro-branch maintains broader context.
3. **Short-scream recall improved from 16.7% to 83.3%:** Duration-Aware Fusion (Candidate C) and Padding-Aware Fusion (Candidate E) recover 5 out of 6 short screams without retraining model weights.
4. **Computational latency target met:** P95 latency is **7.5 ms** (well below the $\le 25\text{ ms}$ requirement). Zero hop deadline misses across 1, 2, and 4 concurrent streams.

However, **the audited hard-negative false positive rate remains high ($56.12\% - 58.16\%$)**, dominated by stadium cheering ($78.6\%$) and infant crying ($85.7\%$).

Because Stage 8.9.31 was an architectural and evaluation stage with a strict freeze on model weights, resolving these false alarms requires a dedicated model training stage.

---

## 2. PRIORITIZED RECOMMENDATIONS FOR STAGE 8.9.32

### Recommendation 1: Train a Dedicated Stadium Cheering & Crowd Discrimination Classifier (Priority 1 — CRITICAL)
- **Problem:** Stadium cheering and crowd applause trigger false alarms in 22 out of 28 recordings (78.6% FPR). Cheering exhibits high vocal energy and turbulent noise that mimics chaotic screams.
- **Solution:**
  - Train a dedicated binary discriminator using spectral entropy dispersion, multi-speaker harmonic superposition, and formant bandwidth divergence.
  - Integrate this discriminator as an early rejection gate before scream classification.

---

### Recommendation 2: Train an Infant Cry Discrimination Filter (Priority 2 — FALSE ALARM REDUCTION)
- **Problem:** Infant crying produces false alarms in 12 out of 14 recordings (85.7% FPR) due to high fundamental pitch ($400 - 800\text{ Hz}$) and intense phonation.
- **Solution:**
  - Exploit the characteristic periodic crying cadence ($1.2 - 2.5\text{ Hz}$ cyclic crying rhythm) to distinguish crying from sudden adult panic shrieks.

---

### Recommendation 3: Train a Native Micro-Resolution (375 ms) Short-Scream Specialist (Priority 3 — SENSITIVITY)
- **Problem:** Currently, the micro branch relies on Candidate G (an older LogisticRegression on modulation features).
- **Solution:**
  - Train a lightweight 1D-CNN or multi-layer perceptron directly on 375 ms audio frames (25 frames of 16-dim short-time features) using the 106 audited genuine screams with synthetic duration-jitter augmentation.

---

### Recommendation 4: Production Architecture Integration (Priority 4 — DEPLOYMENT PREPARATION)
- **Problem:** The live production service (`backend/src/detector/`) currently uses the legacy unpadded buffer.
- **Solution:**
  - Once model weights and false alarm rates meet the engineering targets ($\text{FPR} \le 5\%$), port the `ResearchAudioRingBuffer` flush policy and multi-resolution architecture into the production service under formal change control.

---

## 3. RECOMMENDED STAGE 8.9.32 SPRINT PLAN

| Sprint | Objective | Deliverables |
|---|---|---|
| **Sprint 1** | Model Training Environment Setup | Dataset partitions, augmentation pipeline, feature caching |
| **Sprint 2** | Cheering & Infant Cry Specialist Training | Crowd rejection model, harmonic cadence analyzer |
| **Sprint 3** | Micro-Branch Native 375ms Classifier | Dedicated short-scream neural network |
| **Sprint 4** | Full 204-Recording Audited Validation | Evaluation against Acceptance Gates ($\text{Recall} \ge 96\%$, $\text{FPR} \le 5\%$) |

---

## 4. FORMAL GOVERNANCE STATEMENT

This roadmap represents scientific and engineering recommendations based on empirical findings. In strict adherence to project rules:
- No models have been retrained.
- No production weights or metadata have been altered.
- Production decision threshold remains locked at `0.3500`.
- **Do not proceed to Stage 8.9.32 without explicit user authorization.**
"""
    p = STAGE_31_DIR / "next_development_recommendation.md"
    p.write_text(CodeContent := doc, encoding="utf-8")
    print(f"[Generated Report] {p}")


if __name__ == "__main__":
    pass
