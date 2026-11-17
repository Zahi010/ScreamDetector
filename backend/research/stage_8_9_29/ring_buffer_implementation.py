"""Stage 8.9.29 — Bounded High-Throughput Ring Buffer for Continuous Streaming Audio.

Implements a thread-safe, circular memory ring buffer for real-time streaming audio ingestion:
- Sample rate: 16,000 Hz
- Channels: Mono (float32)
- Window duration: 0.975 seconds (15,600 samples)
- Hop duration: 0.250 seconds (4,000 samples)
- Fully circular indexing with zero memory re-allocation during streaming
- Exact sample boundary alignment and timestamp synchronization
- Graceful overrun / backpressure tracking without silent data corruption
- Support for arbitrary, irregular chunk sizes (160, 320, 800, 1600, 4096, random)
"""

from __future__ import annotations

import threading
from typing import List, Tuple, Optional, Dict, Any
import numpy as np


class AudioRingBuffer:
    """Bounded, high-throughput circular ring buffer for real-time audio streaming."""

    def __init__(
        self,
        sample_rate: int = 16000,
        window_sec: float = 0.975,
        hop_sec: float = 0.250,
        capacity_sec: float = 6.0,  # Bounded circular capacity (e.g., 6.0s = 96,000 samples)
    ):
        self.sample_rate = int(sample_rate)
        self.window_samples = int(round(window_sec * self.sample_rate))  # 15,600
        self.hop_samples = int(round(hop_sec * self.sample_rate))        # 4,000
        
        # Buffer capacity must comfortably exceed window + max burst chunk
        min_capacity = self.window_samples * 2
        requested_capacity = int(round(capacity_sec * self.sample_rate))
        self.capacity = max(min_capacity, requested_capacity)

        # Preallocated memory storage (strictly bounded, zero reallocation)
        self._storage = np.zeros(self.capacity, dtype=np.float32)
        self._write_pos = 0   # Circular write index [0, capacity)
        self._read_pos = 0    # Circular read index (earliest available sample)
        self._available = 0   # Total unread samples currently in buffer

        # Deterministic bookkeeping counters
        self.total_samples_ingested = 0
        self.total_samples_dropped = 0
        self.window_counter = 0
        self.dropped_windows = 0
        self.overrun_count = 0

        # Thread synchronization primitive for safe multi-thread ingestion
        self._lock = threading.Lock()

    def reset(self) -> None:
        """Atomically reset the ring buffer state and clear all samples."""
        with self._lock:
            self._storage.fill(0.0)
            self._write_pos = 0
            self._read_pos = 0
            self._available = 0
            self.total_samples_ingested = 0
            self.total_samples_dropped = 0
            self.window_counter = 0
            self.dropped_windows = 0
            self.overrun_count = 0

    def ingest(self, chunk: np.ndarray) -> List[Tuple[int, float, float, np.ndarray]]:
        """Ingest an arbitrary-length PCM chunk and extract all newly completed windows.
        
        Returns:
            List of tuples: (window_idx, start_sec, end_sec, window_array)
        """
        if chunk.ndim > 1:
            chunk = chunk.flatten()
        if chunk.dtype != np.float32:
            chunk = chunk.astype(np.float32)

        n_samples = len(chunk)
        if n_samples == 0:
            return []

        # If a single chunk exceeds capacity, stream it through in bounded sub-chunks
        if n_samples > self.capacity:
            sub_size = self.hop_samples
            results = []
            for i in range(0, n_samples, sub_size):
                results.extend(self.ingest(chunk[i : i + sub_size]))
            return results

        extracted_windows = []

        with self._lock:
            self.total_samples_ingested += n_samples

            # Handle buffer overrun if chunk exceeds remaining capacity
            if self._available + n_samples > self.capacity:
                overflow = (self._available + n_samples) - self.capacity
                self.overrun_count += 1
                self.total_samples_dropped += overflow

                # Calculate lost windows due to forced skip
                dropped_win = int(np.ceil(overflow / self.hop_samples))
                self.dropped_windows += dropped_win

                # Advance read position to drop oldest unread samples
                self._read_pos = (self._read_pos + overflow) % self.capacity
                self._available -= overflow

            # Copy chunk into circular buffer (handling circular wrap-around)
            first_copy = min(n_samples, self.capacity - self._write_pos)
            second_copy = n_samples - first_copy

            self._storage[self._write_pos : self._write_pos + first_copy] = chunk[:first_copy]
            if second_copy > 0:
                self._storage[0:second_copy] = chunk[first_copy:]

            self._write_pos = (self._write_pos + n_samples) % self.capacity
            self._available += n_samples

            # Extract all complete sliding windows
            while self._available >= self.window_samples:
                # Extract contiguous window with wrap-around support
                win = np.empty(self.window_samples, dtype=np.float32)
                first_read = min(self.window_samples, self.capacity - self._read_pos)
                second_read = self.window_samples - first_read

                win[:first_read] = self._storage[self._read_pos : self._read_pos + first_read]
                if second_read > 0:
                    win[first_read:] = self._storage[0:second_read]

                start_sec = (self.window_counter * self.hop_samples) / self.sample_rate
                end_sec = start_sec + (self.window_samples / self.sample_rate)

                extracted_windows.append((self.window_counter, start_sec, end_sec, win))

                # Advance read index by one hop
                self._read_pos = (self._read_pos + self.hop_samples) % self.capacity
                self._available -= self.hop_samples
                self.window_counter += 1

        return extracted_windows

    def get_metrics(self) -> Dict[str, Any]:
        """Return diagnostic metrics describing buffer status and memory usage."""
        with self._lock:
            return {
                "capacity_samples": self.capacity,
                "capacity_sec": round(self.capacity / self.sample_rate, 3),
                "allocated_bytes": self._storage.nbytes,
                "currently_buffered_samples": self._available,
                "total_samples_ingested": self.total_samples_ingested,
                "total_samples_dropped": self.total_samples_dropped,
                "total_windows_extracted": self.window_counter,
                "dropped_windows": self.dropped_windows,
                "overrun_count": self.overrun_count,
            }
