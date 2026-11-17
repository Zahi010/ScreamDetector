import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * Custom React hook managing real-time WebSocket streaming & REST controls for Multi-Model Live Lab.
 */
export function useMultiModelSocket() {
  const [connectionStatus, setConnectionStatus] = useState('disconnected') // 'connected' | 'reconnecting' | 'disconnected'
  const [labStatus, setLabStatus] = useState({
    is_running: false,
    mic_status: 'stopped',
    mic_error: null,
    selected_device_index: null,
    active_session_id: null,
    window_counter: 0,
    dropped_windows_total: 0,
    buffer_stats: {
      total_samples_written: 0,
      buffered_samples: 0,
      buffered_seconds: 0,
      dropped_samples: 0,
      capacity_seconds: 15.0,
    },
    enabled_models: {},
    uptime_seconds: 0,
  })

  const [models, setModels] = useState([])
  const [latestWindow, setLatestWindow] = useState(null)
  const [windowHistory, setWindowHistory] = useState([])
  const [candidateEvents, setCandidateEvents] = useState([])
  const [devices, setDevices] = useState([])
  const [activeSession, setActiveSession] = useState(null)

  const socketRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const backoffRef = useRef(1000)
  const isUnmountedRef = useRef(false)

  // Reconcile status and models via REST API
  const reconcile = useCallback(async () => {
    try {
      const [modelsRes, statusRes] = await Promise.all([
        fetch('/api/experimental/live/models'),
        fetch('/api/experimental/live/status'),
      ])

      if (modelsRes.ok) {
        const mData = await modelsRes.json()
        setModels(mData.models || [])
      }

      if (statusRes.ok) {
        const sData = await statusRes.json()
        setLabStatus(sData.lab_status || {})
        setDevices(sData.audio_devices || [])
      }

      const eventsRes = await fetch('/api/experimental/live/events?limit=30')
      if (eventsRes.ok) {
        const eData = await eventsRes.json()
        setCandidateEvents(eData.events || [])
      }
    } catch (err) {
      console.warn('Failed to reconcile multi-model lab state:', err)
    }
  }, [])

  const connect = useCallback(() => {
    if (isUnmountedRef.current) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/experimental/multi-model`

    console.info(`[MultiModelSocket] Connecting to ${wsUrl}...`)
    const ws = new WebSocket(wsUrl)
    socketRef.current = ws

    ws.onopen = () => {
      if (isUnmountedRef.current) {
        ws.close()
        return
      }
      console.info('[MultiModelSocket] Connected successfully.')
      setConnectionStatus('connected')
      backoffRef.current = 1000
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)

        if (msg.type === 'multimodel_snapshot') {
          if (msg.status) setLabStatus(msg.status)
          if (msg.models) setModels(msg.models)
          if (msg.recent_windows) setWindowHistory(msg.recent_windows)
          if (msg.recent_events) setCandidateEvents(msg.recent_events)
        } else if (msg.type === 'multimodel_window_result') {
          const winData = msg.data
          setLatestWindow(winData)
          setWindowHistory((prev) => {
            const next = [winData, ...prev.slice(0, 49)]
            return next
          })
          if (winData.dropped_windows_total !== undefined) {
            setLabStatus((prev) => ({
              ...prev,
              window_counter: winData.window_index,
              dropped_windows_total: winData.dropped_windows_total,
            }))
          }
        } else if (msg.type === 'multimodel_status_changed') {
          if (msg.status) {
            setLabStatus(msg.status)
            if (!msg.status.is_running) {
              setLatestWindow(null)
            }
          }
        } else if (msg.type === 'multimodel_event_resolved') {
          if (msg.event) {
            setCandidateEvents((prev) => [msg.event, ...prev.slice(0, 49)])
          }
        } else if (msg.type === 'model_config_updated') {
          setLabStatus((prev) => ({
            ...prev,
            enabled_models: msg.enabled_models || prev.enabled_models,
          }))
          setModels((prev) =>
            prev.map((m) =>
              m.model_id === msg.model_id ? { ...m, is_enabled: msg.enabled } : m
            )
          )
        }
      } catch (err) {
        console.warn('[MultiModelSocket] Message parse error:', err)
      }
    }

    ws.onerror = (err) => {
      console.warn('[MultiModelSocket] Error:', err)
    }

    ws.onclose = () => {
      if (isUnmountedRef.current) return
      console.info('[MultiModelSocket] Closed. Attempting reconnect...')
      setConnectionStatus('reconnecting')
      const delay = Math.min(backoffRef.current, 10000)
      backoffRef.current = Math.min(backoffRef.current * 1.5, 10000)
      reconnectTimeoutRef.current = setTimeout(connect, delay)
    }
  }, [])

  useEffect(() => {
    isUnmountedRef.current = false
    reconcile()
    connect()

    const pingTimer = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ command: 'ping' }))
      }
    }, 15000)

    return () => {
      isUnmountedRef.current = true
      clearInterval(pingTimer)
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      if (socketRef.current) {
        socketRef.current.onclose = null
        socketRef.current.close()
      }
    }
  }, [connect, reconcile])

  // Lab Actions
  const startLab = async (deviceIndex = null, sessionNotes = '') => {
    try {
      const res = await fetch('/api/experimental/live/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_index: deviceIndex, session_notes: sessionNotes }),
      })
      if (!res.ok) {
        let errDetail = `HTTP ${res.status}`
        try {
          const errJson = await res.json()
          if (errJson?.detail) errDetail = errJson.detail
        } catch {
          // ignore json parse error
        }
        throw new Error(errDetail)
      }
      await reconcile()
      return await res.json()
    } catch (err) {
      console.error('Failed to start live lab:', err)
      throw err
    }
  }

  const stopLab = async () => {
    try {
      const res = await fetch('/api/experimental/live/stop', {
        method: 'POST',
      })
      if (!res.ok) {
        let errDetail = `HTTP ${res.status}`
        try {
          const errJson = await res.json()
          if (errJson?.detail) errDetail = errJson.detail
        } catch {
          // ignore json parse error
        }
        throw new Error(errDetail)
      }
      setLatestWindow(null)
      await reconcile()
      return await res.json()
    } catch (err) {
      console.error('Failed to stop live lab:', err)
      throw err
    }
  }

  const toggleAcousticGate = async (enabled, rmsThreshold = 0.0035, peakThreshold = 0.010) => {
    try {
      const res = await fetch('/api/experimental/live/acoustic-gate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          enabled,
          rms_threshold: rmsThreshold,
          peak_threshold: peakThreshold,
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      await reconcile()
      return data
    } catch (err) {
      console.error('Failed to toggle acoustic gate:', err)
      throw err
    }
  }

  const toggleModel = async (modelId, enabled) => {
    try {
      const res = await fetch('/api/experimental/live/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId, enabled }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setModels((prev) =>
        prev.map((m) => (m.model_id === modelId ? { ...m, is_enabled: enabled } : m))
      )
      return data
    } catch (err) {
      console.error('Failed to toggle model:', err)
      throw err
    }
  }

  const simulateAudio = async (signalType = 'scream_burst', duration = 1.5, amplitude = 0.5) => {
    try {
      const res = await fetch('/api/experimental/live/simulate-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          signal_type: signalType,
          duration_seconds: duration,
          amplitude: amplitude,
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      return await res.json()
    } catch (err) {
      console.error('Failed to simulate audio:', err)
      throw err
    }
  }

  const submitReview = async (reviewPayload) => {
    try {
      const res = await fetch('/api/experimental/live/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewPayload),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      await reconcile()
      return data
    } catch (err) {
      console.error('Failed to submit review:', err)
      throw err
    }
  }

  const fetchSessionDetails = async (sessionId) => {
    try {
      const res = await fetch(`/api/experimental/live/session/${sessionId}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setActiveSession(data.session)
      return data.session
    } catch (err) {
      console.error('Failed to fetch session details:', err)
      return null
    }
  }

  return {
    connectionStatus,
    labStatus,
    models,
    latestWindow,
    windowHistory,
    candidateEvents,
    devices,
    activeSession,
    startLab,
    stopLab,
    toggleModel,
    toggleAcousticGate,
    simulateAudio,
    submitReview,
    fetchSessionDetails,
    reconcile,
  }
}
