import os
import sys
import time
import json
import csv
import platform
import psutil
from pathlib import Path
import numpy as np
import torch

BACKEND_DIR = Path(r"C:\Users\zahia\OneDrive\Desktop\ScreamDetector\festival-scream-detector\backend")
sys.path.insert(0, str(BACKEND_DIR))

STAGE_DIR = BACKEND_DIR / "research" / "stage_8_9_39"
sys.path.insert(0, str(STAGE_DIR))

CKPT_DIR_B = STAGE_DIR / "checkpoints" / "config_b"
CKPT_DIR_D = STAGE_DIR / "checkpoints" / "config_d"
RESULTS_DIR = STAGE_DIR / "results" / "latency"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

from scripts.train_config_b import DualEncoderAcousticModel
from scripts.train_config_d import MultiPathwayFusionModel
import scipy.signal as signal

BANDS = [
    ("Band1_300_800Hz", 300, 800),
    ("Band2_800_1500Hz", 800, 1500),
    ("Band3_1500_2000Hz", 1500, 2000),
    ("Band4_2000_3000Hz", 2000, 3000),
    ("Band5_3000_4000Hz", 3000, 4000),
    ("Band6_4000_6000Hz", 4000, 6000)
]

def extract_subband_vector(audio, sr=16000):
    nyq = sr / 2.0
    total_energy = np.sum(audio ** 2) + 1e-9
    band_energies = []
    temp_vars = []
    for b_name, f_low, f_high in BANDS:
        low_norm = f_low / nyq
        high_norm = min(0.999, f_high / nyq)
        b, a = signal.butter(4, [low_norm, high_norm], btype='band')
        filtered = signal.filtfilt(b, a, audio)
        band_energy = float(np.sum(filtered ** 2))
        band_energies.append(band_energy)
        hop = int(0.010 * sr)
        frame = int(0.025 * sr)
        n_frames = max(1, (len(filtered) - frame) // hop + 1)
        frame_rms = [np.sqrt(np.mean(filtered[i*hop:i*hop+frame]**2) + 1e-9) for i in range(n_frames)]
        energy_std = float(np.std(frame_rms))
        energy_mean = float(np.mean(frame_rms))
        temp_var = energy_std / (energy_mean + 1e-9)
        temp_vars.append(temp_var)
    rel_energies = [be / total_energy for be in band_energies]
    low_e = band_energies[0] + band_energies[1] + 1e-9
    scream_band_e = band_energies[3] + band_energies[4] + 1e-9
    scream_band_to_vocal_ratio = float(scream_band_e / low_e)
    high_band_whistle_ratio = float(band_energies[5] / total_energy)
    vec = [
        float(rel_energies[0]), float(rel_energies[1]), float(rel_energies[2]),
        float(rel_energies[3]), float(rel_energies[4]), float(rel_energies[5]),
        float(temp_vars[0]), float(temp_vars[3]), float(temp_vars[4]),
        scream_band_to_vocal_ratio, high_band_whistle_ratio
    ]
    return np.array(vec, dtype=np.float32)

def measure_model_latency(model, sample_inputs, n_warmup=50, n_runs=1000):
    model.eval()
    
    # Warm-up
    with torch.no_grad():
        for _ in range(n_warmup):
            _ = model(*sample_inputs)

    # Timing
    durations = []
    with torch.no_grad():
        for _ in range(n_runs):
            t0 = time.perf_counter()
            _ = model(*sample_inputs)
            t1 = time.perf_counter()
            durations.append((t1 - t0) * 1000.0) # ms

    durations = np.array(durations)
    return {
        'mean_ms': round(float(np.mean(durations)), 3),
        'std_ms': round(float(np.std(durations)), 3),
        'p50_ms': round(float(np.percentile(durations, 50)), 3),
        'p90_ms': round(float(np.percentile(durations, 90)), 3),
        'p95_ms': round(float(np.percentile(durations, 95)), 3),
        'p99_ms': round(float(np.percentile(durations, 99)), 3),
        'max_ms': round(float(np.max(durations)), 3),
        'min_ms': round(float(np.min(durations)), 3),
        'raw_durations': durations.tolist()
    }

def main():
    print("=" * 80)
    print("STAGE 8.9.39: COMPREHENSIVE LATENCY & STREAMING BENCHMARK")
    print("=" * 80)

    # System configuration
    system_info = {
        'os': platform.system(),
        'os_release': platform.release(),
        'processor': platform.processor(),
        'cpu_count_logical': psutil.cpu_count(logical=True),
        'cpu_count_physical': psutil.cpu_count(logical=False),
        'pytorch_version': torch.__version__,
        'torch_threads': torch.get_num_threads(),
        'ram_gb': round(psutil.virtual_memory().total / (1024**3), 2)
    }
    print("Hardware Environment:")
    for k, v in system_info.items():
        print(f"  {k}: {v}")

    # 1. Load Candidate B
    t0_load_b = time.perf_counter()
    ckpt_b = torch.load(CKPT_DIR_B / "best_model.pt", map_location='cpu')
    model_b = DualEncoderAcousticModel(sem_dim=1024, acoustic_dim=6, proj_sem=128, proj_acoust=32)
    model_b.load_state_dict(ckpt_b['model_state_dict'])
    model_b.eval()
    load_time_b_ms = (time.perf_counter() - t0_load_b) * 1000.0

    # 2. Load Candidate D
    t0_load_d = time.perf_counter()
    ckpt_d = torch.load(CKPT_DIR_D / "best_model.pt", map_location='cpu')
    model_d = MultiPathwayFusionModel(sem_dim=1024, acoust_dim=6, subband_dim=11)
    model_d.load_state_dict(ckpt_d['model_state_dict'])
    model_d.eval()
    load_time_d_ms = (time.perf_counter() - t0_load_d) * 1000.0

    # Synthetic single window tensors (batch_size=1)
    x_sem = torch.randn(1, 1024, dtype=torch.float32)
    x_acoust = torch.randn(1, 6, dtype=torch.float32)
    mask_acoust = torch.ones(1, 6, dtype=torch.float32)
    x_subband = torch.randn(1, 11, dtype=torch.float32)

    inputs_b = (x_sem, x_acoust, mask_acoust)
    inputs_d = (x_sem, x_acoust, mask_acoust, x_subband)

    N_WARMUP = 100
    N_RUNS = 2000

    print(f"\nBenchmarking Model Forward Latency ({N_WARMUP} warmup, {N_RUNS} runs, batch=1)...")
    lat_b = measure_model_latency(model_b, inputs_b, n_warmup=N_WARMUP, n_runs=N_RUNS)
    lat_d = measure_model_latency(model_d, inputs_d, n_warmup=N_WARMUP, n_runs=N_RUNS)

    print(f"Candidate B (DualEncoder):")
    print(f"  Load Time: {load_time_b_ms:.2f} ms")
    print(f"  P50: {lat_b['p50_ms']} ms | P95: {lat_b['p95_ms']} ms | P99: {lat_b['p99_ms']} ms | Mean: {lat_b['mean_ms']} ms")
    print(f"  Gate 5 (P95 <= 25 ms): {'PASS' if lat_b['p95_ms'] <= 25.0 else 'FAIL'}")

    print(f"\nCandidate D (MultiPathwayFusion):")
    print(f"  Load Time: {load_time_d_ms:.2f} ms")
    print(f"  P50: {lat_d['p50_ms']} ms | P95: {lat_d['p95_ms']} ms | P99: {lat_d['p99_ms']} ms | Mean: {lat_d['mean_ms']} ms")
    print(f"  Gate 5 (P95 <= 25 ms): {'PASS' if lat_d['p95_ms'] <= 25.0 else 'FAIL'}")

    # 3. Benchmark Feature Extraction Latency (Subband DSP Filter)
    print("\nBenchmarking Subband Feature Extraction (Butterworth DSP filters)...")
    sample_audio_window = np.random.randn(15600).astype(np.float32) # ~975 ms at 16 kHz
    sb_times = []
    for _ in range(50): # warmup
        _ = extract_subband_vector(sample_audio_window, sr=16000)
    for _ in range(500):
        t0 = time.perf_counter()
        _ = extract_subband_vector(sample_audio_window, sr=16000)
        t1 = time.perf_counter()
        sb_times.append((t1 - t0) * 1000.0)

    sb_times = np.array(sb_times)
    subband_latency = {
        'mean_ms': round(float(np.mean(sb_times)), 3),
        'p50_ms': round(float(np.percentile(sb_times, 50)), 3),
        'p95_ms': round(float(np.percentile(sb_times, 95)), 3),
        'p99_ms': round(float(np.percentile(sb_times, 99)), 3)
    }
    print(f"Subband DSP Latency: P50={subband_latency['p50_ms']} ms | P95={subband_latency['p95_ms']} ms | Mean={subband_latency['mean_ms']} ms")

    # 4. End-to-End Window Budget & Audio Hop Deadline (100 ms)
    # 100 ms audio hop deadline: YAMNet inference (~15 ms) + Subband (~4 ms) + Classifier forward (<1 ms) = ~20 ms << 100 ms deadline!
    deadline_misses_b = sum(1 for d in lat_b['raw_durations'] if d > 25.0)
    deadline_misses_d = sum(1 for d in lat_d['raw_durations'] if d > 25.0)

    summary = {
        'hardware_environment': system_info,
        'protocol': {
            'warmup_iterations': N_WARMUP,
            'measurement_iterations': N_RUNS,
            'batch_size': 1,
            'audio_hop_deadline_ms': 100.0,
            'gate_5_p95_limit_ms': 25.0
        },
        'candidate_b': {
            'model_name': 'DualEncoderAcousticModel',
            'load_time_ms': round(load_time_b_ms, 2),
            'computational_latency': {
                'p50_ms': lat_b['p50_ms'],
                'p90_ms': lat_b['p90_ms'],
                'p95_ms': lat_b['p95_ms'],
                'p99_ms': lat_b['p99_ms'],
                'mean_ms': lat_b['mean_ms'],
                'min_ms': lat_b['min_ms'],
                'max_ms': lat_b['max_ms']
            },
            'gate_5_status': 'PASS' if lat_b['p95_ms'] <= 25.0 else 'FAIL',
            'deadline_misses_over_25ms': deadline_misses_b
        },
        'candidate_d': {
            'model_name': 'MultiPathwayFusionModel',
            'load_time_ms': round(load_time_d_ms, 2),
            'computational_latency': {
                'p50_ms': lat_d['p50_ms'],
                'p90_ms': lat_d['p90_ms'],
                'p95_ms': lat_d['p95_ms'],
                'p99_ms': lat_d['p99_ms'],
                'mean_ms': lat_d['mean_ms'],
                'min_ms': lat_d['min_ms'],
                'max_ms': lat_d['max_ms']
            },
            'gate_5_status': 'PASS' if lat_d['p95_ms'] <= 25.0 else 'FAIL',
            'deadline_misses_over_25ms': deadline_misses_d
        },
        'auxiliary_dsp_latency': {
            'subband_feature_extraction': subband_latency
        }
    }

    out_json = RESULTS_DIR / "latency_benchmark_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nLatency benchmark results saved to: {out_json}")

    # Save distribution CSV for plotting
    csv_path = RESULTS_DIR / "latency_distributions.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(['run_index', 'candidate_b_ms', 'candidate_d_ms'])
        for i in range(N_RUNS):
            w.writerow([i + 1, lat_b['raw_durations'][i], lat_d['raw_durations'][i]])
    print(f"Latency distribution CSV saved to: {csv_path}")

if __name__ == "__main__":
    main()
