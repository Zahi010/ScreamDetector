# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# STAGE 8.9.64 — False-Positive Suppression Architecture Ablations

**MANDATORY SAFETY DESIGNATION:**
*This system is an experimental acoustic research prototype. It is not certified for emergency detection, life-safety alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment. All experiments must use legally acquired recorded audio datasets and safe recorded-audio playback protocols only.*

---

## 1. Executive Summary

Track E evaluated six architectural configurations of the Dual-Resolution Gated Model to resolve the false-positive rate (FPR) vulnerability identified in Stage 8.9.63 without eroding short-event scream sensitivity. 

Evaluations were conducted across the 312 recordings ($N_{\text{pos}}=195, N_{\text{neg}}=117$) using 5-fold cross-validation. Metrics are cataloged in [`false_positive_suppression_metrics.csv`](file:///c:/Users/zahia/OneDrive/Desktop/ScreamDetector/festival-scream-detector/backend/research/stage_8_9_64/false_positive_suppression_metrics.csv).

---

## 2. Comparative Ablation Matrix

```
False-Positive Suppression Ablation Results (5-Fold Cross-Validation, N = 312)
┌──────────────────────────────────────┬──────────┬──────────┬──────────┬────────────┬────────────┬──────────┬──────────┬────────────┐
│ Architecture Variant                 │ Gate 1   │ Gate 2   │ F1 Score │ Gate 4     │ UltraShort │ HN FPR   │ PR-AUC   │ Gate Stat  │
│                                      │ (>=96.0%)│ (<=5.0%) │          │ (>=90.0%)  │ (<=0.50s)  │          │          │            │
├──────────────────────────────────────┼──────────┼──────────┼──────────┼────────────┼────────────┼──────────┼──────────┼────────────┤
│ V1: Baseline Dual-Resolution Gated   │ 92.31%   │ 26.50%   │ 0.8867   │ 96.24%     │ 100.00%    │ 26.50%   │ 0.8814   │ FAIL G1,G2 │
│ V2: Dual-Res + HNR Tonal Veto        │ 88.72%   │ 23.08%   │ 0.8759   │ 96.24%     │ 100.00%    │ 23.08%   │ 0.9311   │ FAIL G1,G2 │
│ V3: Dual-Res + Contrastive Hard-Neg  │ 91.79%   │ 19.66%   │ 0.9018   │ 95.49%     │  98.04%    │ 19.66%   │ 0.9327   │ FAIL G1,G2 │
│ V4: Dual-Res + Both (HNR+Contrastive)│ 89.23%   │ 23.93%   │ 0.8766   │ 96.24%     │ 100.00%    │ 23.93%   │ 0.9454   │ FAIL G1,G2 │
│ V5: Dual-Res + Temporal K=2 Filter   │ 94.36%   │ 14.53%   │ 0.9293   │ 97.74%     │  98.04%    │ 14.53%   │ 0.9378   │ FAIL G1,G2 │
│ V6: Dual-Res Full Suppression Stack  │ 87.69%   │  4.27%   │ 0.9218   │ 94.74%     │  98.04%    │  4.27%   │ 0.9631   │ PASS G2,G4 │
└──────────────────────────────────────┴──────────┴──────────┴──────────┴────────────┴────────────┴──────────┴──────────┴────────────┘
```

---

## 3. Analysis of Individual Interventions

### 3.1 Harmonic-to-Noise Ratio (HNR) Tonal Veto (Variant 2)
- **Whistle Suppression:** Evaluated on pure tones and acoustic whistles, HNR attenuation ($w = 0.20$ when $\text{HNR} > 7.0\,\text{dB}, \text{SF} < 0.008$) cut whistle false alarms from $100\%$ down to $50\%$.
- **Short-Scream Preservation:** Because human screams contain high aspiration turbulence ($\text{SF} > 0.025, \text{HNR} < 0\,\text{dB}$), Gate 4 Short-Scream Recall remained identical at **$96.24\%$** and Ultra-Short Recall was **$100.00\%$**.
- **Limitation:** Alone, HNR cannot distinguish impulsive mechanical squeaks or human shouting, as both produce turbulent or complex spectra.

### 3.2 Contrastive Hard-Negative Weighting (Variant 3)
- **Boundary Optimization:** Applying an asymmetric loss penalty ($w_i = 2.50$) to shouts, whistles, and squeaks reduced overall FPR from $26.50\%$ down to **$19.66\%$**, driving PR-AUC up to $0.9327$ and F1 score above $0.90$ ($0.9018$).
- **Whistle FPR:** Whistle false alarms dropped to **$0.00\%$**.

### 3.3 Temporal Persistence Filter ($K=2$) (Variant 5)
- **Transient Rejection:** Transient single-frame noise spikes (clapping, dropped objects, wind gusts) rarely persist across two consecutive analysis hops.
- **FPR Reduction:** Slashed false alarms from $26.50\%$ to **$14.53\%$** while improving overall recall to **$94.36\%$** and Gate 4 short recall to **$97.74\%$**.

### 3.4 Full Suppression Stack (Variant 6)
- **Gate 2 Achievement:** Combining contrastive loss weighting, HNR physical vetoes, temporal corroboration ($K=2$), and event refractory holdoff drove false positive rate down to **$4.27\%$** ($5 / 117$), successfully meeting the Gate 2 requirement ($\le 5.0\%$).
- **Gate 4 Sensitivity:** Gate 4 short-scream recall remained comfortably above the $90.0\%$ threshold at **$94.74\%$** ($126/133$), with ultra-short recall at **$98.04\%$**.
- **Trade-off:** Conservative gating and holdoff slightly dampened sustained scream sensitivity ($72.58\%$), causing overall recall ($87.69\%$) to remain below Gate 1 ($\ge 96.0\%$).

---

## 4. Governance & Promotion Decision

> [!CAUTION]
> **GOVERNANCE VETO — ZERO PRODUCTION PROMOTION.**
> Although Variant 6 achieves Gate 2 ($\text{FPR} = 4.27\% \le 5.0\%$) and Gate 4 ($\text{Short Recall} = 94.74\% \ge 90.0\%$), Gate 1 overall recall ($87.69\% < 96.0\%$) fails on the development cohort.
> 
> Production assets remain strictly frozen bit-for-bit.

