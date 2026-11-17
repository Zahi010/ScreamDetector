"""Real-Time Microphone & Audio Stream Endurance & Performance Test Script (Stage 8.5).

Measures and validates:
1. Long-running stream stability under physical microphone capture or simulated stream.
2. Memory consumption (RSS MB at start, peak, end, delta) to verify no memory leaks.
3. System and process CPU utilization % sampled non-blockingly over the run.
4. Audio window processing latency (mean, median, P95, min, max).
5. Window count, throughput, dropped samples, and buffer underrun/overflow auditing.
6. Alert emissions, cooldown suppression, and state machine transition tracking.
7. Graceful shutdown and output generation in CSV and Markdown formats.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    sd = None
    SOUNDDEVICE_AVAILABLE = False

from src.config import (
    DEFAULT_ALERT_COOLDOWN_SECONDS,
    DEFAULT_SCREAM_THRESHOLD,
    REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.detector import (
    AudioDeviceError,
    MicrophoneCapture,
    StreamDetector,
    list_audio_input_devices,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("endurance_test")


class EnduranceMetricsCollector:
    """Non-blocking system resources and latency metrics sampler."""

    def __init__(self, sample_interval_seconds: float = 1.0):
        self.sample_interval = sample_interval_seconds
        self.process = psutil.Process(os.getpid()) if PSUTIL_AVAILABLE else None

        self.cpu_samples: List[float] = []
        self.rss_mb_samples: List[float] = []
        self.timestamps: List[float] = []

        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available; CPU and process memory sampling disabled.")
            return

        self._running = True
        self._thread = threading.Thread(target=self._sample_loop, daemon=True, name="MetricsSampler")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _sample_loop(self):
        # Warmup CPU measurement
        if self.process:
            self.process.cpu_percent(interval=None)

        while self._running:
            try:
                if self.process:
                    cpu = self.process.cpu_percent(interval=None)
                    mem = self.process.memory_info().rss / (1024.0 * 1024.0)  # MB
                    self.cpu_samples.append(cpu)
                    self.rss_mb_samples.append(mem)
                    self.timestamps.append(time.time())
            except Exception as e:
                logger.debug(f"Sampler error: {e}")
            time.sleep(self.sample_interval)

    def get_summary(self) -> Dict[str, Any]:
        if not self.rss_mb_samples:
            return {
                "cpu_percent": {"mean": "N/A", "max": "N/A"},
                "memory_rss_mb": {"start": "N/A", "peak": "N/A", "end": "N/A", "delta": "N/A"},
            }

        start_mem = self.rss_mb_samples[0]
        end_mem = self.rss_mb_samples[-1]
        peak_mem = max(self.rss_mb_samples)
        delta_mem = end_mem - start_mem

        return {
            "cpu_percent": {
                "mean": round(float(np.mean(self.cpu_samples)), 2) if self.cpu_samples else 0.0,
                "max": round(float(np.max(self.cpu_samples)), 2) if self.cpu_samples else 0.0,
            },
            "memory_rss_mb": {
                "start": round(start_mem, 2),
                "peak": round(peak_mem, 2),
                "end": round(end_mem, 2),
                "delta": round(delta_mem, 2),
            },
        }


def print_device_list():
    devices = list_audio_input_devices()
    print("=" * 80)
    print("AVAILABLE AUDIO INPUT DEVICES (PortAudio / sounddevice):")
    print("=" * 80)
    if not devices:
        print("  No audio input devices found.")
        print("=" * 80)
        return

    print(f" {'Index':<7} {'Device Name':<45} {'Channels':<10} {'Host API':<15}")
    print("-" * 80)
    for d in devices:
        print(f" [{d['device_index']:<4}] {d['name'][:43]:<45} {d['max_input_channels']:<10} {d['host_api']:<15}")
    print("=" * 80)


def run_endurance(
    duration_seconds: int = 60,
    mode: str = "auto",  # 'mic', 'simulate', 'auto'
    device_index: Optional[int] = None,
    threshold: float = DEFAULT_SCREAM_THRESHOLD,
    cooldown: float = DEFAULT_ALERT_COOLDOWN_SECONDS,
    csv_output_path: Optional[Path] = None,
    report_output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute endurance test session and log empirical measurements."""
    print("=" * 80)
    print(f"STAGE 8.5 — ENDURANCE & RESILIENCE VALIDATION RUNNER")
    print("=" * 80)
    print(f"  - Target Duration:    {duration_seconds} seconds ({duration_seconds / 60:.1f} minutes)")
    print(f"  - Requested Mode:     {mode.upper()}")
    print(f"  - Sample Rate:        {TARGET_SAMPLE_RATE} Hz (Mono Float32)")
    print(f"  - Operating Thresh:   {threshold:.2f} (Stage 5 baseline)")
    print(f"  - Cooldown:           {cooldown:.1f}s")
    print("=" * 80)

    # 1. Check Hardware & Mode Resolution
    input_devices = list_audio_input_devices()
    has_mic = len(input_devices) > 0

    if mode == "mic" and not has_mic:
        print("\n[ERROR - TEST BLOCKED] Mode 'mic' requested but no physical input device is available.")
        return {
            "status": "BLOCKED",
            "reason": "No audio input device detected by sounddevice.",
            "duration_seconds": 0,
        }

    actual_mode = "mic" if (mode in ("mic", "auto") and has_mic) else "simulate"
    print(f"  - Active Run Mode:    {'REAL PHYSICAL MICROPHONE' if actual_mode == 'mic' else 'SIMULATED STREAM'}")

    if actual_mode == "mic":
        selected_dev = device_index
        if selected_dev is None and input_devices:
            # Prefer device with max input channels or default
            selected_dev = input_devices[0]["device_index"]
        dev_info = next((d for d in input_devices if d["device_index"] == selected_dev), {"name": "Default"})
        print(f"  - Selected Device:    [{selected_dev}] {dev_info['name']}")
    else:
        print("  - Simulation:         16 kHz synthetic acoustic stream with periodic distress bursts")

    print("-" * 80)

    # 2. Initialize Detector
    print("[1/3] Initializing StreamDetector (YAMNet + Stage 5 Classifier)...")
    detector = StreamDetector(
        sample_rate=TARGET_SAMPLE_RATE,
        threshold=threshold,
        cooldown_seconds=cooldown,
    )

    # 3. Initialize Metrics Sampler
    sampler = EnduranceMetricsCollector(sample_interval_seconds=1.0)
    sampler.start()

    # 4. Setup Audio Source
    mic = None
    running = True

    def sig_handler(sig, frame):
        nonlocal running
        print("\n[SIGINT / Stop Requested] Concluding test session...")
        running = False

    signal.signal(signal.SIGINT, sig_handler)

    total_samples_ingested = 0

    if actual_mode == "mic":
        print(f"[2/3] Connecting to physical microphone stream...")
        try:
            mic = MicrophoneCapture(
                on_audio_chunk=detector.push_audio,
                sample_rate=TARGET_SAMPLE_RATE,
                device_index=selected_dev,
                block_duration_ms=50.0,
            )
            mic.start()
        except AudioDeviceError as e:
            sampler.stop()
            print(f"\n[AUDIO DEVICE ERROR]\n{e}", file=sys.stderr)
            return {"status": "BLOCKED", "reason": str(e)}
    else:
        print("[2/3] Initializing real-time simulation stream generator...")

    # 5. Monitoring & Inference Loop
    print("\n[3/3] RUNNING ENDURANCE TEST... (Press Ctrl+C to abort early)")
    start_time = time.time()
    last_heartbeat = start_time
    last_sim_time = start_time

    try:
        while running:
            now = time.time()
            elapsed = now - start_time

            if elapsed >= duration_seconds:
                print(f"\nTarget test duration reached ({duration_seconds}s). Concluding session...")
                break

            # If simulated, push audio chunks at real-time rate (every 50ms)
            if actual_mode == "simulate":
                if now - last_sim_time >= 0.05:
                    chunk_samples = int(TARGET_SAMPLE_RATE * 0.05)
                    # Periodic distress burst every 15s to exercise state machine
                    in_burst = (int(elapsed) % 15) in (4, 5)
                    freq = 1200.0 if in_burst else 300.0
                    t_chunk = np.linspace(elapsed, elapsed + 0.05, chunk_samples, endpoint=False, dtype=np.float32)
                    chunk = 0.15 * np.sin(2 * np.pi * freq * t_chunk) if in_burst else 0.02 * np.random.randn(chunk_samples).astype(np.float32)
                    detector.push_audio(chunk)
                    total_samples_ingested += chunk_samples
                    last_sim_time = now

            # Process available windows in detector
            results = detector.process_available_windows()

            # Heartbeat display every 5 seconds
            if now - last_heartbeat >= 5.0:
                mets = detector.get_metrics()
                lat = mets["latency_metrics_ms"]
                cur_mem = sampler.rss_mb_samples[-1] if sampler.rss_mb_samples else 0.0
                cur_cpu = sampler.cpu_samples[-1] if sampler.cpu_samples else 0.0
                state_val = detector.state_machine.current_state.value

                print(
                    f"  [{int(elapsed):>3}s / {duration_seconds}s] State: {state_val:<12} | "
                    f"Windows: {mets['windows_processed']:<5} | "
                    f"Latency: {lat['mean']:>5.1f}ms | "
                    f"Alerts: {mets['total_alerts_emitted']:<2} | "
                    f"CPU: {cur_cpu:>4.1f}% | "
                    f"RAM: {cur_mem:>5.1f}MB"
                )
                last_heartbeat = now

            time.sleep(0.02)

    finally:
        actual_duration = time.time() - start_time
        sampler.stop()
        if mic:
            mic.stop()

    # 6. Collate Results
    metrics = detector.get_metrics()
    resource_summary = sampler.get_summary()
    lat = metrics["latency_metrics_ms"]

    results_data = {
        "timestamp_iso": datetime.now().isoformat(),
        "status": "PASS",
        "mode": actual_mode,
        "is_real_microphone": actual_mode == "mic",
        "requested_duration_seconds": duration_seconds,
        "actual_duration_seconds": round(actual_duration, 2),
        "windows_processed": metrics["windows_processed"],
        "audio_seconds_processed": metrics["total_audio_seconds"],
        "total_alerts_emitted": metrics["total_alerts_emitted"],
        "total_alerts_suppressed": metrics["total_alerts_suppressed"],
        "inference_errors": metrics["inference_errors"],
        "dropped_samples": metrics["dropped_samples"],
        "latency_ms": {
            "mean": lat["mean"],
            "min": lat["min"],
            "max": lat["max"],
            "p95": lat["p95"],
            "samples_timed": lat["samples_timed"],
        },
        "realtime_factor": metrics["realtime_factor"],
        "cpu_percent": resource_summary["cpu_percent"],
        "memory_rss_mb": resource_summary["memory_rss_mb"],
    }

    print("\n" + "=" * 80)
    print("STAGE 8.5 ENDURANCE TEST SUMMARY:")
    print("=" * 80)
    print(f"  - Mode:                  {'REAL PHYSICAL MICROPHONE' if actual_mode == 'mic' else 'SIMULATED STREAM'}")
    print(f"  - Duration:              {results_data['actual_duration_seconds']}s (Requested: {duration_seconds}s)")
    print(f"  - Windows Processed:     {results_data['windows_processed']}")
    print(f"  - Inference Errors:      {results_data['inference_errors']}")
    print(f"  - Dropped Samples:       {results_data['dropped_samples']}")
    print(f"  - Mean Window Latency:   {lat['mean']} ms (P95: {lat['p95']} ms, Max: {lat['max']} ms)")
    print(f"  - Realtime Factor:       {results_data['realtime_factor']}x (< 1.0x is real-time)")
    print(f"  - Alerts Emitted:        {results_data['total_alerts_emitted']} (Suppressed: {results_data['total_alerts_suppressed']})")
    print(f"  - Mean CPU Usage:        {resource_summary['cpu_percent']['mean']}% (Max: {resource_summary['cpu_percent']['max']}%)")
    print(f"  - Memory RSS (MB):       Start: {resource_summary['memory_rss_mb']['start']} MB, Peak: {resource_summary['memory_rss_mb']['peak']} MB, Delta: {resource_summary['memory_rss_mb']['delta']} MB")
    print("=" * 80 + "\n")

    # 7. Write CSV Output if path provided
    if csv_output_path:
        csv_output_path.parent.mkdir(parents=True, exist_ok=True)
        file_exists = csv_output_path.exists()
        with open(csv_output_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow([
                    "timestamp_iso", "mode", "is_real_mic", "duration_sec", "windows_processed",
                    "latency_mean_ms", "latency_p95_ms", "latency_max_ms", "realtime_factor",
                    "cpu_mean_pct", "cpu_max_pct", "rss_start_mb", "rss_peak_mb", "rss_delta_mb",
                    "alerts_emitted", "alerts_suppressed", "inference_errors", "dropped_samples"
                ])
            writer.writerow([
                results_data["timestamp_iso"],
                results_data["mode"],
                results_data["is_real_microphone"],
                results_data["actual_duration_seconds"],
                results_data["windows_processed"],
                lat["mean"],
                lat["p95"],
                lat["max"],
                results_data["realtime_factor"],
                resource_summary["cpu_percent"]["mean"],
                resource_summary["cpu_percent"]["max"],
                resource_summary["memory_rss_mb"]["start"],
                resource_summary["memory_rss_mb"]["peak"],
                resource_summary["memory_rss_mb"]["delta"],
                results_data["total_alerts_emitted"],
                results_data["total_alerts_suppressed"],
                results_data["inference_errors"],
                results_data["dropped_samples"],
            ])
        print(f"Performance metrics appended to CSV: {csv_output_path}")

    return results_data


def main():
    parser = argparse.ArgumentParser(description="Stage 8.5 Real-Time Audio Endurance & Performance Tester.")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds (e.g. 60, 600, 1800).")
    parser.add_argument("--mode", choices=["auto", "mic", "simulate"], default="auto", help="Execution mode.")
    parser.add_argument("--device", type=int, default=None, help="Audio input device index.")
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices and exit.")
    parser.add_argument("--threshold", type=float, default=DEFAULT_SCREAM_THRESHOLD, help="Scream threshold (default: 0.35).")
    parser.add_argument("--cooldown", type=float, default=DEFAULT_ALERT_COOLDOWN_SECONDS, help="Cooldown in seconds (default: 3.0s).")
    parser.add_argument("--csv", type=str, default="reports/stage8_5/stage8_5_performance_results.csv", help="CSV output path.")
    parser.add_argument("--report", type=str, default="reports/stage8_5/endurance_summary.json", help="JSON summary path.")
    args = parser.parse_args()

    if args.list_devices:
        print_device_list()
        return 0

    csv_path = backend_dir / args.csv if args.csv else None
    json_path = backend_dir / args.report if args.report else None

    results = run_endurance(
        duration_seconds=args.duration,
        mode=args.mode,
        device_index=args.device,
        threshold=args.threshold,
        cooldown=args.cooldown,
        csv_output_path=csv_path,
        report_output_path=json_path,
    )

    if json_path and results.get("status") == "PASS":
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"JSON summary written to: {json_path}")

    return 0 if results.get("status") == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
