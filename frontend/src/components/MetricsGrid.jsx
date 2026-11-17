export function MetricsGrid({ metrics }) {
  const latency = metrics?.latency_metrics_ms || {}
  const meanLat = latency.mean !== undefined ? `${latency.mean.toFixed(1)} ms` : 'N/A'
  const p95Lat = latency.p95 !== undefined ? `${latency.p95.toFixed(1)} ms` : 'N/A'

  const uptimeSec = metrics?.session_uptime_seconds || 0
  const formatUptime = (sec) => {
    const hrs = Math.floor(sec / 3600)
    const mins = Math.floor((sec % 3600) / 60)
    const s = Math.floor(sec % 60)
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-blue)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          System & Stream Telemetry
        </h2>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Real Offline/Online Engine Metrics
        </span>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Windows Processed</span>
          <span className="metric-number">
            {metrics?.windows_processed?.toLocaleString() || 0}
          </span>
          <span className="metric-sub">
            Hop: {metrics?.hop_duration_ms || 487.5} ms (~50% overlap)
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Alerts Emitted</span>
          <span className="metric-number" style={{ color: metrics?.total_alerts_emitted > 0 ? '#EF4444' : 'inherit' }}>
            {metrics?.total_alerts_emitted || 0}
          </span>
          <span className="metric-sub">
            {metrics?.total_alerts_suppressed || 0} suppressed (cooldown)
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Inference Latency</span>
          <span className="metric-number">
            {meanLat}
          </span>
          <span className="metric-sub">
            P95: {p95Lat} (YAMNet + Classifier)
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Dropped / Errors</span>
          <span className="metric-number" style={{ color: (metrics?.inference_errors > 0 || metrics?.dropped_samples > 0) ? '#F59E0B' : 'inherit' }}>
            {metrics?.inference_errors || 0}
          </span>
          <span className="metric-sub">
            Buffer Gaps: {metrics?.dropped_samples ? `${metrics.dropped_samples} smp` : '0 smp'}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <span>
          <strong>Audio Duration:</strong> {metrics?.total_audio_seconds ? `${metrics.total_audio_seconds.toFixed(1)}s` : '0.0s'}
        </span>
        <span>
          <strong>Realtime Factor:</strong> {metrics?.realtime_factor ? `${metrics.realtime_factor}x` : '< 0.2x'}
        </span>
        <span>
          <strong>Session Uptime:</strong> <span className="mono" style={{ color: '#F8FAFC' }}>{formatUptime(uptimeSec)}</span>
        </span>
      </div>
    </div>
  )
}
