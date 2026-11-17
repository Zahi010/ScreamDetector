"""
Stage 8.9.31 - Enhanced Research Audio Ring Buffer with End-of-Stream Flush Policy.

Features:
- Circular zero-reallocation buffer for real-time streaming audio.
- Explicit end-of-stream `flush()` operation with right-padding.
- Configurable minimum-duration policy (e.g., min 200 ms = 3,200 samples).
- Explicit tracking of valid_samples vs padded_samples for every window.
- Protection against duplicate flush calls (idempotent).
- Ingestion rejection on flushed streams until explicit reset.
- Support for arbitrary window and hop durations (e.g. 375ms/100ms or 975ms/250ms).
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


@dataclass
class WindowFrame:
    """Metadata and PCM payload for an extracted analysis window."""
    window_idx: int
    start_sec: float
    end_sec: float
    pcm: np.ndarray
    valid_samples: int
    padded_samples: int
    is_end_of_stream: bool
    status: str  # COMPLETE_WINDOW, PADDED_END_OF_STREAM, etc.

    @property
    def padding_fraction(self) -> float:
        return float(self.padded_samples / len(self.pcm)) if len(self.pcm) > 0 else 0.0

    @property
    def valid_duration_sec(self) -> float:
        return float(self.valid_samples / 16000.0)


class ResearchAudioRingBuffer:
    """Bounded circular ring buffer with explicit end-of-stream flush and sample provenance."""

    def __init__(
        self,
        sample_rate: int = 16000,
        window_sec: float = 0.975,
        hop_sec: float = 0.250,
        capacity_sec: float = 6.0,
        min_valid_sec: float = 0.200,
    ):
        self.sample_rate = int(sample_rate)
        self.window_samples = int(round(window_sec * self.sample_rate))
        self.hop_samples = int(round(hop_sec * self.sample_rate))
        self.min_valid_samples = int(round(min_valid_sec * self.sample_rate))

        # Ensure capacity comfortably exceeds window + max burst chunk
        min_capacity = self.window_samples * 2
        requested_capacity = int(round(capacity_sec * self.sample_rate))
        self.capacity = max(min_capacity, requested_capacity)

        # Preallocated memory storage (circular)
        self._storage = np.zeros(self.capacity, dtype=np.float32)
        self._write_pos = 0   # Circular write index [0, capacity)
        self._read_pos = 0    # Circular read index
        self._available = 0   # Total unread valid samples in buffer

        # State lifecycle
        self.is_flushed = False
        self.flush_count = 0

        # Deterministic bookkeeping counters
        self.total_samples_ingested = 0
        self.total_samples_dropped = 0
        self.window_counter = 0
        self.dropped_windows = 0
        self.overrun_count = 0

        # Thread synchronization primitive
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Atomically reset the buffer and restore ingestion readiness."""
        with self._lock:
            self._storage.fill(0.0)
            self._write_pos = 0
            self._read_pos = 0
            self._available = 0
            self.is_flushed = False
            self.flush_count = 0
            self.total_samples_ingested = 0
            self.total_samples_dropped = 0
            self.window_counter = 0
            self.dropped_windows = 0
            self.overrun_count = 0

    def ingest(self, chunk: np.ndarray) -> List[WindowFrame]:
        """Ingest arbitrary-length PCM chunk and extract completed sliding windows.

        Raises:
            RuntimeError: If stream has already been flushed without a subsequent reset.
        """
        if chunk.ndim > 1:
            chunk = chunk.flatten()
        if chunk.dtype != np.float32:
            chunk = chunk.astype(np.float32)

        n_samples = len(chunk)
        if n_samples == 0:
            return []

        with self._lock:
            if self.is_flushed:
                raise RuntimeError(
                    "Cannot ingest into an already flushed stream. Call reset() before re-ingesting."
                )

            # If chunk exceeds capacity, ingest in chunks of hop_samples
            if n_samples > self.capacity:
                sub_size = self.hop_samples
                results = []
                for i in range(0, n_samples, sub_size):
                    sub = chunk[i : i + sub_size]
                    results.extend(self._ingest_unlocked(sub))
                return results

            return self._ingest_unlocked(chunk)

    def _ingest_unlocked(self, chunk: np.ndarray) -> List[WindowFrame]:
        n_samples = len(chunk)
        self.total_samples_ingested += n_samples

        # Handle buffer overrun if chunk exceeds remaining capacity
        if self._available + n_samples > self.capacity:
            overflow = (self._available + n_samples) - self.capacity
            self.overrun_count += 1
            self.total_samples_dropped += overflow

            dropped_win = int(np.ceil(overflow / self.hop_samples))
            self.dropped_windows += dropped_win

            # Advance read position to drop oldest unread samples
            self._read_pos = (self._read_pos + overflow) % self.capacity
            self._available -= overflow

        # Copy chunk into circular buffer
        first_copy = min(n_samples, self.capacity - self._write_pos)
        second_copy = n_samples - first_copy

        self._storage[self._write_pos : self._write_pos + first_copy] = chunk[:first_copy]
        if second_copy > 0:
            self._storage[0:second_copy] = chunk[first_copy:]

        self._write_pos = (self._write_pos + n_samples) % self.capacity
        self._available += n_samples

        extracted = []
        while self._available >= self.window_samples:
            win = np.empty(self.window_samples, dtype=np.float32)
            first_read = min(self.window_samples, self.capacity - self._read_pos)
            second_read = self.window_samples - first_read

            win[:first_read] = self._storage[self._read_pos : self._read_pos + first_read]
            if second_read > 0:
                win[first_read:] = self._storage[0:second_read]

            start_sec = (self.window_counter * self.hop_samples) / self.sample_rate
            end_sec = start_sec + (self.window_samples / self.sample_rate)

            frame = WindowFrame(
                window_idx=self.window_counter,
                start_sec=start_sec,
                end_sec=end_sec,
                pcm=win,
                valid_samples=self.window_samples,
                padded_samples=0,
                is_end_of_stream=False,
                status="COMPLETE_WINDOW",
            )
            extracted.append(frame)

            # Advance read index by one hop
            self._read_pos = (self._read_pos + self.hop_samples) % self.capacity
            self._available -= self.hop_samples
            self.window_counter += 1

        return extracted

    def flush(self, min_samples: Optional[int] = None) -> List[WindowFrame]:
        """Explicit end-of-stream flush to extract residual audio without loss.

        Args:
            min_samples: Minimum valid samples required to generate an end-of-stream
                         window. Defaults to self.min_valid_samples (e.g. 200 ms).

        Returns:
            List containing 0 or 1 WindowFrame representing the right-padded final window.
        """
        if min_samples is None:
            min_samples = self.min_valid_samples

        with self._lock:
            if self.is_flushed:
                # Idempotent flush: subsequent calls return empty list
                return []

            self.is_flushed = True
            self.flush_count += 1

            if self._available == 0:
                return []

            if self._available < min_samples:
                # Insufficient valid audio under minimum duration policy
                self._available = 0
                return []

            # Extract residual valid audio and right-pad to window_samples
            valid_count = self._available
            pad_count = max(0, self.window_samples - valid_count)

            win = np.zeros(self.window_samples, dtype=np.float32)
            first_read = min(valid_count, self.capacity - self._read_pos)
            second_read = valid_count - first_read

            win[:first_read] = self._storage[self._read_pos : self._read_pos + first_read]
            if second_read > 0:
                win[first_read:valid_count] = self._storage[0:second_read]

            # Clear buffer available count
            self._available = 0
            self._read_pos = (self._read_pos + valid_count) % self.capacity

            start_sec = (self.window_counter * self.hop_samples) / self.sample_rate
            end_sec = start_sec + (self.window_samples / self.sample_rate)

            frame = WindowFrame(
                window_idx=self.window_counter,
                start_sec=start_sec,
                end_sec=end_sec,
                pcm=win,
                valid_samples=valid_count,
                padded_samples=pad_count,
                is_end_of_stream=True,
                status="PADDED_END_OF_STREAM_WINDOW" if pad_count > 0 else "COMPLETE_WINDOW",
            )
            self.window_counter += 1
            return [frame]

    def get_metrics(self) -> Dict[str, Any]:
        """Diagnostic state inspection."""
        with self._lock:
            return {
                "capacity_samples": self.capacity,
                "window_samples": self.window_samples,
                "hop_samples": self.hop_samples,
                "min_valid_samples": self.min_valid_samples,
                "currently_buffered_samples": self._available,
                "total_samples_ingested": self.total_samples_ingested,
                "total_samples_dropped": self.total_samples_dropped,
                "total_windows_extracted": self.window_counter,
                "is_flushed": self.is_flushed,
                "flush_count": self.flush_count,
                "overrun_count": self.overrun_count,
            }
