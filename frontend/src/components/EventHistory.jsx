import { useState, useEffect, useCallback } from 'react'

export function EventHistory({ onAcknowledgeEvent }) {
  const [events, setEvents] = useState([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [filter, setFilter] = useState('all') // 'all' | 'alerts' | 'unack'
  const [error, setError] = useState(null)

  const fetchEvents = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/events?limit=50&offset=0')
      if (!res.ok) throw new Error(`HTTP error ${res.status}`)
      const data = await res.json()
      setEvents(data.events || [])
      setTotal(data.total || 0)
    } catch (err) {
      console.error('Failed to load event history:', err)
      setError('Unable to load event history from server.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchEvents()
  }, [fetchEvents])

  const filteredEvents = events.filter((e) => {
    if (filter === 'alerts') return e.alert_emitted === true
    if (filter === 'unack') return e.alert_emitted === true && !e.acknowledged
    return true
  })

  return (
    <div className="card events-section" style={{ gridColumn: '1 / -1' }}>
      <div className="card-header">
        <h2 className="card-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
          Persisted Acoustic Event History
        </h2>

        <div className="table-toolbar">
          <div className="filter-tabs">
            <button
              className={`tab-btn ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All Events ({total})
            </button>
            <button
              className={`tab-btn ${filter === 'alerts' ? 'active' : ''}`}
              onClick={() => setFilter('alerts')}
            >
              Alerts Only
            </button>
            <button
              className={`tab-btn ${filter === 'unack' ? 'active' : ''}`}
              onClick={() => setFilter('unack')}
            >
              Needs Acknowledgment
            </button>
          </div>

          <button
            className="btn-secondary"
            onClick={fetchEvents}
            disabled={isLoading}
            title="Refresh event history from backend storage"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
            </svg>
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 'var(--radius-sm)', color: '#FCA5A5', fontSize: '0.85rem' }}>
          {error}
        </div>
      )}

      <div className="table-wrapper">
        <table className="events-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Event ID</th>
              <th>Peak Score</th>
              <th>Duration</th>
              <th>Windows</th>
              <th>Status</th>
              <th>Verification / Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredEvents.length > 0 ? (
              filteredEvents.map((evt) => {
                const peakP = evt.peak_probability || 0
                const peakPct = (peakP * 100).toFixed(1)
                const duration = evt.duration_seconds !== undefined ? `${evt.duration_seconds.toFixed(2)}s` : 'N/A'
                const timestamp = evt.start_wall_time_iso || evt.logged_at_iso
                const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString() : 'N/A'

                let scoreClass = 'score-low'
                if (peakP >= 0.7) scoreClass = 'score-high'
                else if (peakP >= 0.35) scoreClass = 'score-med'

                return (
                  <tr key={evt.event_id}>
                    <td className="mono" style={{ whiteSpace: 'nowrap' }}>{timeStr}</td>
                    <td className="mono" style={{ color: '#F8FAFC' }}>{evt.event_id}</td>
                    <td>
                      <span className={`score-badge ${scoreClass}`}>
                        {peakPct}%
                      </span>
                    </td>
                    <td className="mono">{duration}</td>
                    <td className="mono">{evt.window_count || evt.positive_window_count || 1}</td>
                    <td>
                      <span style={{ fontSize: '0.75rem', textTransform: 'capitalize' }}>
                        {evt.event_status ? evt.event_status.replace('_', ' ') : (evt.alert_emitted ? 'Alert Triggered' : 'Candidate')}
                      </span>
                    </td>
                    <td>
                      {evt.acknowledged ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                          <span style={{ color: '#34D399', fontWeight: 600, fontSize: '0.75rem' }}>
                            ✓ Verified
                          </span>
                          {evt.operator_note && (
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              "{evt.operator_note}"
                            </span>
                          )}
                        </div>
                      ) : evt.alert_emitted ? (
                        <button
                          className="btn-secondary"
                          style={{ fontSize: '0.72rem', padding: '0.25rem 0.5rem' }}
                          onClick={() => onAcknowledgeEvent(evt.event_id, 'Verified from history table')}
                        >
                          Acknowledge
                        </button>
                      ) : (
                        <span style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>—</span>
                      )}
                    </td>
                  </tr>
                )
              })
            ) : (
              <tr>
                <td colSpan="7" className="empty-state">
                  {isLoading ? 'Loading detection history...' : 'No detection events recorded in current log session.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
