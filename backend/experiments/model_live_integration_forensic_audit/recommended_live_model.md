# Recommended Live Demonstration Model Verdict

## 1. Final Recommendation

### PRIMARY LIVE DEMONSTRATION CANDIDATE: PRODUCTION_BASELINE (Stage 5 LR)

Based on exhaustive, controlled empirical evaluation across digital silence, infant crying, loud speech, and genuine screams:

1. **Production Baseline (`PRODUCTION_BASELINE`)** is the **ONLY** trustworthy, production-ready model for the live team demonstration.
   - It reliably rejects digital silence (score: 0.0048 << threshold 0.3500).
   - It rejects infant crying (score: 0.0001 - 0.0031 << threshold 0.3500).
   - It rejects ordinary and loud speech.
   - It reliably detects genuine screams (recall: 88.99%, precision: 0.9023).
   - Its production SHA-256 hashes are 100% verified and frozen.

2. **Experimental Models Verdict**: All experimental models (`D_v4 + Family A`, `D_v4 + Family B`, `F_v6 Acoustic`, `Stage 8.9.15 Model B`) MUST be displayed in the Live Lab as **`REJECTED / UNDER INVESTIGATION`**, not promoted as primary detection models.
   - `D_v4 + Family A` triggers catastrophic false positives on silence (84.5% - 90.6%) and infant crying (45.2% > threshold 0.420).
   - Promoting `D_v4 + Family A` to executive stakeholders would cause immediate demonstration failure.
