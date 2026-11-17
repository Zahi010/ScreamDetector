"""Local Alert Dispatcher and Subscriber Interface (Stage 7).

Manages alert notifications for detected scream events:
- Formats local terminal console alert banners with clear advisory disclaimers.
- Maintains a thread-safe event queue for future consumers (FastAPI WebSockets / UI).
- Dispatches notifications to registered Python callbacks.
- Strictly adheres to local processing: no audio or external network dispatch.
"""

from __future__ import annotations

import logging
import queue
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("alert_dispatcher")


class AlertDispatcher:
    """Dispatches detection alert notifications to console and registered subscribers."""

    def __init__(
        self,
        enable_console_alerts: bool = True,
        max_queue_size: int = 100,
    ):
        """Initialize alert dispatcher.

        Args:
            enable_console_alerts: Whether to print structured alert banners to terminal.
            max_queue_size: Capacity of in-memory thread-safe event queue.
        """
        self.enable_console_alerts = enable_console_alerts
        self.event_queue: queue.Queue[Dict[str, Any]] = queue.Queue(maxsize=max_queue_size)
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback function to receive alert event notifications."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Remove a previously registered callback function."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def dispatch_alert(self, event_data: Dict[str, Any]) -> None:
        """Dispatch an alert event to console, queue, and registered subscribers."""
        event_id = event_data.get("event_id", "Unknown")
        peak_p = event_data.get("peak_probability", 0.0)
        stream_t = event_data.get("start_stream_time", 0.0)
        thresh = event_data.get("threshold", 0.35)
        duration = event_data.get("duration_seconds", 0.0)
        priors = event_data.get("top_priors", [])

        # 1. Console Banner Notification
        if self.enable_console_alerts:
            self._print_console_alert(
                event_id=event_id,
                stream_time=stream_t,
                peak_prob=peak_p,
                threshold=thresh,
                duration=duration,
                priors=priors,
            )

        # 2. Put into thread-safe Queue for future consumers (FastAPI / WebSockets)
        try:
            self.event_queue.put_nowait(event_data)
        except queue.Full:
            # Drop oldest to prevent stall
            try:
                self.event_queue.get_nowait()
                self.event_queue.put_nowait(event_data)
            except Exception:
                pass

        # 3. Notify Python Subscribers
        for sub in list(self._subscribers):
            try:
                sub(event_data)
            except Exception as e:
                logger.error(f"Error in alert subscriber {sub}: {e}", exc_info=True)

    def _print_console_alert(
        self,
        event_id: str,
        stream_time: float,
        peak_prob: float,
        threshold: float,
        duration: float,
        priors: List[Dict[str, Any]],
    ) -> None:
        """Render high-visibility terminal alert banner with safety advisory."""
        priors_str = ", ".join([f"{p['class_name']} ({p['score']:.2f})" for p in priors[:2]]) if priors else "None"
        banner = [
            "\n" + "=" * 80,
            ">>> [LIVE ALERT: POSSIBLE SCREAM EVENT DETECTED] <<<",
            "=" * 80,
            f"  Event ID:           {event_id}",
            f"  Stream Offset:      {stream_time:.2f}s (Duration: ~{duration:.2f}s)",
            f"  Scream Probability: {peak_prob:.4f} ({peak_prob * 100:.1f}%) [Threshold: {threshold:.2f}]",
            f"  YAMNet Audio Priors:{priors_str}",
            "  Advisory:           POSSIBLE SCREAM EVENT — REQUIRES HUMAN AUDITORY VERIFICATION.",
            "                      (This automated detection does not constitute a confirmed emergency).",
            "=" * 80 + "\n",
        ]
        print("\n".join(banner))
