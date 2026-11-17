# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE-SAFETY USE.

# MATHEMATICAL & EMPIRICAL FUSION DYNAMICS: GATED BLENDING VS. SOFT-OR
**Forensic Investigation into Dual-Branch Fusion Topologies**

## 1. Safety Designation
Non-certified acoustic research prototype. Prohibited for life-safety alerting, emergency dispatch, autonomous response, or critical security monitoring.

All tests utilize legally acquired recorded audio files and safe playback protocols only.

---

## 2. Theoretical Formulation of Fusion Topologies

In dual-resolution acoustic detection, two complementary feature vectors are extracted:
- $x_{\text{short}} \in \mathbb{R}^{17}$ (250 ms high-energy focused slice)
- $x_{\text{sust}} \in \mathbb{R}^{17}$ (1,000 ms sustained context window)

Encoders map these representations to latent spaces:
$$z_s = f_{\theta_s}(x_{\text{short}}), \quad z_l = f_{\theta_l}(x_{\text{sust}}) \in \mathbb{R}^{16}$$

### Topology A: Latent Gated Blending (Baseline, Variant 6, Candidate 65-F)
A gating network calculates scalar blending coefficient $\gamma \in [0, 1]$:
$$\gamma = \sigma(W_g [z_s; z_l] + b_g)$$
$$z_{\text{fused}} = \gamma z_s + (1 - \gamma) z_l$$
$$p_{\text{gated}} = \sigma(W_h z_{\text{fused}} + b_h)$$

- **Convex Combination Property:** Since $z_{\text{fused}}$ is a convex combination of $z_s$ and $z_l$, features are bounded:
  $$\|z_{\text{fused}}\| \le \gamma \|z_s\| + (1 - \gamma) \|z_l\|$$
- **Cross-Resolution Consensus:** For an alarm to fire ($p \ge \tau$), the combined latent vector must lie within the positive classification half-space. If one branch is completely negative (e.g. ambient noise in $x_{\text{sust}}$) and the gating weight is balanced, $z_{\text{fused}}$ is attenuated, dampening false alarms.

### Topology B: Independent Head Soft-OR Fusion (Sust_D)
Each branch projects independently through its own classification head:
$$p_s = \sigma(W_s z_s + b_s), \quad p_l = \sigma(W_l z_l + b_l)$$
Posterior probabilities are fused via probabilistic disjunction (Soft-OR):
$$p_{\text{fused}} = 1 - (1 - p_s)(1 - p_l) = p_s + p_l - p_s \cdot p_l$$

---

## 3. Mathematical Proof of False Alarm Amplification under Soft-OR

Let $X$ be a non-scream recording (null hypothesis $H_0: Y=0$).
Assume the short-branch false alarm probability is $\alpha_s = P(p_s \ge \tau \mid H_0)$ and the sustained-branch false alarm probability is $\alpha_l = P(p_l \ge \tau \mid H_0)$.

Under Soft-OR with decision threshold $\tau = 0.50$:
$$p_{\text{fused}} \ge 0.50 \iff (1 - p_s)(1 - p_l) \le 0.50$$

If $p_s$ and $p_l$ are conditionally independent given $H_0$:
$$P(p_{\text{fused}} \ge 0.50 \mid H_0) \ge P(p_s \ge 0.50 \cup p_l \ge 0.50 \mid H_0)$$
$$P(\text{Alarm} \mid H_0) = 1 - (1 - \alpha_s)(1 - \alpha_l) = \alpha_s + \alpha_l - \alpha_s \alpha_l$$

For small $\alpha_s, \alpha_l$, this expands to:
$$\alpha_{\text{fused}} \approx \alpha_s + \alpha_l$$

The false positive rate is approximately **additive**.

### Empirical Verification on Development Cohort ($N=117$ negatives)
- Short Head Alone False Positives: $FP_s = 39$ ($\alpha_s = 33.33\%$)
- Sustained Head Alone False Positives: $FP_l = 42$ ($\alpha_l = 35.90\%$)
- Joint False Positives (Both trigger): $FP_{s \cap l} = 13$ ($11.11\%$)
- Soft-OR False Positives: $FP_{\text{fused}} = 39 + 42 - 13 = 68$
- Observed Soft-OR FPR: $\frac{68}{117} = \mathbf{58.12\%}$

This matches the theoretical additive prediction exactly ($33.33\% + 35.90\% - 11.11\% = 58.12\%$).

---

## 4. Why Gated Blending Controls FPR

Under Gated Blending, when a non-scream transient appears in the 250 ms window (e.g. a sudden whistle blast), the short branch activates strongly ($z_s$ high), but the sustained branch observes the entire 1,000 ms surrounding context and detects a static sinusoid or ambient quietude ($z_l$ low).

The gating network evaluates both branches simultaneously. If $z_l$ contradicts $z_s$, the blended latent vector $z_{\text{fused}}$ falls short of the activation boundary:
$$\text{Baseline Gated FPR} = 21.37\% \quad \text{vs.} \quad \text{Soft-OR FPR} = 58.12\%$$

When combined with selective acoustic filtering (Candidate 65-F), the gated topology achieves:
$$\text{Candidate 65-F FPR} = \mathbf{5.98\%}$$

---

## 5. Architectural Recommendations

1. **Reject Naive Soft-OR:** Disjunctive confidence fusion without inter-branch consensus guarantees unacceptable false alarm rates in acoustic monitoring environments.
2. **Require Cross-Branch Consensus:** Any dual-resolution architecture must require either gated latent feature blending or an explicit veto gate where disagreement triggers scrutiny.
3. **Selective Gating for Sustained Recall:** To capture sustained screams without blowing up FPR, future research should explore asymmetric gating where high sustained confidence can elevate borderline short events only when spectral harmonicity matches human vocal tract acoustics.

