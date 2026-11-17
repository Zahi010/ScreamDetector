"""Thread-Safe Bounded Rolling Audio Buffer (Stage 7).

Maintains a continuous in-memory circular audio stream for real-time rolling-window inference.
Enforces bounded memory growth, tracks absolute sample offsets, and manages window extraction.
"""

from __future__ import annotations

import logging
import threading
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger("audio_buffer")


class BufferUnderrunError(Exception):
    """Raised when requesting audio beyond the available buffer capacity."""
    pass


class RollingAudioBuffer:
    """Thread-safe circular audio buffer bounded by a maximum duration in seconds."""

    def __init__(
        self,
        sample_rate: int = 16000,
        max_duration_seconds: float = 10.0,
    ):
        """Initialize rolling audio buffer.

        Args:
            sample_rate: Audio sampling rate in Hz (default: 16,000 Hz).
            max_duration_seconds: Maximum buffer capacity before oldest audio is overwritten.
        """
        self.sample_rate = int(sample_rate)
        self.max_capacity_samples = int(self.sample_rate * max_duration_seconds)
        self._lock = threading.Lock()

        # Circular buffer allocation
        self._buffer = np.zeros(self.max_capacity_samples, dtype=np.float32)
        self._write_pos: int = 0  # Position in circular array
        self._total_samples_written: int = 0
        self._dropped_samples: int = 0
        self._read_offset: int = 0

    @property
    def total_samples_written(self) -> int:
        """Total cumulative audio samples ingested since initialization."""
        with self._lock:
            return self._total_samples_written

    @property
    def buffered_samples(self) -> int:
        """Current number of active audio samples retained in memory."""
        with self._lock:
            return min(self._total_samples_written, self.max_capacity_samples)

    @property
    def buffered_seconds(self) -> float:
        """Current duration of audio in seconds retained in memory."""
        return self.buffered_samples / self.sample_rate

    @property
    def dropped_samples(self) -> int:
        """Count of samples overwritten before being read."""
        with self._lock:
            return self._dropped_samples

    def write(self, audio_chunk: np.ndarray) -> int:
        """Write a new chunk of mono float32 audio into the rolling buffer.

        Args:
            audio_chunk: 1D float32 numpy array.

        Returns:
            Number of samples successfully written.
        """
        if audio_chunk.ndim != 1:
            audio_chunk = audio_chunk.flatten()

        chunk_len = len(audio_chunk)
        if chunk_len == 0:
            return 0

        # Ensure float32
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        with self._lock:
            # If a single chunk is larger than entire buffer capacity, keep only latest
            if chunk_len >= self.max_capacity_samples:
                self._buffer[:] = audio_chunk[-self.max_capacity_samples:]
                self._write_pos = 0
                self._dropped_samples += (self._total_samples_written + chunk_len - self.max_capacity_samples)
                self._total_samples_written += chunk_len
                return chunk_len

            # Check if write will overwrite unread samples beyond buffer capacity
            samples_held = min(self._total_samples_written, self.max_capacity_samples)
            if samples_held + chunk_len > self.max_capacity_samples:
                overflow = (samples_held + chunk_len) - self.max_capacity_samples
                self._dropped_samples += overflow

            # Circular write
            space_at_end = self.max_capacity_samples - self._write_pos
            if chunk_len <= space_at_end:
                self._buffer[self._write_pos : self._write_pos + chunk_len] = audio_chunk
                self._write_pos = (self._write_pos + chunk_len) % self.max_capacity_samples
            else:
                self._buffer[self._write_pos :] = audio_chunk[:space_at_end]
                remaining = chunk_len - space_at_end
                self._buffer[:remaining] = audio_chunk[space_at_end:]
                self._write_pos = remaining

            self._total_samples_written += chunk_len

        return chunk_len

    def has_window(self, window_samples: int, start_offset: int) -> bool:
        """Check if an audio window of specified size starting at start_offset is ready."""
        with self._lock:
            return (start_offset + window_samples) <= self._total_samples_written

    def _get_window_locked(
        self,
        window_samples: int,
        start_offset: int,
    ) -> Optional[np.ndarray]:
        """Internal helper to extract window assuming self._lock is already held."""
        end_offset = start_offset + window_samples
        if end_offset > self._total_samples_written:
            return None

        # Check if start_offset has already fallen out of the rolling circular window
        oldest_available_offset = max(0, self._total_samples_written - self.max_capacity_samples)
        if start_offset < oldest_available_offset:
            raise BufferUnderrunError(
                f"Requested offset {start_offset} has expired from rolling buffer "
                f"(oldest available offset: {oldest_available_offset})."
            )

        # Map absolute offsets to circular array indices
        start_idx = (self._write_pos - (self._total_samples_written - start_offset)) % self.max_capacity_samples
        end_idx = start_idx + window_samples

        if end_idx <= self.max_capacity_samples:
            window = self._buffer[start_idx:end_idx].copy()
        else:
            # Wrap-around slice
            part1 = self._buffer[start_idx:]
            part2 = self._buffer[: end_idx % self.max_capacity_samples]
            window = np.concatenate([part1, part2])

        return window

    def get_window(
        self,
        window_samples: int,
        start_offset: int,
    ) -> Optional[np.ndarray]:
        """Extract a continuous window of audio samples starting at absolute start_offset.

        Args:
            window_samples: Length of window in samples.
            start_offset: Absolute cumulative sample index of window start.

        Returns:
            1D float32 numpy array of shape (window_samples,), or None if insufficient audio.
        """
        with self._lock:
            return self._get_window_locked(window_samples, start_offset)

    def available_windows(self, window_samples: int, hop_samples: int) -> int:
        """Return number of complete unread windows available starting from internal _read_offset."""
        with self._lock:
            oldest_available = max(0, self._total_samples_written - self.max_capacity_samples)
            if self._read_offset < oldest_available:
                self._read_offset = oldest_available

            if (self._read_offset + window_samples) > self._total_samples_written:
                return 0

            remaining = self._total_samples_written - (self._read_offset + window_samples)
            return 1 + (remaining // hop_samples)

    def read_window(self, window_samples: int, hop_samples: int) -> Optional[np.ndarray]:
        """Read the next unread window and advance the internal read pointer by hop_samples.

        Automatically advances _read_offset if circular overwrite occurred.
        """
        with self._lock:
            oldest_available = max(0, self._total_samples_written - self.max_capacity_samples)
            if self._read_offset < oldest_available:
                self._read_offset = oldest_available

            if (self._read_offset + window_samples) > self._total_samples_written:
                return None

            try:
                window = self._get_window_locked(window_samples, self._read_offset)
            except BufferUnderrunError:
                self._read_offset = oldest_available
                window = self._get_window_locked(window_samples, self._read_offset)

            if window is not None:
                self._read_offset += hop_samples

            return window

    def clear(self) -> None:
        """Reset buffer state and zero all internal storage."""
        with self._lock:
            self._buffer.fill(0.0)
            self._write_pos = 0
            self._total_samples_written = 0
            self._dropped_samples = 0
            self._read_offset = 0

    def reset(self) -> None:
        """Reset buffer state and zero all internal storage (alias for clear)."""
        self.clear()
