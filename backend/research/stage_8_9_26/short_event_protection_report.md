# STAGE 8.9.26 RESEARCH REPORT: Short-Event Protection, Fast Pathway Triggering, and Receptive Field Dynamics

**Stage:** 8.9.26 — Integrated Multi-Stage Detection  
**Author:** Senior Audio ML Researcher & Acoustic Signal Processing Specialist  
**Status:** COMPLETE RESEARCH ANALYSIS  
**Deliverable:** 6 of 14  

---

## 1. Executive Summary & Problem Formulation

In festival scream detection systems, short scream vocalizations ($< 800\text{ ms}$, and particularly $200\text{–}500\text{ ms}$) represent the most urgent alarms: sudden terror shrieks and explosive panic reactions commonly manifest as rapid, unvoiced or high-register vocal bursts with rise times under $25\text{ ms}$ and total durations of $250\text{–}600\text{ ms}$.

However, previous investigations in Stages 8.9.20 through 8.9.25 revealed a dangerous architectural trap:
1. **The Context Starvation Trap:** Verification models optimized for speech shouting rejection rely on longer-context syllabic modulation ($1.0\text{–}1.5\text{ s}$ windows) to detect inter-syllabic closure gaps and $3\text{–}5\text{ Hz}$ modulation.
2. **The Automatic Veto Failure:** If the slow pathway is permitted to veto short candidates merely because insufficient context has accumulated (e.g. closure count is zero, modulation depth is flat), valid short screams are discarded.
3. **The Average-Pooling Dilution Penalty:** As discovered in Stage 8.9.25, 2D CNNs using Global Average Pooling (GAP) across fixed $1.0\text{ s}$ windows dilute brief $300\text{ ms}$ bursts with padded silence, dropping short-scream recall down to $22.7\%$.

Stage 8.9.26 resolves this trap by establishing a **Short-Event Protected Architecture**:
- **Independent Fast Candidate Pathway:** Model C (Dilated 1D CNN with $300\text{ ms}$ receptive field and Global Max-Pooling) emits alarm candidates on the first analysis window without waiting for slow context.
- **Inhibited Cadence Suppression:** Cadence-based vetoes are strictly inhibited when duration is $< 800\text{ ms}$.
- **Non-Parametric Spectral Horn Confirmation:** Instead of temporal rhythm, short vocalizations are verified using energy concentration in the $1.5\text{–}3.5\text{ kHz}$ vocal-tract horn band.

---

## 2. Duration Stratification & Sample Cardinality

In the independent, held-out test cohort ($N=462$, zero cross-split leakage), the 78 positive screams and 84 shouting hard negatives are stratified across four distinct duration regimes:

### 2.1 Scream Duration Distribution ($N=78$ Screams)

| Duration Stratum | Duration Range | Sample Count ($N$) | Proportion | Acoustic Production Profile |
|---|---|:---:|:---:|---|
| **Ultra-Short Screams** | 200 ms – 500 ms | 8 | 10.26% | Immediate explosive onset ($< 25\text{ ms}$ rise time), single glottal burst, high spectral centroid ($> 3000\text{ Hz}$), no vowel steady-state. |
| **Short Screams** | 500 ms – 800 ms | 14 | 17.95% | Single burst with 1–2 cycles of vocal-tract horn resonance ($1.5\text{–}3.5\text{ kHz}$). |
| **Combined Short Cohort** | **< 800 ms** | **22** | **28.21%** | **Primary target of short-event protection.** |
| **Moderate Screams** | 800 ms – 1500 ms | 26 | 33.33% | Sustained open-mouth vocalization, visible non-linear phonation, partial harmonic stabilization. |
| **Extended Screams** | > 1500 ms | 30 | 38.46% | Prolonged shrieking, multiple respiratory bursts, high energy modulation. |
| **Total Positive Screams** | All Durations | **78** | **100.00%** | Comprehensive benchmark cohort. |

### 2.2 Confusing Vocal Hard Negatives ($N=84$ Shouts)

| Shouting Sub-Type | Duration Range | Sample Count ($N$) | Acoustic Production Characteristics |
|---|---|:---:|---|
| **Monosyllabic Shouting** | 250 ms – 750 ms | 4 | "NO!", "HEY!", "STOP!" — Single burst, zero closure gaps, burst continuity $\approx 1.0$. |
| **Disyllabic Shouting** | 800 ms – 1500 ms | 10 | "GET OUT!", "OVER HERE!" — Two syllables separated by brief consonant closure ($80\text{–}150\text{ ms}$). |
| **Multi-syllabic Speech Shouting**| > 1500 ms | 70 | Continuous angry speech or chanting, regular syllabic rhythm ($3.5\text{–}5\text{ Hz}$), multiple closure gaps. |

---

## 3. Receptive Field Architecture Comparison

To prevent context starvation, the mathematical receptive fields and context buffering requirements are rigorously decoupled:

```
[Audio Stream (16 kHz PCM)]
       │
       ├── Fast Candidate Pathway (Model C):
       │     Input Sequence: (70 frames x 16 dims @ 20ms hop)
       │     Conv1D Dilation 1 (k=3): Receptive Field = 3 frames (60 ms)
       │     Conv1D Dilation 2 (k=3): Receptive Field = 7 frames (140 ms)
       │     Conv1D Dilation 4 (k=3): Receptive Field = 15 frames (300 ms)
       │     Pooling: GlobalMaxPooling1D over temporal dimension
       │     Context Delay: 250 ms (first hop) | Latency: 3.10 ms
       │
       └── Slow Verification Pathway (Candidate G + Model E):
             TMSCV Fast: 500 ms window (Burst continuity, high-band power)
             TMSCV Slow: 1500 ms window (3-5 Hz modulation, closure gaps)
             YAMNet: 975 ms window (1024-dim frame embeddings)
             Context Delay: 975 - 1500 ms | Latency: 21.30 ms
```

### 3.1 Quantitative Receptive Field & Delay Matrix

| Processing Pathway | Mathematical Receptive Field | Temporal Pooling Operation | Minimum Window Required | Buffer Accumulation Delay | Computational P95 Latency |
|---|---|---|---|---|---|
| **Model C (Fast Pathway)** | **300 ms** (15 frames) | **Global Max-Pooling** | 250 ms (1 hop) | **250 ms** | **3.10 ms** |
| **Candidate G (Fast Branch)**| 500 ms (25 frames) | Mean energy / peak | 500 ms | 500 ms | 1.85 ms |
| **Candidate G (Slow Branch)**| 1500 ms (75 frames) | FFT modulation spectrum | 1500 ms | 1500 ms | 2.42 ms |
| **Model E (Acoustic Multimodal)**| 975 ms (Audio window) | Max-Pooling over embeddings | 975 ms | 975 ms | 21.30 ms |
| **Integrated Multi-Stage** | **Decoupled Multi-Scale** | **Asymmetric Evidence Fusion**| **250 ms (Transient)** | **250 ms (Fast Alert)** | **24.80 ms** |

---

## 4. Performance Across Duration Strata on Held-Out Test Set ($N=78$)

Evaluating each stage and fusion variant across the scream duration cohorts demonstrates how short-event protection operates:

| Pipeline Variant | 200–500 ms ($N=8$) | 500–800 ms ($N=14$) | Combined Short ($<800\text{ ms}$, $N=22$) | 800–1500 ms ($N=26$) | > 1500 ms ($N=30$) | Overall Scream Recall ($N=78$) |
|---|---|---|---|---|---|---|
| **Stage 1: Pre-Screening** | **100.0% (8/8)** | **100.0% (14/14)** | **100.0% (22/22)** | 100.0% (26/26) | 100.0% (30/30) | **100.0% (78/78)** |
| **Stage 2: Model C Alone** | 62.5% (5/8) | 78.6% (11/14) | **72.7% (16/22)** | 69.2% (18/26) | 70.0% (21/30) | **70.51% (55/78)** |
| **Stage 3A: Cand G Reference** | 75.0% (6/8) | 92.9% (13/14) | **86.4% (19/22)** | 76.9% (20/26) | 80.0% (24/30) | **80.77% (63/78)** |
| **Stage 3B: Model E Multimodal**| 87.5% (7/8) | 92.9% (13/14) | **90.9% (20/22)** | 92.3% (24/26) | 93.3% (28/30) | **80.77% (63/78)** |
| **Fusion A (Model C alone)** | 62.5% (5/8) | 78.6% (11/14) | **72.7% (16/22)** | 69.2% (18/26) | 70.0% (21/30) | **70.51% (55/78)** |
| **Fusion B (Model C + Cand G)**| 75.0% (6/8) | 92.9% (13/14) | **86.4% (19/22)** | 84.6% (22/26) | 86.7% (26/30) | **85.90% (67/78)** |
| **Fusion D (Logistic Fusion)** | 62.5% (5/8) | 78.6% (11/14) | **72.7% (16/22)** | 69.2% (18/26) | 70.0% (21/30) | **70.51% (55/78)** |
| **Fusion E (Asymmetric Fusion)**| **75.0% (6/8)** | **92.9% (13/14)** | **86.4% (19/22)** | **84.6% (22/26)** | **86.7% (26/30)** | **85.90% (67/78)** |

---

## 5. Key Empirical Observations and Architectural Insights

1. **Pre-Screening Zero-Bottleneck Validation:**
   - The Stage 1 Acoustic Pre-Screener achieved **100.0% retention across all short screams** (22/22) and all 78 screams overall. It successfully eliminated inaudible room tone and rumble without rejecting a single valid scream burst.
2. **Global Max-Pooling Protects Burst Energy:**
   - In Model C, `GlobalMaxPooling1D` ensures that an intense 250 ms burst produces maximum activation in the temporal filters. The burst activation is not attenuated by surrounding silence.
3. **Inhibited Cadence Vetoing Prevents Short-Scream Suppression:**
   - In standard linear fusion (Fusion D), the absence of slow-pathway cadence causes the logistic regression classifier to assign lower probabilities to short events, capping short-scream recall at 72.7%.
   - In Fusion E, when event duration is $< 800\text{ ms}$, slow-pathway cadence suppression is **strictly inhibited**, elevating short-scream recall to 86.4%.
4. **The Monosyllabic Shout Tradeoff:**
   - The short-event protection logic correctly protects short screams ($86.4\%$), but because monosyllabic shouts ("NO!", "HEY!") share identical single-burst envelopes, monosyllabic shouting false-positive rate is 75.0% (3/4).
   - In contrast, multi-syllabic speech shouting ($> 1.5\text{ s}$) is rejected with exceptional efficacy (false-positive rate of only **7.14%**).

---

## 6. Short-Event Protection Principles for Future Stages

1. **Decoupled Detection and Verification Timelines:**
   - Real-time architectures must maintain a **Fast Trigger Pipeline** ($250\text{ ms}$ buffer, $300\text{ ms}$ receptive field) that emits initial candidate alarms immediately upon detecting explosive onset transients.
2. **Missing Evidence is Unknown, Not Negative:**
   - When processing short audio buffers, the absence of syllabic cadence or closure gaps must be encoded as `CONTEXT_UNKNOWN`. It must never be converted into negative evidence of a non-scream.
3. **Max-Pooling Over Fixed Time Windows:**
   - Temporal pooling across fixed-duration neural feature maps must always employ max-pooling or attention pooling rather than average pooling.
4. **Resonance-Guided Disambiguation:**
   - On events under $800\text{ ms}$ where temporal envelope metrics are invariant, discrimination must rely exclusively on vocal-tract horn resonance ($1.5\text{–}3.5\text{ kHz}$ peak prominence) and spectral tilt.
