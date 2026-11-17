# Event Boundary Annotation and Evaluation Protocol

**Document Version:** 1.0  
**Date:** October 29, 2026  
**Applicability:** Festival Scream Detector — Temporal State Machine and Event-Boundary Evaluation

---

## 1. Motivation & Problem Definition

In Stage 8.9.11 and 8.9.12, acoustic evaluation revealed a sharp divergence between **window-level metrics** and **event-level operational metrics**:
1. **Window-Level Pooling (Stage 8.9.11):** Audio files were pooled into a single feature vector, yielding isolated single-frame false-positive rates (~5%–7%).
2. **Streaming Window Sequences (Stage 8.9.12):** When evaluated in streaming 1.0-second rolling windows with a 500 ms hop interval, adjacent windows are acoustically correlated. A 4-second crowd cheering clip yields 7 overlapping windows; if window 2 triggers, windows 3 and 4 frequently trigger as well. Under naive file-level counting, event-level false positive rates escalated to 25%–40%.
3. **Short-Event Suppression:** Preregistered temporal persistence policies ($C=2, C=3$) eliminated repeated false alarms, but completely blinded the detector to brief screams shorter than 1.0 second (0.0% recall on short events).

To prevent methodological ambiguity and ensure safety-critical evaluation, this document codifies the authoritative mathematical definitions for ground-truth events, prediction event boundaries, temporal collar matching, duplicate alert assignment, and operational exposure modeling.

---

## 2. Ground-Truth Event Definitions

An acoustic ground-truth event $E_i$ is defined as a tuple:
$$E_i = \left( t_{\text{start}}^{(i)}, t_{\text{end}}^{(i)}, c_i, d_i \right)$$
where:
- $t_{\text{start}}^{(i)}$: The exact onset timestamp of the acoustic sound in seconds (first audible vocalization or sound source).
- $t_{\text{end}}^{(i)}$: The exact offset timestamp in seconds (sound decays to ambient noise floor).
- $c_i$: Class category ($c_i \in \{\text{scream}, \text{masked\_scream}, \text{shouting}, \text{crowd\_chant}, \text{infant\_crying}, \text{whistle}, \text{siren}, \text{environmental}\}$).
- $d_i = t_{\text{end}}^{(i)} - t_{\text{start}}^{(i)}$: Event duration in seconds.

### Event Duration Classes:
1. **Brief / Startle Shrieks:** Duration $d_i < 1.0\text{ s}$ (typically 300 ms to 800 ms).
2. **Sustained Screams:** Duration $d_i \ge 1.0\text{ s}$ (typically 1.2s to 4.5s).
3. **Continuous Background Sound:** Duration $d_i \ge 3.0\text{ s}$ (crowd cheering, music, industrial noise).

### Minimum Inter-Event Separation:
Two acoustic events $E_1$ and $E_2$ of the same category are distinct if:
$$t_{\text{start}}^{(2)} - t_{\text{end}}^{(1)} \ge \Delta t_{\text{sep}} = 1.0\text{ s} \quad (2 \text{ hops})$$
If two sound bursts occur with less than 1.0s separation, they are treated as sub-bursts of a single continuous compound event.

---

## 3. Predicted Alert Event Definitions

A temporal alert policy processes rolling audio windows $W_k = [k \cdot H, k \cdot H + W_{\text{dur}}]$ where:
- $W_{\text{dur}} = 1.0\text{ s}$ (window duration)
- $H = 0.5\text{ s}$ (hop interval)
- $p_k \in [0.0, 1.0]$: Acoustic model posterior probability for window $k$.

When the temporal state machine triggers, it emits a **Predicted Alert Event** $\hat{E}_j$:
$$\hat{E}_j = \left( \hat{t}_{\text{onset}}^{(j)}, \hat{t}_{\text{offset}}^{(j)}, \hat{p}_{\text{peak}}^{(j)} \right)$$
where:
- $\hat{t}_{\text{onset}}^{(j)}$: The timestamp (endpoint of window $k$) where the alert was officially dispatched.
- $\hat{t}_{\text{offset}}^{(j)}$: The timestamp where the state machine returns to `IDLE` state after acoustic release and recovery.
- $\hat{p}_{\text{peak}}^{(j)} = \max_{k \in \hat{E}_j} p_k$: Peak model confidence during the alert event.

---

## 4. Matching Criterion & Temporal Collar Matching

To determine whether an alert $\hat{E}_j$ correctly detected a ground-truth scream event $E_i$, a temporal collar tolerance $\Delta t_{\text{collar}} = 0.5\text{ s}$ (1 hop) is applied.

$$\text{Valid Match Condition:} \quad \hat{t}_{\text{onset}}^{(j)} \in \left[ t_{\text{start}}^{(i)}, t_{\text{end}}^{(i)} + \Delta t_{\text{collar}} \right]$$

```
Ground Truth Scream E_i:    |----------------- Event Duration d_i -----------------|-- collar --|
                             t_start                                               t_end        t_end + 0.5s

Predicted Alert 1 (Valid):                  * [t_onset_1] -> TRUE POSITIVE DETECTION
Predicted Alert 2 (Dupe):                               * [t_onset_2] -> DUPLICATE ALERT (Not False Alarm)

Predicted Alert 3 (Outside):                                                                   * [t_onset_3] -> FALSE ALARM EVENT
```

### Assignment Rules:
1. **Primary True Detection:** The first alert $\hat{E}_j$ satisfying the valid match condition for ground-truth event $E_i$ is recorded as a **True Positive Event (TP)**.
2. **Duplicate Alert Suppression:** Any subsequent alert $\hat{E}_{j+m}$ falling within $[t_{\text{start}}^{(i)}, t_{\text{end}}^{(i)} + \Delta t_{\text{collar}}]$ for an already detected event is counted as a **Duplicate Alert**. It does **NOT** increment True Positives, nor is it counted as a False Alarm.
3. **Missed Event (False Negative):** A ground-truth scream event $E_i$ with zero matching alerts is recorded as a **False Negative Event (FN)**.
4. **False Alert Event (False Positive):** Any alert $\hat{E}_k$ whose onset falls outside all ground-truth scream collars is recorded as a **False Positive Event (FP)**.
5. **Overlapping Multi-Window False Alarm Clustering:** If consecutive overlapping windows $[W_k, W_{k+1}, W_{k+2}]$ fire during a single negative sound burst (e.g. 3-second shouted speech), the state machine's active duration merges them into **ONE False Alert Event**, not three separate false alarms.

---

## 5. Formal Metric Definitions

### 5.1 Event-Level Scream Recall ($\text{Recall}_{\text{event}}$)
$$\text{Recall}_{\text{event}} = \frac{N_{\text{TP\_events}}}{N_{\text{True\_Positive\_Events}}} \times 100\%$$
- **Target Gate:** $\ge 96.00\%$.

### 5.2 Short-Scream Recall ($\text{Recall}_{\text{short}}$)
$$\text{Recall}_{\text{short}} = \frac{N_{\text{TP\_short\_events}}}{N_{\text{True\_Short\_Events}}} \times 100\% \quad (\text{Events with } d_i < 1.0\text{ s})$$
- **Mandate:** Any policy that drops short-scream recall below $90.0\%$ to reduce false alarms is strictly disqualified.

### 5.3 Event-Level Hard-Negative False Positive Rate ($\text{FPR}_{\text{event}}$)
$$\text{FPR}_{\text{event}} = \frac{N_{\text{FP\_events}}}{N_{\text{Negative\_Audio\_Events}}} \times 100\%$$
- **Target Gate:** $\le 5.00\%$.

### 5.4 Shouted-Speech Event FPR ($\text{FPR}_{\text{shout}}$)
$$\text{FPR}_{\text{shout}} = \frac{N_{\text{FP\_shout\_events}}}{N_{\text{Shouting\_Events}}} \times 100\%$$
- **Target Gate:** $\le 15.00\%$.

### 5.5 Detection Delay ($\Delta t_{\text{delay}}$)
$$\Delta t_{\text{delay}} = \hat{t}_{\text{onset}} - t_{\text{start}}$$
- Measures the latency in seconds between acoustic onset and alert dispatch.

### 5.6 Duplicate Alerts per Event ($R_{\text{dupe}}$)
$$R_{\text{dupe}} = \frac{N_{\text{total\_alerts\_on\_screams}} - N_{\text{TP\_events}}}{N_{\text{TP\_events}}}$$
- Measures operator alarm fatigue caused by un-cooldown alerts during continuous scream events.

### 5.7 Operational Hourly False Alert Rate ($A_{\text{hr}}$)
Under continuous streaming audio monitoring at an assumed emergency event prevalence $\pi = 10^{-4}$ (approx. 1 true incident per 1.4 hours):
$$A_{\text{hr}} = \text{FPR}_{\text{event}} \times \left( \frac{3600\text{ s/hr}}{\bar{d}_{\text{neg}} + \Delta t_{\text{quiet}}} \right)$$
where $\bar{d}_{\text{neg}} \approx 2.0\text{ s}$ is average negative sound duration. This models realistic festival exposure without treating adjacent 500 ms hops as independent random variables.
