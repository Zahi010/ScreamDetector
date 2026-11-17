import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * Custom React hook managing real-time WebSocket connection and status reconciliation.
 */
export function useDetectorSocket() {
  const [connectionStatus, setConnectionStatus] = useState('disconnected') // 'connected' | 'reconnecting' | 'disconnected'
  const [detectorStatus, setDetectorStatus] = useState({
    is_running: false,
    state: 'IDLE',
    mic_status: 'stopped',
    mic_error: null,
    uptime_seconds: 0,
    threshold: 0.35,
    cooldown_seconds: 3.0,
    min_consecutive_positive: 2,
    smoothing_alpha: 0.6,
    active_event: null,
    available_devices: 0,
  })
  const [metrics, setMetrics] = useState({
    windows_processed: 0,
    total_audio_seconds: 0,
    total_alerts_emitted: 0,
    total_alerts_suppressed: 0,
    inference_errors: 0,
    dropped_samples: 0,
    latency_metrics_ms: { mean: 0, min: 0, max: 0, p95: 0, samples_timed: 0 },
    hop_duration_ms: 487.5,
    realtime_factor: 0,
    session_uptime_seconds: 0,
    acknowledged_events_count: 0,
  })
  const [windowTelemetry, setWindowTelemetry] = useState({
    window_index: 0,
    stream_time_seconds: 0,
    raw_probability: 0,
    smoothed_probability: 0,
    is_positive: false,
    threshold: 0.35,
    state: 'IDLE',
    audio_rms: 0,
    latency_ms: 0,
    priors: [],
  })
  const [activeAlert, setActiveAlert] = useState(null)

  const socketRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const backoffRef = useRef(1000)
  const isUnmountedRef = useRef(false)

  // Reconcile status and metrics via HTTP REST API
  const reconcileState = useCallback(async () => {
    try {
      const [statusRes, metricsRes] = await Promise.all([
        fetch('/api/status'),
        fetch('/api/metrics'),
      ])
      if (statusRes.ok) {
        const sData = await statusRes.json()
        setDetectorStatus((prev) => ({ ...prev, ...sData }))
        if (sData.active_event && sData.state === 'ALERT_ACTIVE') {
          setActiveAlert(sData.active_event)
        }
      }
      if (metricsRes.ok) {
        const mData = await metricsRes.json()
        setMetrics(mData)
      }
    } catch (err) {
      console.warn('Failed to reconcile status via REST API:', err)
    }
  }, [])

  const connect = useCallback(() => {
    if (isUnmountedRef.current) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/events`

    setConnectionStatus((prev) => (prev === 'disconnected' ? 'reconnecting' : prev))
    const ws = new WebSocket(wsUrl)
    socketRef.current = ws

    ws.onopen = () => {
      if (isUnmountedRef.current) return
      setConnectionStatus('connected')
      backoffRef.current = 1000 // Reset backoff on success
      reconcileState() // Reconcile any state missed during reconnect
    }

    ws.onmessage = (event) => {
      if (isUnmountedRef.current) return
      try {
        const data = jsonParseSafe(event.data)
        if (!data) return

        switch (data.type) {
          case 'initial_snapshot':
            if (data.status) setDetectorStatus(data.status)
            if (data.metrics) setMetrics(data.metrics)
            if (data.active_event) setActiveAlert(data.active_event)
            break

          case 'detector_status_changed':
            if (data.status) setDetectorStatus(data.status)
            break

          case 'state_changed':
            setDetectorStatus((prev) => ({
              ...prev,
              state: data.new_state,
              active_event: data.event,
            }))
            if (data.new_state === 'ALERT_ACTIVE' && data.event) {
              setActiveAlert(data.event)
            }
            break

          case 'window_update':
            setWindowTelemetry({
              window_index: data.window_index,
              stream_time_seconds: data.stream_time_seconds,
              raw_probability: data.raw_probability,
              smoothed_probability: data.smoothed_probability,
              is_positive: data.is_positive,
              threshold: data.threshold,
              state: data.state,
              audio_rms: data.audio_rms,
              latency_ms: data.latency_ms,
              priors: data.priors || [],
            })
            setDetectorStatus((prev) => ({
              ...prev,
              state: data.state,
            }))
            break

          case 'alert_triggered':
            setActiveAlert(data.event)
            setDetectorStatus((prev) => ({
              ...prev,
              state: 'ALERT_ACTIVE',
              active_event: data.event,
            }))
            break

          case 'event_concluded':
            setDetectorStatus((prev) => ({
              ...prev,
              active_event: null,
            }))
            break

          case 'event_acknowledged':
            setActiveAlert((prev) =>
              prev && prev.event_id === data.acknowledgment?.event_id
                ? { ...prev, acknowledged: true, ...data.acknowledgment }
                : prev
            )
            break

          case 'metrics_update':
            if (data.metrics) setMetrics(data.metrics)
            break

          case 'config_updated':
            if (data.config) {
              setDetectorStatus((prev) => ({ ...prev, ...data.config }))
            }
            break

          default:
            break
        }
      } catch (e) {
        console.error('Error processing WebSocket message:', e)
      }
    }

    ws.onclose = () => {
      if (isUnmountedRef.current) return
      setConnectionStatus('reconnecting')
      const delay = Math.min(backoffRef.current, 10000)
      backoffRef.current = delay * 1.5

      reconnectTimeoutRef.current = setTimeout(() => {
        connect()
      }, delay)
    }

    ws.onerror = (err) => {
      console.warn('WebSocket encountered error:', err)
      ws.close()
    }
  }, [reconcileState])

  useEffect(() => {
    isUnmountedRef.current = false
    connect()

    return () => {
      isUnmountedRef.current = true
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (socketRef.current) {
        socketRef.current.close()
      }
    }
  }, [connect])

  const dismissAlert = useCallback(() => {
    setActiveAlert(null)
  }, [])

  return {
    connectionStatus,
    detectorStatus,
    metrics,
    windowTelemetry,
    activeAlert,
    dismissAlert,
    reconcileState,
  }
}

function jsonParseSafe(str) {
  try {
    return JSON.parse(str)
  } catch {
    return null
  }
}
