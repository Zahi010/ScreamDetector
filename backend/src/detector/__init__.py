"""Streaming audio detection, rolling-window aggregation, and event state management."""

from src.detector.audio_buffer import BufferUnderrunError, RollingAudioBuffer
from src.detector.event_logger import DetectionEventLogger
from src.detector.mic_capture import (
    AudioDeviceError,
    MicrophoneCapture,
    list_audio_input_devices,
)
from src.detector.state_machine import (
    DetectorState,
    EventStateMachine,
    ScreamEvent,
    WindowInferenceResult,
)
from src.detector.stream_detector import StreamDetector

from src.detector.service import (
    DetectorService,
    get_detector_service,
    reset_detector_service,
)

__all__ = [
    "RollingAudioBuffer",
    "BufferUnderrunError",
    "EventStateMachine",
    "DetectorState",
    "ScreamEvent",
    "WindowInferenceResult",
    "DetectionEventLogger",
    "StreamDetector",
    "MicrophoneCapture",
    "AudioDeviceError",
    "list_audio_input_devices",
    "DetectorService",
    "get_detector_service",
    "reset_detector_service",
]
