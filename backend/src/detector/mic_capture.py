"""Live Microphone Capture Interface using sounddevice (Stage 7).

Manages non-blocking audio capture from physical microphones on Windows and Linux:
- Normalizes incoming stream to 16,000 Hz, mono, float32.
- Feeds raw audio frames into StreamDetector without blocking the audio driver callback.
- Robustly handles missing devices, permission denials, and PortAudio errors.
- Provides device enumeration and diagnostics.
"""

from __future__ import annotations

import logging
import sys
import threading
from typing import Callable, List, Optional

import numpy as np

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    sd = None
    SOUNDDEVICE_AVAILABLE = False

from src.config import TARGET_SAMPLE_RATE

logger = logging.getLogger("mic_capture")


class AudioDeviceError(Exception):
    """Raised when an audio input device cannot be initialized or accessed."""
    pass


def list_audio_input_devices() -> List[dict]:
    """Query and enumerate all available audio input devices on the system."""
    if not SOUNDDEVICE_AVAILABLE:
        return []

    devices = []
    try:
        host_apis = sd.query_hostapis()
        for idx, dev in enumerate(sd.query_devices()):
            if dev.get("max_input_channels", 0) > 0:
                api_name = host_apis[dev["hostapi"]]["name"] if dev.get("hostapi") < len(host_apis) else "Unknown"
                devices.append({
                    "device_index": idx,
                    "name": dev["name"],
                    "max_input_channels": dev["max_input_channels"],
                    "default_samplerate": dev["default_samplerate"],
                    "host_api": api_name,
                })
    except Exception as e:
        logger.warning(f"Error querying audio devices: {e}")
    return devices


class MicrophoneCapture:
    """Non-blocking physical microphone audio stream capturer."""

    def __init__(
        self,
        on_audio_chunk: Callable[[np.ndarray], None],
        sample_rate: int = TARGET_SAMPLE_RATE,
        device_index: Optional[int] = None,
        block_duration_ms: float = 50.0,
        chunk_duration_ms: Optional[float] = None,
    ):
        """Initialize microphone capture.

        Args:
            on_audio_chunk: Callback function invoked with float32 mono audio chunks.
            sample_rate: Desired sample rate in Hz (default: 16,000 Hz).
            device_index: Optional sounddevice device index (None for system default).
            block_duration_ms: Capture chunk duration in milliseconds (default: 50ms = 800 samples).
            chunk_duration_ms: Alias for block_duration_ms.
        """
        if chunk_duration_ms is not None:
            block_duration_ms = chunk_duration_ms

        self.on_audio_chunk = on_audio_chunk
        self.sample_rate = int(sample_rate)
        self.device_index = device_index
        self.block_size = int(self.sample_rate * (block_duration_ms / 1000.0))

        self._stream: Optional[Any] = None
        self._is_active = False
        self._lock = threading.Lock()

    @property
    def is_active(self) -> bool:
        """Check if microphone stream is actively capturing."""
        with self._lock:
            return self._is_active

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: Any,
        status: Any,
    ) -> None:
        """Non-blocking low-level PortAudio stream callback."""
        if status:
            logger.warning(f"PortAudio status warning: {status}")

        # Flatten mono channel to 1D float32
        chunk = indata[:, 0].copy() if indata.ndim == 2 else indata.copy()
        try:
            self.on_audio_chunk(chunk)
        except Exception as e:
            logger.error(f"Error forwarding microphone chunk: {e}", exc_info=True)

    def start(self) -> None:
        """Start capturing audio from the microphone."""
        if not SOUNDDEVICE_AVAILABLE:
            raise AudioDeviceError(
                "sounddevice library is not installed. Run `uv pip install sounddevice` to enable live mic."
            )

        with self._lock:
            if self._is_active:
                logger.warning("Microphone stream is already active.")
                return

            try:
                # Query device info
                if self.device_index is not None:
                    dev_info = sd.query_devices(self.device_index)
                else:
                    dev_info = sd.query_devices(kind="input")

                if dev_info.get("max_input_channels", 0) < 1:
                    raise AudioDeviceError(
                        f"Selected device '{dev_info.get('name')}' has 0 input channels."
                    )

                logger.info(
                    f"Opening microphone stream on: '{dev_info['name']}' "
                    f"(sample_rate: {self.sample_rate} Hz, block_size: {self.block_size} samples)"
                )

                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    blocksize=self.block_size,
                    device=self.device_index,
                    channels=1,
                    dtype="float32",
                    callback=self._audio_callback,
                )
                self._stream.start()
                self._is_active = True
                logger.info("Microphone audio stream started successfully.")

            except Exception as e:
                self._is_active = False
                self._stream = None
                available_devices = list_audio_input_devices()
                dev_list_str = "\n".join([f"  [{d['device_index']}] {d['name']} ({d['host_api']})" for d in available_devices[:8]])
                raise AudioDeviceError(
                    f"Failed to initialize audio input device: {e}\n"
                    f"Available input devices:\n{dev_list_str if dev_list_str else '  No input devices found.'}"
                ) from e

    def stop(self) -> None:
        """Stop microphone capture and release hardware resources."""
        with self._lock:
            if not self._is_active or self._stream is None:
                return

            try:
                self._stream.stop()
                self._stream.close()
            except Exception as e:
                logger.warning(f"Error closing audio input stream: {e}")
            finally:
                self._stream = None
                self._is_active = False
                logger.info("Microphone stream stopped.")
