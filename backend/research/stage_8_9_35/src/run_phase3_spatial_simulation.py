import os
import csv
import json
import numpy as np
import soundfile as sf
import scipy.signal as signal

# Simulation Parameters (SYNTHETIC SIMULATION ONLY)
C_SOUND = 343.0 # Speed of sound (m/s)
MIC_SPACING = 0.05 # 50mm array spacing
SR = 16000 # Sample rate

def fractional_delay(x, delay_samples):
    """Apply fractional delay using sinc interpolation or phase shifting."""
    N = len(x)
    freqs = np.fft.rfftfreq(N, 1.0 / SR)
    X = np.fft.rfft(x)
    phase_shift = np.exp(-2j * np.pi * freqs * (delay_samples / SR))
    y = np.fft.irfft(X * phase_shift, n=N)
    return y

def gcc_phat(sig1, sig2, max_tau=None):
    """Generalized Cross-Correlation Phase Transform (GCC-PHAT)."""
    N = len(sig1) + len(sig2)
    X1 = np.fft.rfft(sig1, n=N)
    X2 = np.fft.rfft(sig2, n=N)
    R = X1 * np.conj(X2)
    R_norm = R / (np.abs(R) + 1e-9)
    cc = np.fft.irfft(R_norm, n=N)
    max_shift = int(max_tau * SR) if max_tau else len(cc) // 2
    cc = np.concatenate((cc[-max_shift:], cc[:max_shift+1]))
    shift = np.argmax(np.abs(cc)) - max_shift
    tau = shift / SR
    return tau, cc

def delay_and_sum_beamform(ch1, ch2, steer_tau):
    """Delay-and-sum beamformer steered to time delay steer_tau."""
    steered_ch2 = fractional_delay(ch2, steer_tau * SR)
    out = 0.5 * (ch1 + steered_ch2)
    return out

def run_spatial_simulation():
    print("=" * 70)
    print("STAGE 8.9.35 - PHASE 3: SPATIAL AUDIO SIMULATION (TRACK B)")
    print("=" * 70)
    print("DESIGNATION: CONTROLLED SYNTHETIC SIMULATION ONLY")
    print("NOTE: Production edge hardware has 1 mono mic; this simulates future dual-mic array.\n")
    
    # Load manifest to select clean sources
    manifest_path = 'backend/experiments/v2_hard_negative_training/manifests/dataset_manifest_v3.csv'
    with open(manifest_path, encoding='utf-8') as f:
        records = list(csv.DictReader(f))
        
    scream_files = [r for r in records if r['binary_label'] == 'scream' and os.path.exists(r['workspace_audio_path'])]
    shout_files = [r for r in records if r['target_category'] == 'shouting_and_speech' and os.path.exists(r['workspace_audio_path'])]
    crowd_files = [r for r in records if r['target_category'] == 'crowd_chant_cheering' and os.path.exists(r['workspace_audio_path'])]
    
    print(f"Pool for spatial mixing: {len(scream_files)} screams, {len(shout_files)} shouts, {len(crowd_files)} crowds")
    
    test_angles = [0, 30, 45, 60, 90, 120, 135, 150, 180]
    snr_levels_db = [10.0, 5.0, 0.0, -3.0, -5.0]
    
    simulation_results = []
    
    rng = np.random.RandomState(42)
    n_trials = 20
    
    for snr_db in snr_levels_db:
        sinr_improvements = []
        doa_errors_deg = []
        detection_gains = []
        
        for trial in range(n_trials):
            # Target scream
            s_rec = scream_files[trial % len(scream_files)]
            s_audio, sr = sf.read(s_rec['workspace_audio_path'])
            if s_audio.ndim > 1: s_audio = np.mean(s_audio, axis=1)
            target_len = int(1.0 * sr) # 1-second segment
            if len(s_audio) < target_len:
                s_audio = np.pad(s_audio, (0, target_len - len(s_audio)))
            else:
                s_audio = s_audio[:target_len]
                
            # Interefering crowd/shout
            c_rec = crowd_files[trial % len(crowd_files)]
            c_audio, _ = sf.read(c_rec['workspace_audio_path'])
            if c_audio.ndim > 1: c_audio = np.mean(c_audio, axis=1)
            if len(c_audio) < target_len:
                c_audio = np.pad(c_audio, (0, target_len - len(c_audio)))
            else:
                c_audio = c_audio[:target_len]
                
            # Scale interference for desired SNR
            p_signal = np.mean(s_audio**2) + 1e-9
            p_noise = np.mean(c_audio**2) + 1e-9
            target_noise_p = p_signal / (10.0 ** (snr_db / 10.0))
            scale = np.sqrt(target_noise_p / p_noise)
            interference = c_audio * scale
            
            # Geometry: target at theta_t = 45 deg, interference at theta_i = 135 deg
            theta_target_deg = 45.0
            theta_interf_deg = 135.0
            
            tau_target = (MIC_SPACING * np.cos(np.radians(theta_target_deg))) / C_SOUND
            tau_interf = (MIC_SPACING * np.cos(np.radians(theta_interf_deg))) / C_SOUND
            
            # Channel 1: mic 1
            ch1 = s_audio + interference
            # Channel 2: mic 2 with delay + thermal noise
            s_delayed = fractional_delay(s_audio, tau_target * sr)
            i_delayed = fractional_delay(interference, tau_interf * sr)
            thermal_noise = rng.randn(target_len) * 0.005
            ch2 = s_delayed + i_delayed + thermal_noise
            
            # Baseline single-channel SINR
            sinr_in = 10.0 * np.log10(np.mean(s_audio**2) / (np.mean(interference**2) + 1e-9))
            
            # GCC-PHAT DOA estimation
            max_tau = MIC_SPACING / C_SOUND
            est_tau, _ = gcc_phat(ch1, ch2, max_tau=max_tau)
            cos_theta = np.clip(est_tau * C_SOUND / MIC_SPACING, -1.0, 1.0)
            est_angle_deg = np.degrees(np.arccos(cos_theta))
            doa_err = abs(est_angle_deg - theta_target_deg)
            doa_errors_deg.append(doa_err)
            
            # Beamforming
            beamformed = delay_and_sum_beamform(ch1, ch2, -est_tau)
            
            # Measure output SINR (signal component vs noise component after beamforming)
            bf_sig = 0.5 * (s_audio + fractional_delay(s_delayed, -est_tau * sr))
            bf_noise = 0.5 * (interference + fractional_delay(i_delayed, -est_tau * sr)) + 0.5 * thermal_noise
            sinr_out = 10.0 * np.log10(np.mean(bf_sig**2) / (np.mean(bf_noise**2) + 1e-9))
            
            sinr_improvements.append(sinr_out - sinr_in)
            
        mean_gain = float(np.mean(sinr_improvements))
        mean_err = float(np.mean(doa_errors_deg))
        
        simulation_results.append({
            'input_snr_db': snr_db,
            'array_elements': 2,
            'array_spacing_m': MIC_SPACING,
            'mean_beamforming_gain_db': round(mean_gain, 2),
            'mean_doa_error_deg': round(mean_err, 2),
            'target_angle_deg': 45.0,
            'interference_angle_deg': 135.0,
            'synthetic_label': 'SYNTHETIC_SIMULATION_ONLY'
        })
        print(f"Condition: SNR={snr_db:5.1f} dB | Array Gain: +{mean_gain:4.2f} dB | Mean DOA Error: {mean_err:4.1f} deg [SYNTHETIC]")
        
    out_csv = 'backend/research/stage_8_9_35/spatial_analysis/spatial_experiment_results.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(simulation_results[0].keys()))
        w.writeheader()
        w.writerows(simulation_results)
    print(f"\nSaved {out_csv}")

if __name__ == '__main__':
    run_spatial_simulation()
