export function LiveMonitor({ detectorStatus, telemetry = {} }) {
  const threshold = detectorStatus.threshold || 0.35
  const rawProb = telemetry.raw_probability || 0
  const smoothedProb = telemetry.smoothed_probability || 0
  const audioRms = telemetry.audio_rms || 0
  const state = detectorStatus.state || 'IDLE'
  const priors = telemetry.priors || []
  const latencyMs = telemetry.inference_latency_ms || 16.62

  // Determine clear 3-state classification (SCREAM CANDIDATE, NON-SCREAM, UNCERTAIN)
  let classification = 'NON-SCREAM'
  let classificationClass = 'class-non-scream'
  if (smoothedProb >= threshold || rawProb >= threshold || state === 'CANDIDATE' || state === 'ALERT_ACTIVE') {
    classification = 'SCREAM CANDIDATE'
    classificationClass = 'class-scream'
  } else if (rawProb >= Math.max(0, threshold - 0.10) || smoothedProb >= Math.max(0, threshold - 0.10)) {
    classification = 'UNCERTAIN'
    classificationClass = 'class-uncertain'
  }

  // Scale RMS to a visible percentage (0.0 to ~0.2 typical range for normalized float32)
  const rmsPercent = Math.min(100, Math.round((audioRms / 0.15) * 100))
  const rawPercent = Math.min(100, Math.round(rawProb * 100))
  const smoothedPercent = Math.min(100, Math.round(smoothedProb * 100))
  const thresholdPercent = Math.min(100, Math.round(threshold * 100))

  const micStatusLabel = detectorStatus.mic_status === 'active'
    ? 'Active (Live Mic)'
    : detectorStatus.is_running
    ? 'Active (Buffer)'
    : 'Stopped (Idle)'

  return (
    <div className="card telemetry-panel">
      {/* Isolation Banner: Distinguish Live Production vs Offline Experimental Model */}
      <div className="live-isolation-banner" title="Safety Isolation Banner">
        <div className="isolation-banner-left">
          <span className="badge-live-prod">LIVE INFERENCE</span>
          <span className="live-path-text">
            PRODUCTION BASELINE — EXPERIMENTAL METRICS SHOWN SEPARATELY
          </span>
        </div>
        <div className="isolation-banner-right font-mono text-xs">
          <span>Model: <strong>Stage 5 LR (Frozen)</strong></span>
          <span className="sep">•</span>
          <span>Threshold: <strong>{threshold.toFixed(2)}</strong></span>
        </div>
      </div>

      <div className="card-header">
        <h2 className="card-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent-cyan)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 12h5l2-8 5 16 2-8h6" />
          </svg>
          Live Acoustic Detection & Inference
        </h2>
        <div className="header-status-pills font-mono">
          <span className="pill-latency" title="Edge model latency">
            Latency: <strong>{latencyMs.toFixed(1)} ms</strong>
          </span>
          <span className="pill-window">
            Window: #{telemetry.window_index || 0}
          </span>
        </div>
      </div>

      {/* Primary Classification & State Summary Row */}
      <div className="live-classification-summary-row">
        {/* Classification Result */}
        <div className="classification-box">
          <span className="summary-box-label">Current Classification</span>
          <div className={`classification-badge ${classificationClass}`}>
            <span className="status-dot pulse-dot" />
            <span className="font-semibold">{classification}</span>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="classification-box">
          <span className="summary-box-label">Classification Confidence</span>
          <div className="confidence-readout font-mono font-semibold">
            {smoothedProb >= threshold ? 'High Distress' : smoothedProb >= (threshold - 0.1) ? 'Elevated' : 'Baseline'} (p={smoothedProb.toFixed(3)})
          </div>
        </div>

        {/* Microphone Status */}
        <div className="classification-box">
          <span className="summary-box-label">Microphone Status</span>
          <div className={`mic-status-readout ${detectorStatus.is_running ? 'text-emerald' : 'text-muted'}`}>
            <span className="status-dot" />
            <span>{micStatusLabel}</span>
          </div>
        </div>

        {/* Internal State Machine */}
        <div className="classification-box state-machine-col">
          <span className="summary-box-label">State Machine</span>
          <div className={`state-badge-large state-${state}`}>
            <span className="status-dot pulse-dot" />
            {state}
          </div>
        </div>
      </div>

      {/* Audio Waveform & Activity Visualizer */}
      <div className="live-waveform-section">
        <div className="meter-header">
          <span className="meter-title">Real-Time Waveform Energy & Dynamic Activity</span>
          <span className="meter-value mono">RMS: {audioRms.toFixed(4)}</span>
        </div>
        <div className="waveform-strip-container">
          <div className="waveform-bars-visualizer">
            {[0.4, 0.7, 1.0, 0.8, 0.5, 0.9, 1.2, 0.6, 1.1, 0.75, 0.5, 0.85, 0.65, 0.4].map((mult, idx) => {
              const h = Math.min(100, Math.max(8, Math.round(rmsPercent * mult)))
              return (
                <div
                  key={idx}
                  className="waveform-bar"
                  style={{
                    height: `${h}%`,
                    opacity: audioRms > 0.005 ? 0.9 : 0.3,
                  }}
                />
              )
            })}
          </div>
        </div>
      </div>

      {/* Raw Scream Score Meter */}
      <div className="meter-group">
        <div className="meter-header">
          <span className="meter-title">Window Scream Score (Raw Model Output)</span>
          <span className="meter-value" style={{ color: rawProb >= threshold ? '#EF4444' : 'var(--text-primary)' }}>
            {(rawProb * 100).toFixed(1)}% ({rawProb.toFixed(4)})
          </span>
        </div>
        <div className="meter-track" title={`Raw Score: ${(rawProb * 100).toFixed(1)}% | Threshold: ${(threshold * 100).toFixed(1)}%`}>
          <div
            className="threshold-marker"
            style={{ left: `${thresholdPercent}%` }}
            title={`Threshold: ${(threshold * 100).toFixed(1)}%`}
          />
          <div
            className="meter-fill meter-fill-score"
            style={{ width: `${rawPercent}%` }}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
          <span>0.00 (Silent)</span>
          <span style={{ color: 'var(--text-secondary)' }}>Threshold: {threshold.toFixed(2)}</span>
          <span>1.00 (Definite Scream)</span>
        </div>
      </div>

      {/* Temporally Smoothed Probability */}
      <div className="meter-group">
        <div className="meter-header">
          <span className="meter-title">Temporally Smoothed Decision Score (EMA)</span>
          <span className="meter-value">
            {(smoothedProb * 100).toFixed(1)}% ({smoothedProb.toFixed(4)})
          </span>
        </div>
        <div className="meter-track">
          <div
            className="threshold-marker"
            style={{ left: `${thresholdPercent}%` }}
          />
          <div
            className="meter-fill meter-fill-smoothed"
            style={{ width: `${smoothedPercent}%` }}
          />
        </div>
      </div>

      {/* Pretrained AudioSet Priors */}
      <div className="priors-container">
        <div className="meter-header" style={{ marginBottom: '0.4rem' }}>
          <span className="meter-title">Pretrained YAMNet Acoustic Context Priors</span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Top 3 AudioSet Classes</span>
        </div>
        <div className="priors-list">
          {priors.length > 0 ? (
            priors.map((p, idx) => (
              <span key={idx} className="prior-pill">
                {p.class_name}: <strong>{(p.score * 100).toFixed(1)}%</strong>
              </span>
            ))
          ) : (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Awaiting window inference...
            </span>
          )}
        </div>
      </div>

      {/* Mandatory Safety Notice - Section 3.F */}
      <div className="live-safety-notice-box">
        <div className="safety-notice-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </div>
        <p className="safety-notice-text text-xs">
          <strong>OPERATIONAL SAFETY NOTICE:</strong> Possible scream detected — requires human auditory verification. Automated acoustic alerts do not confirm an emergency. Automated dispatch of emergency services is strictly prohibited.
        </p>
      </div>
    </div>
  )
}
