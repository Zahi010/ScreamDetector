# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# Hierarchical Vocalization-Discrimination Architecture Design

**Stage Identifier:** Stage 8.9.73  
**Classification:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE  
**Conceptual Structure:**
`Input Audio -> Multi-Resolution Acoustic Encoder -> Vocalization Discrimination (Stage B) -> Conditional Scream Refiner (Stage C)`

---

## 1. Architectural Stages

### Stage A — Multi-Resolution Acoustic Encoder
- Dual-resolution short (250 ms) and sustained (1,000 ms) C5 acoustic streams (17 dims each) combined with normalized vocal non-linearities (5 dims: roughness, HF ratio, flux, HNR, flatness).
- Latent representations: $z_s \in \mathbb{R}^{16}$, $z_l \in \mathbb{R}^{16}$.
- Gated fusion: $z_{fused} = g \cdot z_s + (1 - g) \cdot z_l$.

### Stage B — Vocalization Discrimination Head
- Classifies audio into 3 discrete acoustic regimes:
  1. `Class 0: Non-Vocal / Environmental` (Sirens, whistles, ambient crowd noise)
  2. `Class 1: Vocal Non-Scream` (Shouted speech, infant crying, crowd cheering)
  3. `Class 2: Scream-Like Vocalization` (Genuine screams, distress vocalizations)
- Loss: Categorical Cross-Entropy with class balancing.

### Stage C — Conditional Scream Assessment Refiner
- Inputs: Concatenation $[z_{fused}, P(vocal\_class)] \in \mathbb{R}^{19}$.
- Outputs: Continuous calibrated scream score $\hat{y} \in [0, 1]$.
- Objective: Restricts scream triggering unless Stage B assigns high confidence to Class 2.

---

## 2. Theoretical Hypothesis vs Empirical Outcome

- **Hypothesis:** By decoupling vocal detection from scream detection, the hierarchical model will filter shouted speech and whistles prior to binary classification, eliminating the need for rigid heuristic vetoes.
- **Empirical Reality:** High-intensity shouted speech and infant crying share identical vocal tract physics, high fundamental frequency ($F_0$), and broad subband energy distributions with screams. Without auditory roughness in the 30–150 Hz band, Stage B incorrectly routes shouted speech into the scream refiner, resulting in an unacceptable shouted-speech FPR of **27.27% to 47.73%** (failing Gate 3).
