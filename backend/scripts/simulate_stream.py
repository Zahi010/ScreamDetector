"""Offline Stream Simulation CLI Script (Stage 7).

Simulates continuous real-time audio streaming from an audio file without physical microphone hardware.
Feeds overlapping chunks into StreamDetector, exercising the exact same rolling-window inference,
temporal smoothing, state transitions, event logging, and alert callbacks.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import numpy as np

from src.audio.preprocessor import generate_synthetic_chirp, load_audio
from src.config import (
    NIGENS_DIR,
    OPENSLR99_DIR,
    REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.detector import StreamDetector


def find_default_scream_wav() -> Optional[Path]:
    """Find a verified scream WAV file from OpenSLR or NIGENS datasets for simulation."""
    openslr_scream_dir = OPENSLR99_DIR / "screaming"
    if openslr_scream_dir.is_dir():
        wavs = list(openslr_scream_dir.glob("*.wav"))
        if wavs:
            return wavs[0]

    nigens_scream_dir = NIGENS_DIR / "femaleScream"
    if nigens_scream_dir.is_dir():
        wavs = list(nigens_scream_dir.glob("*.wav"))
        if wavs:
            return wavs[0]

    return None


def generate_simulation_report(
    sim_metrics: Dict[str, Any],
    events_detected: List[Dict[str, Any]],
    audio_path_str: str,
    audio_duration: float,
    wall_clock_elapsed: float,
    report_path: Path,
) -> None:
    """Generate Markdown report for stream simulation and latency benchmarks."""
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lat_metrics = sim_metrics.get("latency_metrics_ms", {})
    hop_ms = sim_metrics.get("hop_duration_ms", 487.5)
    rtf = sim_metrics.get("realtime_factor", 0.0)
    throughput_x = (audio_duration / wall_clock_elapsed) if wall_clock_elapsed > 0 else 0.0

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Stage 7 Streaming Detection Latency & Simulation Benchmark Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        f.write("## 1. Executive Summary\n\n")
        f.write(f"- **Simulated Audio Source**: `{audio_path_str}`\n")
        f.write(f"- **Simulated Audio Duration**: **{audio_duration:.2f} seconds**\n")
        f.write(f"- **Total Wall-Clock Execution Time**: **{wall_clock_elapsed:.2f} seconds**\n")
        f.write(f"- **Processing Throughput**: **{throughput_x:.2f}x Real-Time** (Inference executes faster than real-time playback)\n")
        f.write(f"- **Total Windows Processed**: **{sim_metrics['windows_processed']}** (Hop: {hop_ms:.1f}ms)\n")
        f.write(f"- **Total Alerts Emitted**: **{sim_metrics['total_alerts_emitted']}**\n")
        f.write(f"- **Duplicate Alerts Suppressed During Cooldown**: **{sim_metrics['total_alerts_suppressed']}**\n")
        f.write(f"- **Inference / Buffer Errors**: **{sim_metrics['inference_errors']}**\n\n")

        f.write("---\n\n")
        f.write("## 2. Window Latency Statistics (End-to-End per 0.975s Window)\n\n")
        f.write("> [!NOTE]\n")
        f.write("> **Latency Measurement Scope**:\n")
        f.write("> Latency values include: (1) YAMNet 1,024-dimensional feature extraction, (2) max-pooling, ")
        f.write("and (3) Logistic Regression pipeline classification. They do not include audio buffering overhead.\n\n")

        f.write("| Latency Metric | Measured Value (ms) | Target Constraint |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Mean Window Latency** | **{lat_metrics.get('mean', 0.0):.2f} ms** | < 100 ms (Real-time threshold) |\n")
        f.write(f"| **Minimum Latency** | **{lat_metrics.get('min', 0.0):.2f} ms** | — |\n")
        f.write(f"| **95th Percentile (P95)** | **{lat_metrics.get('p95', 0.0):.2f} ms** | < 200 ms |\n")
        f.write(f"| **Maximum Peak Latency** | **{lat_metrics.get('max', 0.0):.2f} ms** | < {hop_ms:.1f} ms (Hop step boundary) |\n")
        f.write(f"| **Real-Time Factor (RTF)** | **{rtf:.4f}** | < 1.0 (Real-time capability) |\n\n")

        f.write("---\n\n")
        f.write("## 3. Detected Events Log\n\n")
        if not events_detected:
            f.write("No scream alert events were triggered during this simulation run.\n\n")
        else:
            f.write("| Event ID | Stream Time (Start - End) | Duration | Peak Score | Threshold | Emitted? | Contributing Windows |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for ev in events_detected:
                f.write(
                    f"| `{ev['event_id']}` | {ev['start_stream_time']:.2f}s – {ev['end_stream_time']:.2f}s | "
                    f"{ev['duration_seconds']:.2f}s | **{ev['peak_probability']:.4f}** | {ev['threshold']:.2f} | "
                    f"{'YES (ALERT)' if ev['alert_emitted'] else 'SUPPRESSED'} | {ev['window_count']} |\n"
                )
            f.write("\n")

        f.write("---\n\n")
        f.write("## 4. Methodological Disclaimer\n\n")
        f.write("1. **Simulation vs. Live Microphone**: Offline simulation exercises identical model and state-machine code, ")
        f.write("but does not experience physical hardware interrupts, microphone electrical noise, or operating system thread contention.\n")
        f.write("2. **Festival Noise Gap**: Stage 6 contains 0 approved external hard negatives; true acoustic robustness against live EDM music and crowd cheering remains unverified until dedicated field recordings are ingested.\n")


def run_simulation(
    audio_path: Optional[str] = None,
    use_synthetic: bool = False,
    threshold: float = 0.35,
    playback_speed: float = 0.0,
    chunk_ms: float = 50.0,
    generate_report: bool = True,
) -> int:
    print("=" * 80)
    print("STAGE 7 — OFFLINE STREAMING DETECTOR SIMULATION")
    print("=" * 80)

    # 1. Determine Input Audio
    is_synthetic = False
    target_path: Optional[Path] = None

    if use_synthetic:
        is_synthetic = True
        audio_label = "[SYNTHETIC CHIRP + TONE SEQUENCE - 4.0s]"
        # 1.5s silence + 1.5s chirp (scream-like) + 1.0s silence
        c1 = np.zeros(int(TARGET_SAMPLE_RATE * 1.5), dtype=np.float32)
        c2 = generate_synthetic_chirp(start_hz=1200.0, end_hz=3200.0, duration_seconds=1.5)
        c3 = np.zeros(int(TARGET_SAMPLE_RATE * 1.0), dtype=np.float32)
        waveform = np.concatenate([c1, c2, c3])
        total_duration = len(waveform) / TARGET_SAMPLE_RATE
    elif audio_path:
        target_path = Path(audio_path).resolve()
        if not target_path.exists():
            print(f"[ERROR] Audio file not found: {target_path}", file=sys.stderr)
            return 1
        audio_label = target_path.name
        waveform, meta = load_audio(target_path, target_sr=TARGET_SAMPLE_RATE)
        total_duration = meta.duration_seconds
    else:
        target_path = find_default_scream_wav()
        if target_path:
            audio_label = target_path.name
            waveform, meta = load_audio(target_path, target_sr=TARGET_SAMPLE_RATE)
            total_duration = meta.duration_seconds
        else:
            print("[WARN] No audio path specified and no dataset sample found. Using synthetic signal.")
            is_synthetic = True
            audio_label = "[SYNTHETIC SIGNAL]"
            waveform = generate_synthetic_chirp(start_hz=800.0, end_hz=2800.0, duration_seconds=3.0)
            total_duration = len(waveform) / TARGET_SAMPLE_RATE

    print(f"\n[Simulation Target]: {audio_label}")
    print(f"  - Duration:              {total_duration:.2f} seconds ({len(waveform):,} samples at {TARGET_SAMPLE_RATE} Hz)")
    print(f"  - Playback Mode:         {'Real-Time (1.0x)' if playback_speed == 1.0 else f'Accelerated ({playback_speed}x)' if playback_speed > 0 else 'Maximum Benchmark Speed (Unthrottled)'}")
    print(f"  - Chunk Size:            {chunk_ms:.1f} ms ({int(TARGET_SAMPLE_RATE * chunk_ms / 1000.0)} samples)")
    print(f"  - Decision Threshold:    {threshold:.2f} (Stage 5 baseline)")

    # 2. Initialize Stream Detector
    print("\n[Step 1/3] Initializing StreamDetector and models...")
    events_captured: List[Dict[str, Any]] = []

    def on_alert_listener(event_dict: Dict[str, Any]):
        events_captured.append(event_dict)

    detector = StreamDetector(
        sample_rate=TARGET_SAMPLE_RATE,
        threshold=threshold,
        min_consecutive_positive=2,
        cooldown_seconds=3.0,
    )
    detector.alert_dispatcher.subscribe(on_alert_listener)

    # 3. Stream Audio in Chunks
    chunk_samples = int(TARGET_SAMPLE_RATE * (chunk_ms / 1000.0))
    total_samples = len(waveform)
    num_chunks = int(np.ceil(total_samples / chunk_samples))

    print(f"\n[Step 2/3] Streaming audio through rolling-window engine ({num_chunks} chunks)...")
    wall_start = time.perf_counter()

    for i in range(num_chunks):
        start_idx = i * chunk_samples
        end_idx = min(total_samples, start_idx + chunk_samples)
        chunk = waveform[start_idx:end_idx]

        # Push chunk into circular rolling buffer
        detector.push_audio(chunk)

        # Process any ready windows
        window_results = detector.process_available_windows()
        for wr in window_results:
            status_tag = "POS (SCREAM)" if wr.is_positive else "NEG"
            print(
                f"  [Sim Time: {wr.stream_time_seconds:6.2f}s] Window #{wr.window_index:3d} | "
                f"Raw P: {wr.raw_probability:6.4f} | Smoothed P: {wr.smoothed_probability:6.4f} | "
                f"State: {detector.state_machine.current_state.value:<12} | "
                f"Latency: {wr.latency_ms:5.1f}ms | {status_tag}"
            )

        # Playback throttle if requested
        if playback_speed > 0.0:
            target_elapsed = (end_idx / TARGET_SAMPLE_RATE) / playback_speed
            actual_elapsed = time.perf_counter() - wall_start
            sleep_needed = target_elapsed - actual_elapsed
            if sleep_needed > 0.001:
                time.sleep(sleep_needed)

    wall_elapsed = time.perf_counter() - wall_start
    metrics = detector.get_metrics()

    print("\n" + "=" * 80)
    print("SIMULATION EXECUTION SUMMARY:")
    print("=" * 80)
    print(f"  - Simulated Audio Time:   {total_duration:.2f} seconds")
    print(f"  - Wall-Clock Run Time:    {wall_elapsed:.2f} seconds ({total_duration / wall_elapsed:.2f}x Real-Time)")
    print(f"  - Total Windows Evaluated:{metrics['windows_processed']}")
    print(f"  - Alerts Emitted:         {metrics['total_alerts_emitted']}")
    print(f"  - Duplicate Alarms Muted: {metrics['total_alerts_suppressed']} (during cooldown)")
    lat = metrics["latency_metrics_ms"]
    print(f"  - Mean Window Latency:    {lat['mean']:.2f} ms (Min: {lat['min']:.1f}ms, Max: {lat['max']:.1f}ms, P95: {lat['p95']:.1f}ms)")
    print(f"  - Real-Time Factor (RTF): {metrics['realtime_factor']:.4f} (Hop step: {metrics['hop_duration_ms']:.1f}ms)")
    print("=" * 80)

    # 4. Generate Latency & Simulation Report
    if generate_report:
        report_path = REPORTS_DIR / "stage7_latency_and_simulation_report.md"
        generate_simulation_report(
            sim_metrics=metrics,
            events_detected=events_captured,
            audio_path_str=str(target_path) if target_path else audio_label,
            audio_duration=total_duration,
            wall_clock_elapsed=wall_elapsed,
            report_path=report_path,
        )
        print(f"\n[Report Generated]: {report_path}")

    print("\n[SUCCESS] Stream simulation completed successfully!\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate real-time streaming scream detection on a WAV file.")
    parser.add_argument("--audio", type=str, default=None, help="Path to WAV audio file. Defaults to scream sample.")
    parser.add_argument("--synthetic", action="store_true", help="Simulate using a generated synthetic test audio.")
    parser.add_argument("--threshold", type=float, default=0.35, help="Decision threshold (default: 0.35).")
    parser.add_argument("--speed", type=float, default=0.0, help="Playback speed (1.0 = real-time, 0.0 = max speed).")
    parser.add_argument("--chunk-ms", type=float, default=50.0, help="Audio chunk size in ms (default: 50ms).")
    parser.add_argument("--no-report", action="store_true", help="Do not write report to reports directory.")
    args = parser.parse_args()

    return run_simulation(
        audio_path=args.audio,
        use_synthetic=args.synthetic,
        threshold=args.threshold,
        playback_speed=args.speed,
        chunk_ms=args.chunk_ms,
        generate_report=not args.no_report,
    )


if __name__ == "__main__":
    sys.exit(main())
