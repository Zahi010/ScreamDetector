import { useState } from 'react'

export function AlertBanner({ alert, onAcknowledge, onDismiss }) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [operatorNote, setOperatorNote] = useState('')
  const [showNoteInput, setShowNoteInput] = useState(false)

  if (!alert) return null

  const handleAcknowledge = async () => {
    setIsSubmitting(true)
    try {
      await onAcknowledge(alert.event_id, operatorNote || 'Operator verified on dashboard')
      setShowNoteInput(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  const peakProbPercent = ((alert.peak_probability || 0) * 100).toFixed(1)
  const durationSec = (alert.duration_seconds || 0).toFixed(2)

  return (
    <div className="alert-banner-container">
      <div className="alert-banner">
        <div className="alert-content">
          <div className="alert-headline-row">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
            <span className="alert-title">POSSIBLE SCREAM EVENT DETECTED</span>
            <span className="score-badge score-high">{peakProbPercent}% Confidence</span>
          </div>

          <div className="alert-disclaimer">
            <strong>Security Advisory:</strong> Automated detection indicates acoustic distress features. Requires human auditory verification. Does not constitute a confirmed emergency.
          </div>

          <div className="alert-details">
            <span><strong>Event ID:</strong> {alert.event_id}</span>
            <span><strong>Duration:</strong> ~{durationSec}s</span>
            <span><strong>Windows:</strong> {alert.window_count || alert.positive_window_count || 1}</span>
            {alert.start_wall_time_iso && (
              <span><strong>Time:</strong> {new Date(alert.start_wall_time_iso).toLocaleTimeString()}</span>
            )}
          </div>

          {showNoteInput && (
            <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <input
                type="text"
                className="form-input"
                placeholder="Optional operator verification note..."
                value={operatorNote}
                onChange={(e) => setOperatorNote(e.target.value)}
                style={{ flex: 1, minWidth: '240px' }}
              />
              <button
                className="btn-primary"
                onClick={handleAcknowledge}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Saving...' : 'Submit Acknowledgment'}
              </button>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {!showNoteInput && !alert.acknowledged && (
            <button
              className="alert-action-btn"
              onClick={() => setShowNoteInput(true)}
              title="Acknowledge and log operator verification"
            >
              Acknowledge Alert
            </button>
          )}

          {alert.acknowledged && (
            <span className="status-badge badge-connected" style={{ padding: '0.5rem 0.85rem' }}>
              ✓ Acknowledged
            </span>
          )}

          <button
            className="btn-secondary"
            onClick={onDismiss}
            title="Dismiss notification banner"
            style={{ padding: '0.55rem' }}
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}
