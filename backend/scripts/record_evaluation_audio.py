"""Controlled Laptop-Microphone Recording Tool for Real-World Evaluation (Stage 8.6).

Provides an auditable, operator-initiated audio collection workflow:
- Lists audio input devices and enforces explicit device selection.
- Displays device name, host API, channels, and native hardware sample rate.
- Pre-recording visual countdown and clear start/stop notifications.
- Faithful audio capture saved as standard 16-bit PCM WAV files.
- Generates sidecar JSON metadata and appends to session & global manifests.
- Safe Ctrl+C interruption and robust hardware resource cleanup.
- Strictly operator-initiated: raw audio is never recorded automatically.
"""

from __future__ import annotations

import argparse
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

try:
    import sounddevice as sd
    import soundfile as sf
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    sd = None
    sf = None
    SOUNDDEVICE_AVAILABLE = False

from src.config import (
    BACKEND_DIR,
    RAW_DATASET_DIR,
    REAL_WORLD_EVAL_DIR,
    STAGE8_6_REPORTS_DIR,
    TARGET_SAMPLE_RATE,
)
from src.dataset.real_world import (
    CONSENT_STATUSES,
    DISTANCE_CATEGORIES,
    ENVIRONMENT_CATEGORIES,
    RECORDING_METHODS,
    SOUND_SOURCE_CATEGORIES,
    build_recording_record,
    compute_file_sha256,
    compute_pcm_sha256,
    load_recording_manifest,
    save_recording_manifests,
)
from src.detector.mic_capture import AudioDeviceError, list_audio_input_devices

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("record_evaluation_audio")


def display_devices() -> None:
    """Print all discovered audio input devices with detailed technical parameters."""
    devices = list_audio_input_devices()
    print("\n================================================================================")
    print("DISCOVERED AUDIO INPUT DEVICES (Windows / PortAudio)")
    print("================================================================================")
    if not devices:
        print("  [ERROR] No audio input devices found or sounddevice library not installed.")
        print("================================================================================\n")
        return

    for dev in devices:
        idx = dev["device_index"]
        name = dev["name"]
        ch = dev["max_input_channels"]
        sr = int(dev["default_samplerate"])
        api = dev["host_api"]
        print(f"  Device [{idx:2d}]: {name}")
        print(f"               Channels: {ch} | Native Sample Rate: {sr} Hz | Host API: {api}")
    print("================================================================================\n")


def record_single_clip(
    device_index: Optional[int],
    duration: float,
    sample_rate: int,
    channels: int,
) -> np.ndarray:
    """Capture raw audio data from sounddevice synchronously."""
    frames_to_record = int(duration * sample_rate)
    logger.info(f"Recording {duration:.2f}s ({frames_to_record} frames at {sample_rate} Hz, {channels} ch)...")

    audio_data = sd.rec(
        frames=frames_to_record,
        samplerate=sample_rate,
        channels=channels,
        device=device_index,
        dtype="float32",
    )
    sd.wait()
    return audio_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Controlled Laptop-Microphone Audio Collection Tool (Stage 8.6)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--list-devices", action="store_true", help="List all available audio input devices and exit")
    parser.add_argument("--device", type=int, default=None, help="Explicit PortAudio input device index")
    parser.add_argument("--duration", type=float, default=5.0, help="Recording duration in seconds (must be > 0.5s)")
    parser.add_argument("--repeats", type=int, default=1, help="Number of consecutive clips to record in this session")
    parser.add_argument("--session-id", type=str, default=None, help="Custom session ID (default: session_YYYYMMDD_HHMMSS)")
    parser.add_argument("--output-dir", type=str, default=str(REAL_WORLD_EVAL_DIR), help="Output base directory")
    parser.add_argument("--countdown", type=int, default=3, help="Countdown seconds before each recording")
    parser.add_argument("--no-countdown", action="store_true", help="Skip pre-recording countdown")
    parser.add_argument("--sample-rate", type=int, default=None, help="Capture sample rate (default: device native default)")
    parser.add_argument("--channels", type=int, default=1, choices=[1, 2], help="Number of channels to capture (1=mono, 2=stereo)")

    # Metadata classifications
    parser.add_argument(
        "--environment",
        type=str,
        default="indoor_quiet",
        choices=list(ENVIRONMENT_CATEGORIES.keys()),
        help="Acoustic environment category",
    )
    parser.add_argument(
        "--sound-source",
        type=str,
        default="other",
        choices=list(SOUND_SOURCE_CATEGORIES.keys()),
        help="Sound source content category",
    )
    parser.add_argument(
        "--distance",
        type=str,
        default="medium_1_2m",
        choices=list(DISTANCE_CATEGORIES.keys()),
        help="Distance from microphone",
    )
    parser.add_argument(
        "--recording-method",
        type=str,
        default="laptop_internal_mic",
        choices=list(RECORDING_METHODS.keys()),
        help="Hardware recording method",
    )
    parser.add_argument(
        "--consent-status",
        type=str,
        default="consented_operator",
        choices=list(CONSENT_STATUSES.keys()),
        help="Participant consent status",
    )
    parser.add_argument("--notes", type=str, default="", help="Optional operator notes or description")

    args = parser.parse_args()

    if args.list_devices:
        display_devices()
        return

    if not SOUNDDEVICE_AVAILABLE:
        print("[ERROR] sounddevice or soundfile library is not available. Please verify installation.")
        sys.exit(1)

    if args.duration < 0.5:
        print("[ERROR] Duration must be at least 0.5 seconds.")
        sys.exit(1)

    # 1. Device Discovery & Validation
    devices = list_audio_input_devices()
    if not devices:
        print("[ERROR] No audio input devices found on system.")
        sys.exit(1)

    selected_dev = None
    if args.device is not None:
        matching = [d for d in devices if d["device_index"] == args.device]
        if not matching:
            print(f"[ERROR] Selected device index [{args.device}] is not a valid input device.")
            display_devices()
            sys.exit(1)
        selected_dev = matching[0]
    else:
        # Default input device
        try:
            default_info = sd.query_devices(kind="input")
            # Find in list
            for d in devices:
                if d["name"] == default_info["name"]:
                    selected_dev = d
                    break
            if selected_dev is None:
                selected_dev = devices[0]
            print(f"[INFO] No explicit device index specified. Using system default input device: [{selected_dev['device_index']}] {selected_dev['name']}")
        except Exception as e:
            selected_dev = devices[0]
            print(f"[INFO] Using first available input device: [{selected_dev['device_index']}] {selected_dev['name']}")

    dev_index = selected_dev["device_index"]
    dev_name = selected_dev["name"]
    native_sr = int(selected_dev["default_samplerate"])
    capture_sr = args.sample_rate if args.sample_rate else native_sr
    capture_channels = min(args.channels, selected_dev["max_input_channels"])

    # 2. Session Directory Preparation
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    session_id = args.session_id or f"session_{timestamp_str}"
    session_dir = Path(args.output_dir) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    print("\n================================================================================")
    print("STAGE 8.6: CONTROLLED AUDIO RECORDING SESSION")
    print("================================================================================")
    print(f"  Session ID:        {session_id}")
    print(f"  Output Directory:  {session_dir}")
    print(f"  Selected Device:   [{dev_index}] {dev_name}")
    print(f"  Capture Rate:      {capture_sr} Hz (Hardware Native: {native_sr} Hz)")
    print(f"  Channels:          {capture_channels} ({'Mono' if capture_channels == 1 else 'Stereo'})")
    print(f"  Clip Duration:     {args.duration:.2f} seconds")
    print(f"  Clips to Record:   {args.repeats}")
    print(f"  Environment:       {args.environment} ({ENVIRONMENT_CATEGORIES[args.environment]})")
    print(f"  Sound Source:      {args.sound_source} ({SOUND_SOURCE_CATEGORIES[args.sound_source]})")
    print(f"  Distance:          {args.distance}")
    print(f"  Recording Method:  {args.recording_method}")
    print(f"  Consent Status:    {args.consent_status}")
    if args.notes:
        print(f"  Operator Notes:    {args.notes}")
    print("================================================================================\n")

    session_records: List[Dict[str, Any]] = []

    # 3. Execution of Recording Loop
    try:
        for clip_idx in range(1, args.repeats + 1):
            clip_id = f"{session_id}_{clip_idx:03d}"
            wav_filename = f"{clip_id}.wav"
            wav_path = session_dir / wav_filename
            relative_audio_path = f"{session_id}/{wav_filename}"

            print(f"\n--- Clip [{clip_idx}/{args.repeats}]: {clip_id} ---")

            # Countdown
            if not args.no_countdown and args.countdown > 0:
                print("Get ready...")
                for sec in range(args.countdown, 0, -1):
                    print(f"  [{sec}]...", end="\r", flush=True)
                    time.sleep(1.0)
                print("  [RECORDING NOW!]                             ")
            else:
                print("  [RECORDING NOW!]")

            # Record
            t_start = time.perf_counter()
            audio_array = record_single_clip(
                device_index=dev_index,
                duration=args.duration,
                sample_rate=capture_sr,
                channels=capture_channels,
            )
            elapsed = time.perf_counter() - t_start
            print(f"  [STOPPED] Recorded {elapsed:.2f}s of audio.")

            # Flatten to mono for diagnostics/quantization if needed
            mono_view = audio_array[:, 0] if audio_array.ndim == 2 else audio_array
            peak_val = float(np.max(np.abs(mono_view)))
            rms_val = float(np.sqrt(np.mean(mono_view ** 2)))

            print(f"  Audio Metrics: Peak Amplitude={peak_val:.4f}, RMS={rms_val:.6f}")
            if peak_val >= 0.999:
                print("  [WARNING] Audio signal hit digital full scale (clipping detected).")
            elif peak_val < 0.005:
                print("  [WARNING] Audio signal is near silence. Please check microphone gain.")

            # Save faithfully as 16-bit PCM WAV
            sf.write(str(wav_path), audio_array, capture_sr, subtype="PCM_16")

            # Compute Hashes
            file_hash = compute_file_sha256(wav_path)
            pcm_hash = compute_pcm_sha256(mono_view)

            # Build Metadata Record
            record = build_recording_record(
                recording_id=clip_id,
                session_id=session_id,
                relative_audio_path=relative_audio_path,
                duration_seconds=args.duration,
                actual_sample_rate=capture_sr,
                channel_count=capture_channels,
                sample_format="PCM_16",
                recording_device_label=dev_name,
                environment_category=args.environment,
                sound_source_category=args.sound_source,
                distance_category=args.distance,
                recording_method=args.recording_method,
                consent_status=args.consent_status,
                review_notes=args.notes,
                ground_truth_label="unlabeled",  # Never auto-labeled
                source_group_id=f"src_{session_id}",
                file_sha256=file_hash,
                pcm_sha256=pcm_hash,
                audio_rms=rms_val,
                peak_amplitude=peak_val,
            )
            session_records.append(record)

            # Save individual clip sidecar JSON
            sidecar_path = session_dir / f"{clip_id}.json"
            import json
            with open(sidecar_path, "w", encoding="utf-8") as f:
                json.dump(record, f, indent=2)

            print(f"  Saved WAV:      {wav_path.name}")
            print(f"  Saved Sidecar:  {sidecar_path.name}")
            print(f"  SHA-256 Hash:   {file_hash[:16]}...")

            if clip_idx < args.repeats:
                print("\nPausing 2.0s before next clip...")
                time.sleep(2.0)

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Recording interrupted by operator (Ctrl+C). Saving completed clips...")
    except Exception as e:
        logger.error(f"Recording error occurred: {e}", exc_info=True)
        print(f"\n[ERROR] Audio recording failed: {e}")

    finally:
        # Save session manifests if any clips were recorded
        if session_records:
            save_recording_manifests(session_records, session_dir)
            print(f"\n[SUCCESS] Session manifest updated: {session_dir / 'recording_manifest.json'}")

            # Update or create global manifest in reports/stage8_6/ and raw_dataset_dir
            master_dir = STAGE8_6_REPORTS_DIR
            master_dir.mkdir(parents=True, exist_ok=True)
            master_manifest_json = master_dir / "recording_manifest.json"

            existing_master_records = load_recording_manifest(master_manifest_json) if master_manifest_json.exists() else []
            # Merge without duplicates by recording_id
            existing_ids = {r["recording_id"] for r in existing_master_records}
            merged_records = list(existing_master_records)
            for r in session_records:
                if r["recording_id"] not in existing_ids:
                    merged_records.append(r)
                    existing_ids.add(r["recording_id"])

            save_recording_manifests(merged_records, master_dir)
            save_recording_manifests(merged_records, Path(args.output_dir))
            print(f"[SUCCESS] Master manifest updated: {master_manifest_json} (Total: {len(merged_records)} recordings)")
        else:
            print("\n[INFO] Zero clips recorded in this session.")


if __name__ == "__main__":
    main()
