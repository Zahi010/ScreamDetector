# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# CANDIDATE 65-F FORMAL FREEZE REPORT
**Cryptographic Checkpoint Locking, Hyperparameter Serialization, and Freeze Manifest**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety use, emergency alerting, autonomous dispatch, police response, active-shooter notification, or critical security deployment.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Frozen Checkpoint Specification

- **Candidate Name:** `Candidate_65_F_Combined_Selective`
- **Checkpoint Path:** `models/candidate_65f_frozen.pt`
- **Cryptographic SHA-256:** `06a98025dbdabf462bec305b0cfe8455dd137b3d515cafca8811606865bacfab`
- **Metadata File:** `models/candidate_freeze_metadata.json`
- **Freeze Timestamp:** `2026-11-12T08:05:15Z`

---

## 3. Parameter and Architectural Freeze

1. **Encoder Topologies:**
   - Short Branch: Linear(17, 32) -> BatchNorm1d -> ReLU -> Dropout(0.10) -> Linear(32, 16) -> ReLU
   - Sustained Branch: Linear(17, 32) -> BatchNorm1d -> ReLU -> Dropout(0.10) -> Linear(32, 16) -> ReLU
2. **Blending Mechanism:**
   - Gate Network: Linear(32, 16) -> ReLU -> Linear(16, 1) -> Sigmoid()
   - Fusion: $z_{\text{fused}} = \gamma z_s + (1 - \gamma) z_l$
   - Head: Linear(16, 1)
3. **Post-Processing Suppression Constants:**
   - Calibrated Operating Threshold: $\tau = 0.48$
   - High-Confidence Protection Threshold: $p_{\text{protect}} = 0.80$
   - Latent Cosine Agreement Threshold: $\text{sim}_{\text{thresh}} = 0.40$
   - Narrow-Band Whistle Veto: $\text{HNR} > 12.0\text{ dB}$ AND $\text{Flatness} < 0.001$
   - Attenuation Multiplier: $0.15$

---

## 4. Integrity and Immutability Guarantee
The checkpoint and metadata are permanently locked. No downstream retuning, fine-tuning, or parameter adjustment is permitted without incrementing the research stage and invalidating preregistration.
