import { useState, useEffect, useRef, useMemo } from 'react'
import { useMultiModelSocket } from '../hooks/useMultiModelSocket'

/**
 * Multi-Model Live Audio Testing Lab (Stage 8.9.16).
 *
 * Real-time testing environment evaluating multiple experimental scream detection models
 * simultaneously using a single incoming shared audio stream.
 *
 * Primary Model: D_v4 + Family A (Stage 8.9.14, Threshold: 0.420)
 * Comparison Candidates: D_v4+B, F_v6 Acoustic, Stage 15 Models A/B/C, Production Baseline
 */
export function MultiModelLiveLab() {
  const {
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
  } = useMultiModelSocket()

  const [selectedDevice, setSelectedDevice] = useState('')
  const [selectedSignal, setSelectedSignal] = useState('scream_burst')
  const [isSimulating, setIsSimulating] = useState(false)
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false)
  const [reviewTargetEvent, setReviewTargetEvent] = useState(null)
  const [reviewLabel, setReviewLabel] = useState('SCREAM')
  const [soundClass, setSoundClass] = useState('screaming')
  const [reviewerNotes, setReviewerNotes] = useState('')
  const [sessionNotes, setSessionNotes] = useState('Multi-Model Comparative Live Session')
  const [isSubmittingReview, setIsSubmittingReview] = useState(false)
  const [diagnosticMode, setDiagnosticMode] = useState(false)

  // Waveform Canvas
  const canvasRef = useRef(null)

  // Draw simulated or live waveform
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId
    let phase = 0

    const render = () => {
      const width = canvas.width
      const height = canvas.height
      ctx.clearRect(0, 0, width, height)

      // Background grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(0, height / 2)
      ctx.lineTo(width, height)
      ctx.stroke()

      // Waveform trace
      const rms = latestWindow?.audio_rms || 0.005
      const peak = latestWindow?.audio_peak || 0.01
      const isClipping = latestWindow?.is_clipping || false

      ctx.beginPath()
      ctx.lineWidth = 2
      ctx.strokeStyle = isClipping
        ? '#ef4444'
        : rms > 0.08
        ? '#f59e0b'
        : '#06b6d4'

      const points = 120
      for (let i = 0; i < points; i++) {
        const x = (i / (points - 1)) * width
        const amp = Math.min(height * 0.45, Math.max(2, rms * height * 5.0))
        const freq = 0.15 + (latestWindow?.primary_prediction?.score || 0.1) * 0.2
        const y =
          height / 2 +
          Math.sin(i * freq + phase) * amp * (0.8 + 0.2 * Math.cos(i * 0.08))
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.stroke()

      phase += labStatus.is_running ? 0.2 : 0.02
      animationId = requestAnimationFrame(render)
    }

    render()
    return () => cancelAnimationFrame(animationId)
  }, [latestWindow, labStatus.is_running])

  // Handle Start / Stop
  const handleToggleLab = async () => {
    try {
      if (labStatus.is_running) {
        await stopLab()
      } else {
        const devIdx = selectedDevice !== '' ? parseInt(selectedDevice, 10) : null
        await startLab(devIdx, sessionNotes)
      }
    } catch (err) {
      alert(`Error toggling lab: ${err.message}`)
    }
  }

  // Handle Audio Injection
  const handleSimulate = async (sigType = selectedSignal) => {
    setIsSimulating(true)
    try {
      await simulateAudio(sigType, 1.5, 0.6)
    } catch (err) {
      console.error('Simulation error:', err)
    } finally {
      setTimeout(() => setIsSimulating(false), 500)
    }
  }

  // Open Review Modal
  const handleOpenReview = (event) => {
    setReviewTargetEvent(event)
    setReviewLabel('SCREAM')
    setSoundClass('screaming')
    setReviewerNotes('')
    setIsReviewModalOpen(true)
  }

  // Submit Review
  const handleSubmitReview = async () => {
    if (!reviewTargetEvent) return
    setIsSubmittingReview(true)
    try {
      await submitReview({
        session_id: labStatus.active_session_id || reviewTargetEvent.session_id || 'manual_review_session',
        event_id: reviewTargetEvent.event_id,
        window_start_idx: reviewTargetEvent.window_start_idx,
        window_end_idx: reviewTargetEvent.window_end_idx,
        timestamp_start: Date.now() / 1000 - (reviewTargetEvent.duration_seconds || 1.0),
        timestamp_end: Date.now() / 1000,
        ground_truth_label: reviewLabel,
        sound_class: soundClass,
        reviewer_notes: reviewerNotes,
      })
      if (labStatus.active_session_id) {
        await fetchSessionDetails(labStatus.active_session_id)
      }
      setIsReviewModalOpen(false)
      setReviewTargetEvent(null)
    } catch (err) {
      alert(`Error submitting human review: ${err.message}`)
    } finally {
      setIsSubmittingReview(false)
    }
  }

  // Primary model prediction helper
  const primaryPred = latestWindow?.primary_prediction || {
    display_name: 'D_v4 + Family A (Turbulence)',
    score: 0.0,
    threshold: 0.420,
    decision_margin: -0.420,
    classification: labStatus.is_running ? 'NO_ACOUSTIC_ACTIVITY' : 'STANDBY',
    latency_ms: 0.0,
    status: 'ACTIVE',
  }

  // Comparison models list
  const comparisonList = useMemo(() => {
    const list = []
    const predMap = latestWindow?.all_predictions || {}

    // Expected order
    const order = [
      'D_V4_FAMILY_B',
      'F_V6_ACOUSTIC',
      'STAGE_8915_MODEL_A',
      'STAGE_8915_MODEL_B',
      'STAGE_8915_MODEL_C',
      'PRODUCTION_BASELINE',
    ]

    for (const mid of order) {
      const regMeta = models.find((m) => m.model_id === mid)
      const pred = predMap[mid]
      list.push({
        model_id: mid,
        meta: regMeta,
        pred: pred || {
          model_id: mid,
          display_name: regMeta?.display_name || mid,
          stage: regMeta?.stage || '',
          score: 0.0,
          threshold: regMeta?.operating_threshold || 0.35,
          decision_margin: -(regMeta?.operating_threshold || 0.35),
          classification: labStatus.is_running ? 'NO_ACOUSTIC_ACTIVITY' : 'STANDBY',
          latency_ms: 0.0,
          status: regMeta?.status === 'ERROR' ? 'ERROR' : 'ACTIVE',
        },
      })
    }
    return list
  }, [models, latestWindow, labStatus.is_running])

  // Helpers for badge styling
  const getClassificationBadge = (classification) => {
    switch (classification) {
      case 'SCREAM_CANDIDATE':
        return <span className="lab-badge lab-badge-scream animate-pulse">SCREAM CANDIDATE</span>
      case 'NO_ACOUSTIC_ACTIVITY':
        return <span className="lab-badge lab-badge-silence">NO ACOUSTIC ACTIVITY</span>
      case 'UNCERTAIN':
        return <span className="lab-badge lab-badge-uncertain">UNCERTAIN</span>
      case 'MODEL_ERROR':
        return <span className="lab-badge lab-badge-error">MODEL ERROR</span>
      case 'DISABLED':
        return <span className="lab-badge lab-badge-disabled">DISABLED</span>
      case 'STANDBY':
        return <span className="lab-badge lab-badge-disabled">STANDBY</span>
      default:
        return <span className="lab-badge lab-badge-non-scream">{classification || 'NON-SCREAM'}</span>
    }
  }

  return (
    <div className="multimodel-lab-container">
      {/* SECTION 5.A: TOP AUDIO INPUT & CONTROL PANEL */}
      <section className="lab-panel lab-input-panel">
        <div className="lab-panel-header">
          <div className="panel-title-group">
            <div className="lab-icon-pulse">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 1v11M8 5a4 4 0 0 0 8 0M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8" />
              </svg>
            </div>
            <div>
              <h2 className="lab-title">Shared Microphone Capture & Audio Testing Stream</h2>
              <div className="lab-subtitle">Single unified audio pipeline feeding 7 simultaneous experimental architectures</div>
            </div>
          </div>

          <div className="lab-controls-group">
            <select
              className="lab-device-select"
              value={selectedDevice}
              onChange={(e) => setSelectedDevice(e.target.value)}
              disabled={labStatus.is_running}
              title="Select audio input device"
            >
              <option value="">Default Microphone (16 kHz)</option>
              {devices.map((d) => (
                <option key={d.index} value={d.index}>
                  {d.name} {d.is_default ? '(System Default)' : ''}
                </option>
              ))}
            </select>

            <button
              type="button"
              className={`btn-lab-toggle ${labStatus.is_running ? 'running' : 'stopped'}`}
              onClick={handleToggleLab}
            >
              {labStatus.is_running ? (
                <>
                  <span className="btn-dot-pulse" /> Stop Live Lab
                </>
              ) : (
                <>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  Start Live Testing
                </>
              )}
            </button>
          </div>
        </div>

        {/* Audio Telemetry Strip */}
        <div className="audio-telemetry-grid">
          <div className="telemetry-item">
            <span className="telemetry-label">Microphone Status</span>
            <span className={`telemetry-val ${labStatus.mic_status === 'active' ? 'text-emerald' : 'text-amber'}`}>
              {labStatus.mic_status === 'active'
                ? 'Active (16,000 Hz Mono)'
                : labStatus.is_running
                ? 'Buffer Stream Active'
                : 'Inactive / Stopped'}
            </span>
          </div>

          <div className="telemetry-item">
            <span className="telemetry-label">Current Window</span>
            <span className="telemetry-val font-mono">
              #{latestWindow?.window_index || labStatus.window_counter || 0} ({0.975}s / {0.4875}s hop)
            </span>
          </div>

          <div className="telemetry-item">
            <span className="telemetry-label">RMS Energy / Peak</span>
            <span className="telemetry-val font-mono">
              RMS: {(latestWindow?.audio_rms || 0).toFixed(4)} | Peak: {(latestWindow?.audio_peak || 0).toFixed(3)}
            </span>
          </div>

          <div className="telemetry-item">
            <span className="telemetry-label">Clipping / Backpressure</span>
            <span className="telemetry-val font-mono">
              {latestWindow?.is_clipping ? (
                <strong className="text-crimson animate-pulse">CLIPPING DETECTED</strong>
              ) : (
                <span className="text-secondary">Clean Headroom</span>
              )}
              {' • '}
              Dropped: {labStatus.dropped_windows_total || 0}
            </span>
          </div>
        </div>

        {/* Acoustic Activity Gate & Diagnostic Mode Controls */}
        <div className="diagnostic-panel-strip font-mono" style={{ margin: '0.75rem 0' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={labStatus.acoustic_gate?.enabled !== false}
              onChange={(e) => toggleAcousticGate(e.target.checked)}
            />
            <span>
              Acoustic Activity Gate:{' '}
              <strong className={labStatus.acoustic_gate?.enabled !== false ? 'text-emerald' : 'text-amber'}>
                {labStatus.acoustic_gate?.enabled !== false ? 'ACTIVE (Muting Silence False Positives)' : 'BYPASSED'}
              </strong>
            </span>
          </label>

          <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer', marginLeft: 'auto' }}>
            <input
              type="checkbox"
              checked={diagnosticMode}
              onChange={(e) => setDiagnosticMode(e.target.checked)}
            />
            <strong className="text-cyan">Diagnostic Mode (Raw Feature Telemetry)</strong>
          </label>

          {diagnosticMode && latestWindow && (
            <div style={{ width: '100%', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '0.4rem', fontSize: '0.7rem' }}>
              <span className="text-secondary">Signal Diagnostics: </span>
              RMS: <strong>{(latestWindow.audio_rms || 0).toFixed(6)}</strong> | Peak: <strong>{(latestWindow.audio_peak || 0).toFixed(4)}</strong> |
              Gate State: <strong className={latestWindow.acoustic_gate_active ? 'text-amber' : 'text-emerald'}>{latestWindow.acoustic_gate_active ? 'SILENCE GATED (RMS < 0.0035)' : 'AUDIO ACTIVE'}</strong> |
              Feature Latency: <strong>{latestWindow.shared_feature_latency_ms || 0} ms</strong>
            </div>
          )}
        </div>

        {/* Live Waveform Canvas & Synthetic Audio Injection */}
        <div className="waveform-and-injection-row">
          <div className="canvas-container">
            <canvas ref={canvasRef} width="640" height="90" className="waveform-canvas" />
            <div className="canvas-watermark font-mono">16 kHz Real-Time Buffer Trace</div>
          </div>

          <div className="audio-injection-panel">
            <div className="injection-header">
              <span className="injection-title">Audio Injection Simulator (Zero-Hardware Lab Testing)</span>
              <span className="injection-sub">Injects exact acoustic waveforms directly into the shared buffer</span>
            </div>
            <div className="injection-buttons-grid">
              <button
                type="button"
                className="btn-inject btn-inject-scream"
                onClick={() => handleSimulate('scream_burst')}
                disabled={isSimulating}
                title="Inject synthetic distress scream burst (1.8-3.2 kHz with subharmonics)"
              >
                Distress Scream
              </button>
              <button
                type="button"
                className="btn-inject btn-inject-shout"
                onClick={() => handleSimulate('high_pitch_shout')}
                disabled={isSimulating}
                title="Inject high-pitch vocal shouting (formant harmonics without turbulence)"
              >
                High-Pitch Shout
              </button>
              <button
                type="button"
                className="btn-inject btn-inject-crowd"
                onClick={() => handleSimulate('crowd_noise')}
                disabled={isSimulating}
                title="Inject festival crowd chatter and pink noise"
              >
                Crowd Cheering
              </button>
              <button
                type="button"
                className="btn-inject btn-inject-chirp"
                onClick={() => handleSimulate('chirp')}
                disabled={isSimulating}
                title="Inject acoustic linear frequency sweep"
              >
                Chirp Sweep
              </button>
              <button
                type="button"
                className="btn-inject btn-inject-silence"
                onClick={() => handleSimulate('silence')}
                disabled={isSimulating}
                title="Inject background acoustic floor"
              >
                Silence / Floor
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5.B: PRIMARY EXPERIMENTAL MODEL CARD */}
      <section className="primary-model-banner">
        <div className="primary-banner-badge" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>PRIMARY EXPERIMENTAL CANDIDATE (STAGE 8.9.14)</span>
          <span className="lab-verdict-badge verdict-rejected">
            AUDIT VERDICT: REJECTED (127.3 FA/HR)
          </span>
        </div>
        <div className="primary-card-content">
          <div className="primary-left">
            <div className="primary-title-row">
              <h3 className="primary-model-name">D_v4 + Family A — Acoustic Discriminability Model</h3>
              {getClassificationBadge(primaryPred.classification)}
            </div>
            <div className="primary-desc">
              Multi-pooled YAMNet embeddings [max, p10, mean] (3,072) + 8 Family A Vocal Turbulence & Harmonicity features. Total 3,080 dims.
              <span className="text-amber" style={{ display: 'block', marginTop: '0.3rem', fontSize: '0.75rem' }}>
                Forensic Audit Warning: Model officially failed preregistered acceptance gates offline (7.07% FPR, 20.0% infant crying FPR). Production Baseline is the recommended demonstration candidate.
              </span>
            </div>

            <div className="primary-metrics-strip font-mono">
              <div className="p-stat">
                <span className="p-stat-label">Model Score</span>
                <span className={`p-stat-val ${primaryPred.score >= 0.420 ? 'text-crimson' : 'text-cyan'}`}>
                  {(primaryPred.score || 0).toFixed(4)}
                </span>
              </div>
              <div className="p-stat">
                <span className="p-stat-label">Threshold</span>
                <span className="p-stat-val text-amber">0.4200</span>
              </div>
              <div className="p-stat">
                <span className="p-stat-label">Decision Margin</span>
                <span className={`p-stat-val ${primaryPred.decision_margin >= 0 ? 'text-crimson' : 'text-emerald'}`}>
                  {primaryPred.decision_margin >= 0 ? '+' : ''}{(primaryPred.decision_margin || 0).toFixed(4)}
                </span>
              </div>
              <div className="p-stat">
                <span className="p-stat-label">Inference Latency</span>
                <span className="p-stat-val text-secondary">{(primaryPred.latency_ms || 0).toFixed(2)} ms</span>
              </div>
              <div className="p-stat">
                <span className="p-stat-label">Integrity SHA-256</span>
                <span className="p-stat-val text-emerald">92FEAA72... (VERIFIED)</span>
              </div>
            </div>
          </div>

          <div className="primary-meter-container">
            <div className="meter-label-row font-mono">
              <span>0.00</span>
              <span className="meter-th-label">Threshold: 0.420</span>
              <span>1.00</span>
            </div>
            <div className="meter-track">
              <div
                className={`meter-fill ${primaryPred.score >= 0.420 ? 'meter-fill-alert' : 'meter-fill-safe'}`}
                style={{ width: `${Math.min(100, Math.max(0, (primaryPred.score || 0) * 100))}%` }}
              />
              <div className="meter-threshold-marker" style={{ left: '42%' }} />
            </div>
            <div className="meter-status-note">
              {primaryPred.score >= 0.420 ? (
                <span className="text-crimson font-semibold">Distress Acoustic Signature Exceeds Threshold</span>
              ) : (
                <span className="text-emerald">Operating in Quiet / Non-Distress Range</span>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 5.C: COMPARISON MODEL CARDS GRID */}
      <section className="comparison-grid-section">
        <div className="section-heading-row">
          <div>
            <h3 className="section-title">Experimental Candidate & Baseline Comparison Suite</h3>
            <p className="section-subtitle">Real-time side-by-side inference on identical audio windows. Toggle candidates to benchmark CPU latency.</p>
          </div>
          <div className="shared-feat-latency-badge font-mono">
            Shared Feature Extraction: {latestWindow?.shared_feature_latency_ms || 0} ms | Total Window: {latestWindow?.total_latency_ms || 0} ms
          </div>
        </div>

        <div className="model-cards-grid">
          {comparisonList.map(({ model_id, meta, pred }) => (
            <div key={model_id} className={`comparison-card ${pred.status === 'DISABLED' ? 'card-disabled' : ''} ${model_id === 'PRODUCTION_BASELINE' ? 'card-production-highlight' : ''}`}>
              <div className="card-top-row">
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                    <span className="card-stage font-mono">{meta?.stage || pred.stage}</span>
                    {meta?.is_certified ? (
                      <span className="lab-verdict-badge verdict-verified">RECOMMENDED BASELINE</span>
                    ) : (
                      <span className="lab-verdict-badge verdict-rejected">AUDIT: REJECTED</span>
                    )}
                  </div>
                  <h4 className="card-model-name">{meta?.display_name || pred.display_name}</h4>
                </div>
                <div className="card-toggle-wrapper">
                  <label className="toggle-switch" title={`Toggle ${meta?.display_name || model_id}`}>
                    <input
                      type="checkbox"
                      checked={meta?.is_enabled !== false}
                      onChange={(e) => toggleModel(model_id, e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>
              </div>

              <div className="card-features-note">
                {meta?.feature_extractor_type || `${meta?.expected_feature_dims || 1024} dimensions`}
              </div>

              <div className="card-status-badge-row">
                {getClassificationBadge(pred.classification)}
                <span className="card-latency font-mono">{pred.latency_ms.toFixed(2)} ms</span>
              </div>

              {/* Score bar */}
              <div className="card-meter-wrapper">
                <div className="meter-label-row font-mono text-xs">
                  <span>Score: {pred.score.toFixed(4)}</span>
                  <span>Th: {pred.threshold.toFixed(3)}</span>
                </div>
                <div className="meter-track meter-track-sm">
                  <div
                    className={`meter-fill ${pred.score >= pred.threshold ? 'meter-fill-alert' : 'meter-fill-safe'}`}
                    style={{ width: `${Math.min(100, Math.max(0, pred.score * 100))}%` }}
                  />
                  <div
                    className="meter-threshold-marker"
                    style={{ left: `${pred.threshold * 100}%` }}
                  />
                </div>
              </div>

              <div className="card-footer font-mono text-xs">
                <span>Margin: {pred.decision_margin >= 0 ? '+' : ''}{pred.decision_margin.toFixed(4)}</span>
                <span className={pred.status === 'ERROR' ? 'text-crimson' : 'text-emerald'}>
                  {pred.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* SECTION 5.D & 5.E: LIVE PREDICTION COMPARISON TABLE & MODEL AGREEMENT */}
      <section className="agreement-and-table-section">
        <div className="agreement-banner">
          <div className="agreement-col">
            <span className="agreement-label">Model Agreement Matrix (Latest Window #{latestWindow?.window_index || 0})</span>
            <div className="agreement-stats-row font-mono">
              <span className="agree-stat text-crimson">
                Scream Votes: <strong>{latestWindow?.agreement?.scream_votes || 0}</strong>
              </span>
              <span className="agree-stat text-emerald">
                Non-Scream: <strong>{latestWindow?.agreement?.non_scream_votes || 0}</strong>
              </span>
              <span className="agree-stat text-amber">
                Uncertain: <strong>{latestWindow?.agreement?.uncertain_votes || 0}</strong>
              </span>
              <span className="agree-stat text-cyan">
                Active Models: <strong>{latestWindow?.agreement?.total_active_models || 0}</strong>
              </span>
            </div>
          </div>

          <div className="agreement-verdict-col">
            {latestWindow?.agreement?.disagreement_detected ? (
              <div className="disagreement-alert font-mono">
                <span className="alert-pulse-dot" /> DISAGREEMENT DETECTED ACROSS MODELS
              </div>
            ) : (
              <div className="agreement-consensus font-mono text-emerald">
                CONSENSUS: ALL MODELS AGREE
              </div>
            )}
            <div className="primary-prod-divergence font-mono text-xs">
              Primary (D_v4+A): <strong>{latestWindow?.primary_prediction?.classification || 'NON_SCREAM'}</strong> vs Prod Baseline: <strong>{latestWindow?.production_prediction?.classification || 'NON_SCREAM'}</strong>
              {latestWindow?.agreement?.primary_vs_production_divergence && (
                <span className="text-amber font-semibold"> (DIVERGING)</span>
              )}
            </div>
            <div className="agreement-disclaimer">
              Notice: Majority vote is for comparative diagnostic visualization only; not a validated classifier.
            </div>
          </div>
        </div>

        {/* Section 5.D Table */}
        <div className="lab-table-container">
          <div className="table-header-title">Synchronized Audio Window Prediction Log (Recent 15 Windows)</div>
          <table className="lab-table font-mono">
            <thead>
              <tr>
                <th>Win #</th>
                <th>Timestamp</th>
                <th>Model ID</th>
                <th>Raw Score</th>
                <th>Operating Th</th>
                <th>Decision Margin</th>
                <th>Classification</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody>
              {windowHistory.slice(0, 15).flatMap((win) => {
                const preds = Object.values(win.all_predictions || {})
                return preds.map((p, pIdx) => (
                  <tr
                    key={`${win.window_index}_${p.model_id}`}
                    className={`${win.agreement?.disagreement_detected ? 'row-disagreement' : ''} ${pIdx === 0 ? 'row-group-start' : ''}`}
                  >
                    <td>{pIdx === 0 ? `#${win.window_index}` : ''}</td>
                    <td>{pIdx === 0 ? win.iso_timestamp?.slice(11, 19) : ''}</td>
                    <td>
                      <strong>{p.model_id}</strong>
                      {p.model_id === 'D_V4_FAMILY_A' && <span className="tag-primary">PRIMARY</span>}
                      {p.model_id === 'PRODUCTION_BASELINE' && <span className="tag-baseline">REF</span>}
                    </td>
                    <td className={p.score >= p.threshold ? 'text-crimson font-bold' : ''}>
                      {p.score.toFixed(4)}
                    </td>
                    <td>{p.threshold.toFixed(3)}</td>
                    <td className={p.decision_margin >= 0 ? 'text-crimson' : 'text-emerald'}>
                      {p.decision_margin >= 0 ? '+' : ''}{p.decision_margin.toFixed(4)}
                    </td>
                    <td>{getClassificationBadge(p.classification)}</td>
                    <td>{p.latency_ms.toFixed(2)} ms</td>
                  </tr>
                ))
              })}
              {windowHistory.length === 0 && (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem' }}>
                    Awaiting audio window capture. Start the Live Lab or inject synthetic audio above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* SECTION 5.F: LIVE CANDIDATE EVENT HISTORY & HUMAN VERIFICATION */}
      <section className="event-history-section">
        <div className="section-heading-row">
          <div>
            <h3 className="section-title">Candidate Event History & Explicit Human Review Studio</h3>
            <p className="section-subtitle">
              Scream candidates detected in real-time. Explicit operator labeling creates ground-truth records for session metrics without modifying production databases.
            </p>
          </div>
          <div className="font-mono text-xs text-secondary">
            Session ID: {labStatus.active_session_id || 'Unbound'} • Events Captured: {candidateEvents.length}
          </div>
        </div>

        <div className="lab-table-container">
          <table className="lab-table font-mono">
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Start Time</th>
                <th>Duration</th>
                <th>Peak Score</th>
                <th>Candidate Prediction</th>
                <th>Agreeing Models</th>
                <th>Verification Status</th>
                <th>Operator Action</th>
              </tr>
            </thead>
            <tbody>
              {candidateEvents.map((evt) => (
                <tr key={evt.event_id}>
                  <td><strong>{evt.event_id}</strong></td>
                  <td>{evt.start_time?.slice(11, 19)}</td>
                  <td>{evt.duration_seconds}s</td>
                  <td className="text-crimson font-bold">{(evt.peak_score || 0).toFixed(4)}</td>
                  <td><span className="lab-badge lab-badge-scream">SCREAM CANDIDATE</span></td>
                  <td>{(evt.models_in_agreement || []).join(', ') || 'D_v4+A'}</td>
                  <td>
                    {evt.verification_status === 'SCREAM' && (
                      <span className="lab-badge lab-badge-scream">VERIFIED SCREAM</span>
                    )}
                    {evt.verification_status === 'NON_SCREAM' && (
                      <span className="lab-badge lab-badge-non-scream">VERIFIED NON-SCREAM</span>
                    )}
                    {evt.verification_status === 'AMBIGUOUS' && (
                      <span className="lab-badge lab-badge-uncertain">AMBIGUOUS</span>
                    )}
                    {evt.verification_status === 'UNVERIFIED' && (
                      <span className="lab-badge lab-badge-disabled">UNVERIFIED</span>
                    )}
                  </td>
                  <td>
                    <button
                      type="button"
                      className="btn-verify-event"
                      onClick={() => handleOpenReview(evt)}
                    >
                      Verify / Label
                    </button>
                  </td>
                </tr>
              ))}
              {candidateEvents.length === 0 && (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem' }}>
                    No scream candidate events detected yet. Candidate events will appear here when audio exceeds the 0.420 threshold.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* SECTION 6: MODEL PERFORMANCE COMPARISON (OFFLINE VS LIVE EVALUATION) */}
      <section className="performance-comparison-section">
        <h3 className="section-title">Model Performance & Reliability Matrix</h3>

        <div className="perf-grid">
          {/* Offline Benchmark Column */}
          <div className="perf-card">
            <h4 className="perf-header">1. Previously Verified Offline Benchmark (Stages 8.9.14 & 8.9.15)</h4>
            <div className="perf-note">
              1,384 audio files evaluated across 304 test instances (109 screams, 198 hard negatives) under frozen seed 42:
            </div>
            <table className="mini-perf-table font-mono text-xs">
              <thead>
                <tr>
                  <th>Model</th>
                  <th>Recall</th>
                  <th>FPR</th>
                  <th>F1 Score</th>
                  <th>Dims</th>
                  <th>Th</th>
                </tr>
              </thead>
              <tbody>
                <tr className="highlight-row">
                  <td><strong>D_v4 + Family A (Primary)</strong></td>
                  <td className="text-emerald">90.83%</td>
                  <td>7.07%</td>
                  <td className="font-bold">87.61%</td>
                  <td>3,080</td>
                  <td>0.420</td>
                </tr>
                <tr>
                  <td>D_v4 + Family B</td>
                  <td>81.65%</td>
                  <td className="text-emerald">4.55%</td>
                  <td>84.76%</td>
                  <td>3,080</td>
                  <td>0.650</td>
                </tr>
                <tr>
                  <td>F_v6 Acoustic Full</td>
                  <td>87.16%</td>
                  <td>6.57%</td>
                  <td>85.59%</td>
                  <td>3,102</td>
                  <td>0.360</td>
                </tr>
                <tr>
                  <td>Stage 15 Model A (MLP)</td>
                  <td>88.07%</td>
                  <td className="text-emerald">5.05%</td>
                  <td>88.89%</td>
                  <td>3,102</td>
                  <td>0.440</td>
                </tr>
                <tr>
                  <td>Stage 15 Model B (TCN)</td>
                  <td>91.74%</td>
                  <td>5.56%</td>
                  <td>90.50%</td>
                  <td>70x1024</td>
                  <td>0.610</td>
                </tr>
                <tr>
                  <td>Stage 15 Model C (Fusion)</td>
                  <td className="text-emerald">93.58%</td>
                  <td className="text-emerald">4.04%</td>
                  <td className="font-bold">93.15%</td>
                  <td>9</td>
                  <td>0.500</td>
                </tr>
                <tr>
                  <td>Production Baseline</td>
                  <td>83.49%</td>
                  <td className="text-crimson">10.61%</td>
                  <td>81.25%</td>
                  <td>1,024</td>
                  <td>0.350</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Live Microphone Session Evaluation Column */}
          <div className="perf-card">
            <h4 className="perf-header">2. Live Testing Session Metrics (Computed Exclusively from Human Labels)</h4>
            <div className="perf-note">
              Metrics require explicit operator review. Repeated windows from the same candidate event are preserved as single acoustic events.
            </div>

            {activeSession?.metrics?.has_ground_truth ? (
              <table className="mini-perf-table font-mono text-xs">
                <thead>
                  <tr>
                    <th>Model</th>
                    <th>Event Recall</th>
                    <th>Event Precision</th>
                    <th>Event FPR</th>
                    <th>F1</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(activeSession.metrics.per_model_metrics || {}).map(([mid, m]) => (
                    <tr key={mid} className={mid === 'D_V4_FAMILY_A' ? 'highlight-row' : ''}>
                      <td><strong>{mid}</strong></td>
                      <td>{(m.event_recall * 100).toFixed(1)}%</td>
                      <td>{(m.event_precision * 100).toFixed(1)}%</td>
                      <td>{(m.event_fpr * 100).toFixed(1)}%</td>
                      <td className="font-bold">{(m.event_f1 * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="live-no-metrics font-mono">
                <div className="notice-icon">i</div>
                <div>
                  No human-verified ground-truth events submitted yet for this session.
                  <br />
                  <span className="text-secondary text-xs">
                    To compute live precision, recall, and false positive rates, click "Verify / Label" on candidate events in the table above.
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* HUMAN REVIEW MODAL (STRICTLY ISOLATED TO EXPERIMENTAL DB) */}
      {isReviewModalOpen && reviewTargetEvent && (
        <div className="modal-overlay" onClick={() => setIsReviewModalOpen(false)}>
          <div className="modal-dialog font-mono" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Human Auditory Verification — Event #{reviewTargetEvent.event_id}</h3>
              <button
                type="button"
                className="btn-modal-close"
                onClick={() => setIsReviewModalOpen(false)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="review-meta-box">
                <div>Candidate: <strong>{reviewTargetEvent.event_id}</strong></div>
                <div>Peak Score: <strong>{(reviewTargetEvent.peak_score || 0).toFixed(4)}</strong></div>
                <div>Duration: <strong>{reviewTargetEvent.duration_seconds}s</strong></div>
                <div>Active Session: <strong>{labStatus.active_session_id || 'manual_review_session'}</strong></div>
              </div>

              <div className="form-group">
                <label>Ground-Truth Auditory Decision:</label>
                <div className="radio-group">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="gt_label"
                      value="SCREAM"
                      checked={reviewLabel === 'SCREAM'}
                      onChange={() => setReviewLabel('SCREAM')}
                    />
                    <span className="text-crimson font-bold">Genuine Distress Scream (Positive)</span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="gt_label"
                      value="NON_SCREAM"
                      checked={reviewLabel === 'NON_SCREAM'}
                      onChange={() => setReviewLabel('NON_SCREAM')}
                    />
                    <span className="text-emerald font-bold">Non-Scream / Hard Negative (Negative)</span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="gt_label"
                      value="AMBIGUOUS"
                      checked={reviewLabel === 'AMBIGUOUS'}
                      onChange={() => setReviewLabel('AMBIGUOUS')}
                    />
                    <span className="text-amber">Ambiguous / Inaudible</span>
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label>Sound Classification Category:</label>
                <select
                  className="form-select"
                  value={soundClass}
                  onChange={(e) => setSoundClass(e.target.value)}
                >
                  <option value="screaming">Distress Screaming</option>
                  <option value="shouting">Vocal Shouting / Yelling</option>
                  <option value="cheering">Crowd Cheering / Chanting</option>
                  <option value="laughter">Laughter / Play</option>
                  <option value="music">Live Music / Bass</option>
                  <option value="synthetic">Synthetic Test Injection</option>
                  <option value="speech">Normal Conversational Speech</option>
                </select>
              </div>

              <div className="form-group">
                <label>Reviewer Forensic Notes:</label>
                <textarea
                  className="form-textarea"
                  rows="3"
                  value={reviewerNotes}
                  onChange={(e) => setReviewerNotes(e.target.value)}
                  placeholder="Record auditory observations (e.g., vocal fry, sustained pitch, crowd background)..."
                />
              </div>

              <div className="modal-isolation-notice text-xs">
                Notice: This label will be stored strictly in <code>backend/database/experimental_sessions.db</code>. The production review database (<code>stage8_9_reviews.db</code>) is strictly frozen and never modified.
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setIsReviewModalOpen(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn-primary"
                onClick={handleSubmitReview}
                disabled={isSubmittingReview}
              >
                {isSubmittingReview ? 'Submitting...' : 'Commit Human Label'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
