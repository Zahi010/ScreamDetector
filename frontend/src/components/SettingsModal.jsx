import { useState, useEffect } from 'react'

export function SettingsModal({
  isOpen,
  onClose,
  detectorStatus,
  onUpdateConfig,
  onStartDetector,
  onStopDetector,
}) {
  const [threshold, setThreshold] = useState(0.35)
  const [cooldown, setCooldown] = useState(3.0)
  const [minWindows, setMinWindows] = useState(2)
  const [smoothingAlpha, setSmoothingAlpha] = useState(0.6)
  const [devices, setDevices] = useState([])
  const [selectedDevice, setSelectedDevice] = useState('')
  const [feedback, setFeedback] = useState(null) // { type: 'success' | 'error', message: string }
  const [confirmStop, setConfirmStop] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Populate initial values from detectorStatus
  useEffect(() => {
    if (detectorStatus) {
      if (detectorStatus.threshold !== undefined) setThreshold(detectorStatus.threshold)
      if (detectorStatus.cooldown_seconds !== undefined) setCooldown(detectorStatus.cooldown_seconds)
      if (detectorStatus.min_consecutive_positive !== undefined) setMinWindows(detectorStatus.min_consecutive_positive)
      if (detectorStatus.smoothing_alpha !== undefined) setSmoothingAlpha(detectorStatus.smoothing_alpha)
      if (detectorStatus.selected_device_index !== undefined && detectorStatus.selected_device_index !== null) {
        setSelectedDevice(detectorStatus.selected_device_index.toString())
      }
    }
  }, [detectorStatus])

  // Fetch audio input devices
  useEffect(() => {
    if (isOpen) {
      fetch('/api/devices')
        .then((res) => res.json())
        .then((data) => setDevices(data.devices || []))
        .catch((err) => console.warn('Failed to load audio devices:', err))
    }
  }, [isOpen])

  if (!isOpen) return null

  const handleSaveConfig = async () => {
    setIsSaving(true)
    setFeedback(null)
    try {
      const res = await onUpdateConfig({
        threshold: parseFloat(threshold),
        cooldown_seconds: parseFloat(cooldown),
        min_consecutive_positive: parseInt(minWindows, 10),
        smoothing_alpha: parseFloat(smoothingAlpha),
      })
      if (res && res.success) {
        setFeedback({ type: 'success', message: 'Detection settings saved successfully.' })
      } else {
        setFeedback({ type: 'error', message: res?.error || 'Failed to update settings.' })
      }
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Validation error.' })
    } finally {
      setIsSaving(false)
    }
  }

  const handleResetDefault = () => {
    setThreshold(0.35)
    setCooldown(3.0)
    setMinWindows(2)
    setSmoothingAlpha(0.6)
    setFeedback({ type: 'success', message: 'Reset to Stage 5 baseline parameters (Threshold: 0.35).' })
  }

  const handleToggleDetector = async () => {
    if (detectorStatus.is_running) {
      if (!confirmStop) {
        setConfirmStop(true)
        return
      }
      setConfirmStop(false)
      await onStopDetector()
    } else {
      const devIdx = selectedDevice !== '' ? parseInt(selectedDevice, 10) : null
      await onStartDetector(devIdx)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#FFFFFF' }}>
            Detector Settings & Audio Control
          </h3>
          <button className="btn-secondary" onClick={onClose} style={{ padding: '0.25rem 0.6rem' }}>
            ✕
          </button>
        </div>

        {feedback && (
          <div
            style={{
              padding: '0.65rem 0.85rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              background: feedback.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              border: `1px solid ${feedback.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
              color: feedback.type === 'success' ? '#34D399' : '#FCA5A5',
            }}
          >
            {feedback.message}
          </div>
        )}

        {/* Live Audio Stream Control */}
        <div className="form-group" style={{ background: 'var(--bg-deep)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div className="form-label">Live Microphone Capture</div>
              <div className="form-help">
                State: <strong>{detectorStatus.is_running ? 'RUNNING' : 'STOPPED'}</strong>
                {detectorStatus.mic_status && ` (${detectorStatus.mic_status})`}
              </div>
            </div>

            {confirmStop ? (
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  className="btn-danger"
                  onClick={handleToggleDetector}
                  title="Confirm stopping detection stream"
                >
                  Confirm Stop?
                </button>
                <button
                  className="btn-secondary"
                  onClick={() => setConfirmStop(false)}
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                className={detectorStatus.is_running ? 'btn-danger' : 'btn-primary'}
                onClick={handleToggleDetector}
              >
                {detectorStatus.is_running ? 'Stop Detector' : 'Start Live Detector'}
              </button>
            )}
          </div>

          <div style={{ marginTop: '0.75rem' }}>
            <label className="form-label" style={{ fontSize: '0.75rem' }}>Select Microphone Device:</label>
            <select
              className="form-select"
              style={{ width: '100%', marginTop: '0.25rem' }}
              value={selectedDevice}
              onChange={(e) => setSelectedDevice(e.target.value)}
              disabled={detectorStatus.is_running}
            >
              <option value="">Default System Microphone</option>
              {devices.map((d) => (
                <option key={d.device_index} value={d.device_index}>
                  [{d.device_index}] {d.name} ({d.host_api})
                </option>
              ))}
            </select>
            {detectorStatus.is_running && (
              <div className="form-help" style={{ marginTop: '0.25rem' }}>
                * Stop detector to switch audio device.
              </div>
            )}
          </div>
        </div>

        {/* Threshold Slider */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label className="form-label">Decision Threshold</label>
            <span className="mono" style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>
              {parseFloat(threshold).toFixed(2)}
            </span>
          </div>
          <input
            type="range"
            min="0.05"
            max="0.95"
            step="0.01"
            className="form-slider"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
          />
          <div className="form-help">
            Stage 5 Validation Baseline: 0.35 (Lower = higher recall; Higher = lower false alarms).
          </div>
        </div>

        {/* Cooldown Seconds */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label className="form-label">Alert Cooldown (Seconds)</label>
            <span className="mono">{parseFloat(cooldown).toFixed(1)}s</span>
          </div>
          <input
            type="number"
            min="0.5"
            max="30.0"
            step="0.5"
            className="form-input"
            value={cooldown}
            onChange={(e) => setCooldown(e.target.value)}
          />
          <div className="form-help">
            Suppresses duplicate notifications for the same ongoing vocalization event.
          </div>
        </div>

        {/* Min Consecutive Windows */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label className="form-label">Min Consecutive Positive Windows</label>
            <span className="mono">{minWindows}</span>
          </div>
          <input
            type="number"
            min="1"
            max="10"
            className="form-input"
            value={minWindows}
            onChange={(e) => setMinWindows(e.target.value)}
          />
          <div className="form-help">
            Temporal smoothing: requires persistent distress energy before triggering alarm.
          </div>
        </div>

        {/* Smoothing Alpha */}
        <div className="form-group">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <label className="form-label">Smoothing Alpha (EMA Factor)</label>
            <span className="mono">{parseFloat(smoothingAlpha).toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.05"
            className="form-slider"
            value={smoothingAlpha}
            onChange={(e) => setSmoothingAlpha(e.target.value)}
          />
          <div className="form-help">
            1.0 = raw score, lower = heavier temporal smoothing.
          </div>
        </div>

        <div className="modal-actions">
          <button className="btn-secondary" onClick={handleResetDefault}>
            Reset to Default (0.35)
          </button>
          <button
            className="btn-primary"
            onClick={handleSaveConfig}
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}
