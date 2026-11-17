"""Live Evaluation Session Runner (Stage 8.6).

Observes live acoustic streams using the existing physical microphone capture
and StreamDetector pipeline without persisting raw audio by default.

Telemetry collected per 0.975s window:
- Window timestamp (UTC)
- Window sequential ID
- Smoothed model score & raw probability
- Operating threshold (0.35)
- Detector state (IDLE / CANDIDATE / ALERT_ACTIVE / COOLDOWN)
- Alert generation event flag
- Window audio RMS signal level
- Window inference latency in ms
- Dropped window count & error status

Writes bounded evaluation logs to:
  backend/logs/evaluation_sessions/<session_id>/window_scores.csv
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.config import (
    BACKEND_DIR,
    DEFAULT_SCREAM_THRESHOLD,
    EVAL_SESSIONS_LOG_DIR,
    STAGE8_6_REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.detector.mic_capture import AudioDeviceError, MicrophoneCapture, list_audio_input_devices
from src.detector.stream_detector import StreamDetector
from src.model.scream_classifier import FestivalScreamClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("live_evaluation")


def display_devices() -> None:
    """Print available audio input devices."""
    devices = list_audio_input_devices()
    print("\n================================================================================")
    print("AVAILABLE AUDIO INPUT DEVICES FOR LIVE EVALUATION")
    print("================================================================================")
    if not devices:
        print("  [ERROR] No input devices found.")
    for d in devices:
        print(f"  [{d['device_index']:2d}] {d['name']} (Channels: {d['max_input_channels']}, Default SR: {int(d['default_samplerate'])} Hz)")
    print("================================================================================\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Live Microphone Evaluation Session (Stage 8.6)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices and exit")
    parser.add_argument("--device", type=int, default=None, help="Explicit microphone device index")
    parser.add_argument("--duration", type=float, default=60.0, help="Evaluation session duration in seconds")
    parser.add_argument("--session-id", type=str, default=None, help="Custom evaluation session identifier")
    parser.add_argument("--threshold", type=float, default=DEFAULT_SCREAM_THRESHOLD, help="Operational scream threshold")
    parser.add_argument("--output-dir", type=str, default=str(EVAL_SESSIONS_LOG_DIR), help="Directory for evaluation telemetry")
    parser.add_argument("--record-audio", action="store_true", help="Save raw audio (DISABLED by default for privacy)")

    args = parser.parse_args()

    if args.list_devices:
        display_devices()
        return

    # Check device
    devices = list_audio_input_devices()
    if not devices:
        print("[ERROR] No audio input devices detected.")
        sys.exit(1)

    selected_dev = None
    if args.device is not None:
        matching = [d for d in devices if d["device_index"] == args.device]
        if not matching:
            print(f"[ERROR] Device index [{args.device}] not found.")
            display_devices()
            sys.exit(1)
        selected_dev = matching[0]
    else:
        selected_dev = devices[0]
        print(f"[INFO] Using default input device: [{selected_dev['device_index']}] {selected_dev['name']}")

    dev_index = selected_dev["device_index"]
    dev_name = selected_dev["name"]

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    session_id = args.session_id or f"live_eval_{timestamp_str}"
    session_dir = Path(args.output_dir) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    csv_path = session_dir / "window_scores.csv"
    summary_path = session_dir / "session_summary.json"

    print("\n================================================================================")
    print("STAGE 8.6: LIVE MICROPHONE EVALUATION SESSION")
    print("================================================================================")
    print(f"  Session ID:          {session_id}")
    print(f"  Selected Device:     [{dev_index}] {dev_name}")
    print(f"  Duration:            {args.duration:.1f} seconds")
    print(f"  Decision Threshold:  {args.threshold:.3f}")
    print(f"  Raw Audio Saved:     {args.record_audio} (Default: False for venue privacy)")
    print(f"  Telemetry Log:       {csv_path}")
    print("================================================================================\n")

    # Initialize StreamDetector
    print("[1/3] Loading YAMNet and Stage 5 Scream Classifier...")
    detector = StreamDetector(threshold=args.threshold)

    # Telemetry storage
    window_count = 0
    threshold_crossings = 0
    state_transitions = 0
    alerts_triggered = 0
    latencies: List[float] = []
    scores: List[float] = []
    last_state = "IDLE"

    # CSV Writer setup
    fieldnames = [
        "timestamp_iso",
        "window_id",
        "smoothed_score",
        "raw_score",
        "threshold",
        "detector_state",
        "alert_generated",
        "audio_rms",
        "latency_ms",
        "dropped_windows",
        "error",
    ]
    csv_file = open(csv_path, "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Audio callback
    def on_chunk(chunk: np.ndarray) -> None:
        detector.audio_buffer.write(chunk)

    print(f"[2/3] Connecting PortAudio input stream on device [{dev_index}]...")
    mic = MicrophoneCapture(
        on_audio_chunk=on_chunk,
        sample_rate=TARGET_SAMPLE_RATE,
        device_index=dev_index,
        block_duration_ms=50.0,
    )

    is_completed = False
    start_time = time.time()

    print("[3/3] STARTING LIVE EVALUATION STREAM... (Press Ctrl+C to stop)\n")
    mic.start()

    try:
        while time.time() - start_time < args.duration:
            time.sleep(0.05)  # Poll every 50ms

            # Process available windows
            results = detector.process_available_windows()
            for res in results:
                window_count += 1
                score = res.get("score", 0.0)
                raw_score = res.get("raw_probability", score)
                state = res.get("state", "IDLE")
                is_alert = res.get("is_alert", False)
                latency = res.get("latency_ms", 0.0)
                audio_rms = res.get("audio_rms", 0.0)
                dropped = detector.dropped_windows

                scores.append(score)
                latencies.append(latency)

                if score >= args.threshold:
                    threshold_crossings += 1

                if state != last_state:
                    state_transitions += 1
                    last_state = state

                if is_alert:
                    alerts_triggered += 1
                    print(f"  >>> ALERT TRIGGERED! [Window {window_count}] Score: {score:.3f} | Latency: {latency:.1f}ms <<<")

                writer.writerow({
                    "timestamp_iso": datetime.now(timezone.utc).isoformat(),
                    "window_id": window_count,
                    "smoothed_score": round(score, 4),
                    "raw_score": round(raw_score, 4),
                    "threshold": args.threshold,
                    "detector_state": state,
                    "alert_generated": is_alert,
                    "audio_rms": round(audio_rms, 6),
                    "latency_ms": round(latency, 2),
                    "dropped_windows": dropped,
                    "error": "",
                })
                csv_file.flush()

                # Live ticker every 10 windows
                if window_count % 10 == 0:
                    elapsed = time.time() - start_time
                    print(
                        f"  [{elapsed:5.1f}s / {args.duration:5.1f}s] "
                        f"Windows: {window_count:3d} | State: {state:12s} | "
                        f"Score: {score:.3f} | Latency: {latency:4.1f}ms | Alerts: {alerts_triggered}"
                    )

        is_completed = True

    except KeyboardInterrupt:
        print("\n\n[STOPPING] Interrupted by operator (Ctrl+C). Finalizing telemetry...")
    except Exception as e:
        logger.error(f"Live evaluation exception: {e}", exc_info=True)
        print(f"\n[ERROR] Stream processing failed: {e}")
    finally:
        mic.stop()
        csv_file.close()

        actual_duration = round(time.time() - start_time, 2)
        summary = {
            "session_id": session_id,
            "status": "COMPLETED" if is_completed else "INTERRUPTED",
            "device_index": dev_index,
            "device_name": dev_name,
            "requested_duration_sec": args.duration,
            "actual_duration_sec": actual_duration,
            "total_windows_processed": window_count,
            "threshold_crossings": threshold_crossings,
            "state_transitions": state_transitions,
            "alerts_triggered": alerts_triggered,
            "mean_score": round(float(np.mean(scores)), 4) if scores else 0.0,
            "max_score": round(float(np.max(scores)), 4) if scores else 0.0,
            "mean_latency_ms": round(float(np.mean(latencies)), 2) if latencies else 0.0,
            "p95_latency_ms": round(float(np.percentile(latencies, 95)), 2) if latencies else 0.0,
            "raw_audio_persisted": args.record_audio,
            "window_scores_csv": str(csv_path),
        }

        import json
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print("\n================================================================================")
        print("LIVE EVALUATION SESSION SUMMARY")
        print("================================================================================")
        print(f"  Status:                   {summary['status']}")
        print(f"  Duration:                 {actual_duration}s (Requested: {args.duration}s)")
        print(f"  Windows Processed:        {window_count}")
        print(f"  Threshold Crossings:      {threshold_crossings} (Score >= {args.threshold})")
        print(f"  State Transitions:        {state_transitions}")
        print(f"  Unique Alerts Triggered:  {alerts_triggered}")
        print(f"  Peak Score Observed:      {summary['max_score']}")
        print(f"  Mean Latency:             {summary['mean_latency_ms']} ms (P95: {summary['p95_latency_ms']} ms)")
        print(f"  Telemetry CSV:            {csv_path}")
        print("================================================================================\n")


if __name__ == "__main__":
    main()
