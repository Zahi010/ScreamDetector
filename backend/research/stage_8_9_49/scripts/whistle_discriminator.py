"""
Stage 8.9.49: Whistle Discrimination & Acoustic Modulation Analysis Module
Implements four research-grade, isolated intervention filters:
- Intervention A: Acoustic Modulation Analysis (20-30 Hz mechanical pea-trill detection)
- Intervention B: Narrowband Persistence Analysis (spectral concentration in 2.5-3.8 kHz)
- Intervention C: Temporal Consistency Analysis (frame-to-frame stationarity)
- Intervention D: Lightweight Research Rejection Layer (combined multi-modal gating with vocal formant protection)

CRITICAL GOVERNANCE REQUIREMENTS:
- Does NOT modify Candidate B weights.
- Does NOT modify production inference.
- Explicitly logs `rejected_by_research_filter` audit tags.
- Preserves raw Candidate B probabilities and predictions for complete auditing.
"""
import numpy as np
import scipy.signal as signal

def extract_envelope_modulation(y, sr=16000):
    """
    Extracts temporal amplitude envelope via Hilbert transform and assesses
    periodicity and energy concentration in the 18-32 Hz mechanical trill band.
    """
    if len(y) < int(0.05 * sr):
        return {
            "trill_f_hz": 0.0,
            "trill_power_ratio": 0.0,
            "trill_periodicity": 0.0
        }
        
    analytic = signal.hilbert(y)
    env = np.abs(analytic)
    env_dc = env - np.mean(env)
    
    n_env = len(env_dc)
    env_fft = np.abs(np.fft.rfft(env_dc))
    env_freqs = np.fft.rfftfreq(n_env, d=1.0/sr)
    
    total_env_power = np.sum(env_fft**2) + 1e-12
    
    # 18-32 Hz trill band
    trill_mask = (env_freqs >= 18.0) & (env_freqs <= 32.0)
    if np.any(trill_mask):
        trill_power = np.sum(env_fft[trill_mask]**2)
        trill_power_ratio = float(trill_power / total_env_power)
        
        peak_idx = np.argmax(env_fft[trill_mask])
        trill_f = float(env_freqs[trill_mask][peak_idx])
    else:
        trill_power_ratio = 0.0
        trill_f = 0.0
        
    # Autocorrelation of envelope for periodicity check via FFT
    corr = signal.correlate(env_dc, env_dc, mode='full', method='fft')[n_env - 1:]
    corr = corr / (corr[0] + 1e-12)
    
    lag_min = int(sr / 32.0) # ~31.25 ms
    lag_max = int(sr / 18.0) # ~55.5 ms
    if lag_max < len(corr) and lag_min < lag_max:
        peak_corr = float(np.max(corr[lag_min:lag_max]))
    else:
        peak_corr = 0.0
        
    return {
        "trill_f_hz": trill_f,
        "trill_power_ratio": trill_power_ratio,
        "trill_periodicity": max(0.0, peak_corr)
    }

def extract_spectral_concentration(y, sr=16000):
    """
    Extracts spectral concentration, bandwidth, and vocal-band energy ratio.
    """
    n_samples = len(y)
    if n_samples == 0:
        return {"bandwidth": 0.0, "whistle_band_ratio": 0.0, "vocal_band_ratio": 0.0, "flatness": 0.0}
        
    fft_vals = np.abs(np.fft.rfft(y))
    freqs = np.fft.rfftfreq(n_samples, d=1.0/sr)
    power = fft_vals**2
    sum_power = np.sum(power) + 1e-12
    
    centroid = float(np.sum(freqs * power) / sum_power)
    bandwidth = float(np.sqrt(np.sum(((freqs - centroid)**2) * power) / sum_power))
    
    # Energy in whistle band (2500 - 3800 Hz)
    w_mask = (freqs >= 2500.0) & (freqs <= 3800.0)
    whistle_band_ratio = float(np.sum(power[w_mask]) / sum_power)
    
    # Energy in vocal formant band (300 - 1800 Hz)
    v_mask = (freqs >= 300.0) & (freqs <= 1800.0)
    vocal_band_ratio = float(np.sum(power[v_mask]) / sum_power)
    
    # Flatness
    pos_power = power[power > 1e-12]
    if len(pos_power) > 0:
        flatness = float(np.exp(np.mean(np.log(pos_power))) / (np.mean(pos_power) + 1e-12))
    else:
        flatness = 0.0
        
    return {
        "centroid": centroid,
        "bandwidth": bandwidth,
        "whistle_band_ratio": whistle_band_ratio,
        "vocal_band_ratio": vocal_band_ratio,
        "flatness": flatness
    }

def extract_temporal_stationarity(y, sr=16000):
    """
    Computes frame-to-frame centroid relative standard deviation.
    """
    frame_len = int(0.040 * sr) # 40 ms
    hop_len = int(0.020 * sr)   # 20 ms
    
    if len(y) < frame_len * 2:
        return {"centroid_rel_std": 0.15}
        
    n_frames = (len(y) - frame_len) // hop_len + 1
    centroids = []
    freqs = np.fft.rfftfreq(frame_len, d=1.0/sr)
    
    for i in range(n_frames):
        frame = y[i*hop_len : i*hop_len + frame_len]
        fft_f = np.abs(np.fft.rfft(frame))
        p = fft_f**2
        sp = np.sum(p)
        if sp > 1e-8:
            c = np.sum(freqs * p) / sp
            centroids.append(c)
            
    if len(centroids) < 2:
        return {"centroid_rel_std": 0.15}
        
    mean_c = np.mean(centroids)
    std_c = np.std(centroids)
    rel_std = float(std_c / (mean_c + 1e-12))
    return {"centroid_rel_std": rel_std}

# -----------------------------------------------------------------------------
# INTERVENTION A: ACOUSTIC MODULATION ANALYSIS
# -----------------------------------------------------------------------------
def apply_intervention_a(y, raw_prob, raw_pred, sr=16000):
    if raw_pred == 0:
        return 0, "accepted", {"filter": "none"}
        
    mod = extract_envelope_modulation(y, sr=sr)
    # Rejection condition: strong periodic trill in 18-32 Hz
    is_trill = (mod["trill_power_ratio"] > 0.075) and (mod["trill_periodicity"] > 0.35)
    
    if is_trill:
        return 0, "rejected_by_research_filter", {"filter": "intervention_a_modulation", "diag": mod}
    else:
        return 1, "accepted", {"filter": "intervention_a_modulation", "diag": mod}

# -----------------------------------------------------------------------------
# INTERVENTION B: NARROWBAND PERSISTENCE ANALYSIS
# -----------------------------------------------------------------------------
def apply_intervention_b(y, raw_prob, raw_pred, sr=16000):
    if raw_pred == 0:
        return 0, "accepted", {"filter": "none"}
        
    spec = extract_spectral_concentration(y, sr=sr)
    # Rejection condition: narrow bandwidth (<750 Hz) and >70% energy in 2.5-3.8 kHz
    is_narrowband = (spec["bandwidth"] < 750.0) and (spec["whistle_band_ratio"] > 0.70)
    
    if is_narrowband:
        return 0, "rejected_by_research_filter", {"filter": "intervention_b_narrowband", "diag": spec}
    else:
        return 1, "accepted", {"filter": "intervention_b_narrowband", "diag": spec}

# -----------------------------------------------------------------------------
# INTERVENTION C: TEMPORAL CONSISTENCY ANALYSIS
# -----------------------------------------------------------------------------
def apply_intervention_c(y, raw_prob, raw_pred, sr=16000):
    if raw_pred == 0:
        return 0, "accepted", {"filter": "none"}
        
    stat = extract_temporal_stationarity(y, sr=sr)
    # Rejection condition: exceptionally rigid pitch / centroid stationarity
    is_stationary = (stat["centroid_rel_std"] < 0.045) and (len(y) / sr > 0.30)
    
    if is_stationary:
        return 0, "rejected_by_research_filter", {"filter": "intervention_c_temporal", "diag": stat}
    else:
        return 1, "accepted", {"filter": "intervention_c_temporal", "diag": stat}

# -----------------------------------------------------------------------------
# INTERVENTION D: LIGHTWEIGHT RESEARCH REJECTION LAYER (COMBINED GATING)
# -----------------------------------------------------------------------------
def apply_intervention_d(y, raw_prob, raw_pred, sr=16000):
    """
    Combined research rejection layer:
    Conjunction of mechanical trill modulation AND narrowband high-frequency energy,
    WITH EXPLICIT VOCAL FORMANT PRESERVATION (protecting screams with energy < 1800 Hz).
    """
    if raw_pred == 0:
        return 0, "accepted", {"filter": "none"}
        
    mod = extract_envelope_modulation(y, sr=sr)
    spec = extract_spectral_concentration(y, sr=sr)
    
    # Vocal formant protection gate:
    # Authentic human screams maintain substantial vocal resonance below 1800 Hz (F1/F2 formants).
    # If >18% of energy is in 300-1800 Hz, it is protected as an authentic vocalization!
    if spec["vocal_band_ratio"] > 0.18:
        return 1, "accepted", {"filter": "protected_by_vocal_formant_gate", "vocal_ratio": spec["vocal_band_ratio"]}
        
    # Whistle rejection conjunction:
    has_whistle_spectrum = (spec["whistle_band_ratio"] > 0.60) and (spec["bandwidth"] < 800.0)
    has_mechanical_trill = (mod["trill_power_ratio"] > 0.065) or (mod["trill_periodicity"] > 0.30)
    
    if has_whistle_spectrum and has_mechanical_trill:
        return 0, "rejected_by_research_filter", {
            "filter": "intervention_d_combined",
            "mod": mod,
            "spec": spec
        }
    else:
        return 1, "accepted", {
            "filter": "intervention_d_combined",
            "mod": mod,
            "spec": spec
        }
