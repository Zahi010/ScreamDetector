"""Live Microphone Streaming Scream Detector CLI Script (Stage 7).

Captures continuous audio from the physical microphone using sounddevice,
feeds audio into StreamDetector, and prints real-time alerts.
Gracefully handles missing devices, permission errors, and clean shutdown on Ctrl+C.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import (
    DEFAULT_ALERT_COOLDOWN_SECONDS,
    DEFAULT_SCREAM_THRESHOLD,
    TARGET_SAMPLE_RATE,
)
from src.detector import (
    AudioDeviceError,
    MicrophoneCapture,
    StreamDetector,
    list_audio_input_devices,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("run_stream_detector")


def print_device_list() -> None:
    """Print available input audio devices."""
    devices = list_audio_input_devices()
    print("=" * 80)
    print("AVAILABLE AUDIO INPUT DEVICES (sounddevice / PortAudio):")
    print("=" * 80)
    if not devices:
        print("  No audio input devices found.")
        print("=" * 80)
        return

    print(f" {'Index':<7} {'Device Name':<42} {'Channels':<10} {'Host API':<15}")
    print("-" * 80)
    for d in devices:
        print(f" [{d['device_index']:<4}] {d['name'][:40]:<42} {d['max_input_channels']:<10} {d['host_api']:<15}")
    print("=" * 80)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real-time festival scream detector from microphone.")
    parser.add_argument("--list-devices", action="store_true", help="List available audio input devices and exit.")
    parser.add_argument("--device", type=int, default=None, help="Audio input device index.")
    parser.add_argument("--threshold", type=float, default=0.35, help="Decision threshold (default: 0.35).")
    parser.add_argument("--cooldown", type=float, default=DEFAULT_ALERT_COOLDOWN_SECONDS, help="Alert cooldown in seconds (default: 3.0s).")
    parser.add_argument("--min-windows", type=int, default=2, help="Consecutive positive windows before triggering (default: 2).")
    parser.add_argument("--opt-in-recording", action="store_true", help="Explicitly opt into saving raw audio snippets (Default: False for privacy).")
    args = parser.parse_args()

    if args.list_devices:
        print_device_list()
        return 0

    print("=" * 80)
    print("FESTIVAL SCREAM DETECTOR — REAL-TIME MICROPHONE STREAM ENGINE (STAGE 7)")
    print("=" * 80)
    print(f"  - Target Sample Rate:     {TARGET_SAMPLE_RATE} Hz (Mono Float32)")
    print(f"  - Operating Threshold:    {args.threshold:.2f} (Stage 5 baseline)")
    print(f"  - Window Duration:        0.975s (15,600 samples)")
    print(f"  - Window Hop Step:        0.4875s (7,800 samples, ~50% overlap)")
    print(f"  - Min Evidence Windows:   {args.min_windows} consecutive windows (~1.46s distress energy)")
    print(f"  - Alert Cooldown:         {args.cooldown:.1f} seconds")
    print(f"  - Raw Audio Recording:    {'ENABLED (Opt-in)' if args.opt_in_recording else 'DISABLED (Default Privacy-Preserving)'}")
    print("=" * 80)

    # 1. Initialize Streaming Detector Engine
    print("\n[Step 1/2] Initializing StreamDetector, YAMNet feature extractor, and classifier...")
    detector = StreamDetector(
        sample_rate=TARGET_SAMPLE_RATE,
        threshold=args.threshold,
        min_consecutive_positive=args.min_windows,
        cooldown_seconds=args.cooldown,
    )

    # 2. Setup Microphone Capture
    print(f"\n[Step 2/2] Connecting to microphone input device (Index: {args.device if args.device is not None else 'Default'})...")
    mic = MicrophoneCapture(
        on_audio_chunk=detector.push_audio,
        sample_rate=TARGET_SAMPLE_RATE,
        device_index=args.device,
        block_duration_ms=50.0,  # 50ms chunks = 800 samples
    )

    running = True

    def signal_handler(sig, frame):
        nonlocal running
        print("\n[Ctrl+C received] Stopping microphone stream...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)

    try:
        mic.start()
        print("\n" + "-" * 80)
        print("LISTENING FOR DISTRESS VOCALIZATIONS... (Press Ctrl+C to stop)")
        print("-" * 80)

        last_report_time = time.time()
        while running:
            # Process any ready rolling windows
            results = detector.process_available_windows()
            for r in results:
                if r.is_positive:
                    print(
                        f"  [{datetime.now().strftime('%H:%M:%S')}] Positive window: "
                        f"Prob: {r.raw_probability:.4f} (State: {detector.state_machine.current_state.value})"
                    )

            # Sleep briefly to yield CPU
            time.sleep(0.02)

            # Heartbeat logging every 30s
            if time.time() - last_report_time >= 30.0:
                metrics = detector.get_metrics()
                lat = metrics["latency_metrics_ms"]
                print(
                    f"  [Heartbeat] Stream active: {metrics['total_audio_seconds']:.1f}s | "
                    f"Windows: {metrics['windows_processed']} | "
                    f"Alerts: {metrics['total_alerts_emitted']} | "
                    f"Mean Latency: {lat['mean']:.1f}ms"
                )
                last_report_time = time.time()

    except AudioDeviceError as e:
        print(f"\n[AUDIO DEVICE ERROR]\n{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n[UNEXPECTED STREAM ERROR]\n{e}", file=sys.stderr)
        return 1
    finally:
        mic.stop()
        metrics = detector.get_metrics()
        print("\n" + "=" * 80)
        print("SESSION METRICS SUMMARY:")
        print(f"  - Windows Processed:     {metrics['windows_processed']}")
        print(f"  - Total Audio Duration:  {metrics['total_audio_seconds']:.2f} seconds")
        print(f"  - Alerts Emitted:        {metrics['total_alerts_emitted']}")
        print(f"  - Alarms Muted/Cooldown: {metrics['total_alerts_suppressed']}")
        lat = metrics["latency_metrics_ms"]
        print(f"  - Mean Window Latency:   {lat['mean']:.2f} ms (Min: {lat['min']:.1f}ms, Max: {lat['max']:.1f}ms)")
        print("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
