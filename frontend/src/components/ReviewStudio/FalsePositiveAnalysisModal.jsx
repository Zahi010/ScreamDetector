import { useState, useEffect, useCallback, useMemo, useRef } from 'react'

export function FalsePositiveAnalysisModal({
  isOpen,
  onClose,
  onSelectRecording,
}) {
  const [report, setReport] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [errorMsg, setErrorMsg] = useState(null)
  const [statusMsg, setStatusMsg] = useState(null)

  // Filtering states for the error list
  const [errorFilter, setErrorFilter] = useState('all_errors') // 'all_errors' | 'FP' | 'FN' | 'AMBIGUOUS'
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedSource, setSelectedSource] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Audio playback state
  const [playingId, setPlayingId] = useState(null)
  const audioRef = useRef(null)

  // Fetch live evaluation report
  const fetchReport = useCallback(async () => {
    setIsLoading(true)
    setErrorMsg(null)
    try {
      const res = await fetch('/api/review/evaluation/report')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setReport(data)
    } catch (err) {
      console.error('Failed to load evaluation report:', err)
      setErrorMsg(`Failed to load evaluation report: ${err.message}`)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isOpen) {
      fetchReport()
    } else {
      // Pause audio on close
      if (audioRef.current) {
        audioRef.current.pause()
        setPlayingId(null)
      }
    }
  }, [isOpen, fetchReport])

  // Re-run evaluation
  const handleRunEvaluation = async () => {
    setIsEvaluating(true)
    setErrorMsg(null)
    setStatusMsg('Running frozen classifier inference on reviewed recordings...')
    try {
      const res = await fetch('/api/review/evaluation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force_reevaluate: false }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const resData = await res.json()
      setStatusMsg(
        `Inference finished: ${resData.evaluated_count} newly evaluated, ${resData.failed_count} failures.`
      )
      await fetchReport()
    } catch (err) {
      console.error('Evaluation run error:', err)
      setErrorMsg(`Evaluation run error: ${err.message}`)
    } finally {
      setIsEvaluating(false)
    }
  }

  // Audio playback toggle
  const togglePlayAudio = (recId) => {
    if (playingId === recId) {
      if (audioRef.current) {
        audioRef.current.pause()
      }
      setPlayingId(null)
    } else {
      setPlayingId(recId)
      if (audioRef.current) {
        audioRef.current.src = `/api/review/recordings/${recId}/audio`
        audioRef.current.play().catch((err) => {
          console.warn('Playback error:', err)
          setPlayingId(null)
        })
      }
    }
  }

  // Export CSV
  const handleExportCSV = () => {
    window.location.href = '/api/review/evaluation/export.csv'
  }

  // Extract combined list of items for table
  const combinedErrorItems = useMemo(() => {
    if (!report) return []
    const fps = report.false_positives || []
    const fns = report.false_negatives || []
    const amb = report.ambiguous_records || []

    let list = []
    if (errorFilter === 'FP') {
      list = fps
    } else if (errorFilter === 'FN') {
      list = fns
    } else if (errorFilter === 'AMBIGUOUS') {
      list = amb
    } else {
      list = [...fps, ...fns]
    }

    return list.filter((item) => {
      if (selectedCategory !== 'all' && item.proposed_category !== selectedCategory) {
        return false
      }
      if (selectedSource !== 'all' && item.source_provider !== selectedSource) {
        return false
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const idMatch = item.recording_id.toLowerCase().includes(q)
        const titleMatch = (item.original_title || '').toLowerCase().includes(q)
        const notesMatch = (item.reviewer_notes || '').toLowerCase().includes(q)
        if (!idMatch && !titleMatch && !notesMatch) return false
      }
      return true
    })
  }, [report, errorFilter, selectedCategory, selectedSource, searchQuery])

  if (!isOpen) return null

  const binary = report?.binary_evaluation
  const cm = binary?.confusion_matrix
  const metrics = binary?.metrics
  const meta = report?.model_metadata
  const audit = report?.dataset_audit
  const lim = binary?.statistical_limitation

  return (
    <div className="recovery-modal-backdrop" onClick={onClose} data-testid="fp-analysis-modal">
      <div
        className="recovery-modal-container fp-modal-container"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Hidden shared audio player */}
        <audio
          ref={audioRef}
          onEnded={() => setPlayingId(null)}
          onError={() => setPlayingId(null)}
        />

        {/* Modal Header */}
        <div className="recovery-modal-header">
          <div className="recovery-modal-title-wrap">
            <span className="badge-pill-cyan">STAGE 8.9.3</span>
            <h3 className="recovery-modal-title">Human-Verified False-Positive Analysis</h3>
            <span className="fp-threshold-tag font-mono">
              Frozen Classifier &bull; Threshold: {meta?.operating_threshold ?? 0.35} &bull; SHA-256: {meta?.classifier_hash?.slice(0, 10)}...
            </span>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        {/* Modal Content Body */}
        <div className="recovery-modal-body">
          {errorMsg && (
            <div className="recovery-alert-banner alert-error">
              <span>⚠️ {errorMsg}</span>
            </div>
          )}

          {statusMsg && (
            <div className="recovery-alert-banner alert-info">
              <span>ℹ️ {statusMsg}</span>
            </div>
          )}

          {isLoading && (
            <div className="fp-loading-state">
              <span className="spinner-sm" /> Loading live evaluation metrics...
            </div>
          )}

          {report && (
            <>
              {/* Statistical Limitation Caveat Banner */}
              {lim?.flagged && (
                <div className="fp-limitation-banner" data-testid="statistical-limitation-banner">
                  <div className="fp-limitation-icon">⚠️</div>
                  <div className="fp-limitation-text">
                    <strong>Statistical Sample Size Notice:</strong> {lim.message}
                    <div className="fp-limitation-stats font-mono">
                      Ground Truth Class Distribution: Positive Screams N = {lim.positive_count} | Negative Non-Screams N = {lim.negative_count} | Ambiguous Excluded N = {binary.excluded_ambiguous_count}
                    </div>
                  </div>
                </div>
              )}

              {/* Top Metrics Cards Grid */}
              <div className="fp-metrics-grid">
                <div className="fp-metric-card card-primary">
                  <div className="fp-metric-label">Evaluated Candidates</div>
                  <div className="fp-metric-val font-mono">{binary?.total_binary_evaluated}</div>
                  <div className="fp-metric-sub">Human verified (excl. 3 ambiguous)</div>
                </div>

                <div className="fp-metric-card card-specificity">
                  <div className="fp-metric-label">Specificity (TNR)</div>
                  <div className="fp-metric-val font-mono text-emerald">
                    {metrics ? `${(metrics.specificity * 100).toFixed(2)}%` : '--'}
                  </div>
                  <div className="fp-metric-sub">{cm?.true_negatives} of {binary?.negative_count_approved} correctly silent</div>
                </div>

                <div className="fp-metric-card card-fpr">
                  <div className="fp-metric-label">False Positive Rate (FPR)</div>
                  <div className="fp-metric-val font-mono text-amber">
                    {metrics ? `${(metrics.false_positive_rate * 100).toFixed(2)}%` : '--'}
                  </div>
                  <div className="fp-metric-sub">{cm?.false_positives} approved non-screams alarmed</div>
                </div>

                <div className="fp-metric-card card-accuracy">
                  <div className="fp-metric-label">Accuracy</div>
                  <div className="fp-metric-val font-mono">
                    {metrics ? `${(metrics.accuracy * 100).toFixed(2)}%` : '--'}
                  </div>
                  <div className="fp-metric-sub">{cm?.true_positives + cm?.true_negatives} correct predictions</div>
                </div>

                <div className="fp-metric-card card-auc">
                  <div className="fp-metric-label">ROC-AUC / PR-AUC</div>
                  <div className="fp-metric-val font-mono">
                    {metrics?.roc_auc?.toFixed(4) ?? 'N/A'} / {metrics?.pr_auc?.toFixed(4) ?? 'N/A'}
                  </div>
                  <div className="fp-metric-sub">Continuous discrimination curves</div>
                </div>

                <div className="fp-metric-card card-precision-recall">
                  <div className="fp-metric-label">Recall / Precision</div>
                  <div className="fp-metric-val font-mono">
                    {metrics ? `${(metrics.recall_sensitivity * 100).toFixed(1)}%` : '--'} / {metrics ? `${(metrics.precision * 100).toFixed(1)}%` : '--'}
                  </div>
                  <div className="fp-metric-sub">TP: {cm?.true_positives} | FN: {cm?.false_negatives} (Wide CI)</div>
                </div>
              </div>

              {/* Interactive Confusion Matrix Section */}
              <div className="fp-cm-section">
                <div className="fp-section-header">
                  <h4 className="fp-section-title">Confusion Matrix (Human Decisions vs Frozen Model @ 0.35)</h4>
                  <span className="fp-section-hint">Click a quadrant to filter error recordings below</span>
                </div>

                <div className="confusion-matrix-container">
                  <div className="cm-header-row">
                    <div className="cm-cell-blank" />
                    <div className="cm-col-label">Predicted Scream (≥ 0.35)</div>
                    <div className="cm-col-label">Predicted Non-Scream (&lt; 0.35)</div>
                  </div>

                  <div className="cm-grid-row">
                    <div className="cm-row-label">Ground Truth: Scream Present (N = {binary?.positive_count_scream})</div>
                    <div
                      className="cm-quadrant cm-tp"
                      title="True Positive: Scream detected correctly"
                    >
                      <div className="cm-q-label">True Positive (TP)</div>
                      <div className="cm-q-val font-mono">{cm?.true_positives}</div>
                      <div className="cm-q-desc">Correct Alarm</div>
                    </div>
                    <div
                      className={`cm-quadrant cm-fn clickable-quadrant ${errorFilter === 'FN' ? 'quadrant-active' : ''}`}
                      onClick={() => setErrorFilter('FN')}
                      title="False Negative: Scream missed by model"
                    >
                      <div className="cm-q-label">False Negative (FN)</div>
                      <div className="cm-q-val font-mono text-alert">{cm?.false_negatives}</div>
                      <div className="cm-q-desc">Missed Threat (Click to filter)</div>
                    </div>
                  </div>

                  <div className="cm-grid-row">
                    <div className="cm-row-label">Ground Truth: Approved Non-Scream (N = {binary?.negative_count_approved})</div>
                    <div
                      className={`cm-quadrant cm-fp clickable-quadrant ${errorFilter === 'FP' ? 'quadrant-active' : ''}`}
                      onClick={() => setErrorFilter('FP')}
                      title="False Positive: Non-scream triggered false alarm"
                    >
                      <div className="cm-q-label">False Positive (FP)</div>
                      <div className="cm-q-val font-mono text-amber">{cm?.false_positives}</div>
                      <div className="cm-q-desc">False Alarms (Click to filter)</div>
                    </div>
                    <div
                      className="cm-quadrant cm-tn"
                      title="True Negative: Non-scream correctly silent"
                    >
                      <div className="cm-q-label">True Negative (TN)</div>
                      <div className="cm-q-val font-mono text-emerald">{cm?.true_negatives}</div>
                      <div className="cm-q-desc">Correct Silence</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* False Positive Breakdown by Sound Category & Source */}
              <div className="fp-breakdown-row">
                {/* Category Table */}
                <div className="fp-breakdown-box">
                  <h4 className="fp-breakdown-heading">False Positives by Sound Category</h4>
                  <div className="fp-table-wrapper">
                    <table className="fp-table font-mono">
                      <thead>
                        <tr>
                          <th>Category</th>
                          <th>Total</th>
                          <th>FP</th>
                          <th>TN</th>
                          <th>FPR</th>
                          <th>Mean Prob</th>
                        </tr>
                      </thead>
                      <tbody>
                        {report.category_breakdown?.map((cat) => (
                          <tr
                            key={cat.category}
                            className={cat.false_positives > 0 ? 'row-has-fp' : ''}
                            onClick={() => {
                              setSelectedCategory(cat.category)
                              setErrorFilter('FP')
                            }}
                            title={`Filter errors by ${cat.category}`}
                          >
                            <td className="text-left font-sans">{cat.category.replace(/_/g, ' ')}</td>
                            <td>{cat.total_evaluated}</td>
                            <td className={cat.false_positives > 0 ? 'text-amber font-bold' : ''}>
                              {cat.false_positives}
                            </td>
                            <td className="text-muted">{cat.true_negatives}</td>
                            <td>{(cat.false_positive_rate * 100).toFixed(1)}%</td>
                            <td>{cat.mean_score.toFixed(3)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Source Provider Table */}
                <div className="fp-breakdown-box">
                  <h4 className="fp-breakdown-heading">False Positives by Source</h4>
                  <div className="fp-table-wrapper">
                    <table className="fp-table font-mono">
                      <thead>
                        <tr>
                          <th>Source</th>
                          <th>Total</th>
                          <th>FP</th>
                          <th>TN</th>
                          <th>FPR</th>
                        </tr>
                      </thead>
                      <tbody>
                        {report.source_breakdown?.map((src) => (
                          <tr
                            key={src.source}
                            className={src.false_positives > 0 ? 'row-has-fp' : ''}
                            onClick={() => {
                              setSelectedSource(src.source)
                              setErrorFilter('FP')
                            }}
                            title={`Filter errors by ${src.source}`}
                          >
                            <td className="text-left font-sans">{src.source}</td>
                            <td>{src.total_evaluated}</td>
                            <td className={src.false_positives > 0 ? 'text-amber font-bold' : ''}>
                              {src.false_positives}
                            </td>
                            <td className="text-muted">{src.true_negatives}</td>
                            <td>{(src.false_positive_rate * 100).toFixed(1)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              {/* Error Recordings Explorer & Audio Playback */}
              <div className="fp-explorer-section">
                <div className="fp-explorer-header">
                  <div className="fp-tabs-wrap">
                    <button
                      type="button"
                      className={`fp-tab-btn ${errorFilter === 'all_errors' ? 'tab-active' : ''}`}
                      onClick={() => setErrorFilter('all_errors')}
                    >
                      All Classification Errors ({cm?.false_positives + cm?.false_negatives})
                    </button>
                    <button
                      type="button"
                      className={`fp-tab-btn ${errorFilter === 'FP' ? 'tab-active' : ''}`}
                      onClick={() => setErrorFilter('FP')}
                    >
                      False Positives ({cm?.false_positives})
                    </button>
                    <button
                      type="button"
                      className={`fp-tab-btn ${errorFilter === 'FN' ? 'tab-active' : ''}`}
                      onClick={() => setErrorFilter('FN')}
                    >
                      False Negatives ({cm?.false_negatives})
                    </button>
                    <button
                      type="button"
                      className={`fp-tab-btn ${errorFilter === 'AMBIGUOUS' ? 'tab-active' : ''}`}
                      onClick={() => setErrorFilter('AMBIGUOUS')}
                    >
                      Ambiguous Decisions ({binary?.excluded_ambiguous_count})
                    </button>
                  </div>

                  {/* Filter Selectors */}
                  <div className="fp-filter-controls">
                    <select
                      className="fp-select"
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      <option value="all">All Categories</option>
                      {report.category_breakdown?.map((c) => (
                        <option key={c.category} value={c.category}>
                          {c.category.replace(/_/g, ' ')} ({c.false_positives} FPs)
                        </option>
                      ))}
                    </select>

                    <select
                      className="fp-select"
                      value={selectedSource}
                      onChange={(e) => setSelectedSource(e.target.value)}
                    >
                      <option value="all">All Sources</option>
                      {report.source_breakdown?.map((s) => (
                        <option key={s.source} value={s.source}>
                          {s.source} ({s.false_positives} FPs)
                        </option>
                      ))}
                    </select>

                    <input
                      type="text"
                      className="fp-search-input"
                      placeholder="Search ID or title..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />

                    {(selectedCategory !== 'all' || selectedSource !== 'all' || searchQuery || errorFilter !== 'all_errors') && (
                      <button
                        type="button"
                        className="btn-preset-clear"
                        onClick={() => {
                          setSelectedCategory('all')
                          setSelectedSource('all')
                          setSearchQuery('')
                          setErrorFilter('all_errors')
                        }}
                      >
                        Reset
                      </button>
                    )}
                  </div>
                </div>

                {/* Error Items List Table */}
                <div className="fp-error-list-wrap">
                  {combinedErrorItems.length === 0 ? (
                    <div className="fp-empty-errors">
                      No matching recordings found for the selected filter combination.
                    </div>
                  ) : (
                    <div className="fp-error-cards-list">
                      {combinedErrorItems.map((item) => {
                        const isPlaying = playingId === item.recording_id
                        return (
                          <div
                            key={item.recording_id}
                            className={`fp-error-item-card ${isPlaying ? 'card-playing' : ''}`}
                            data-testid={`fp-item-${item.recording_id}`}
                          >
                            <div className="fp-error-item-main">
                              {/* Audio Playback Button */}
                              <button
                                type="button"
                                className={`fp-play-btn ${isPlaying ? 'btn-is-playing' : ''}`}
                                onClick={() => togglePlayAudio(item.recording_id)}
                                title={isPlaying ? 'Pause Audio' : 'Listen to Audio'}
                              >
                                {isPlaying ? (
                                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                                    <rect x="6" y="4" width="4" height="16"></rect>
                                    <rect x="14" y="4" width="4" height="16"></rect>
                                  </svg>
                                ) : (
                                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                                  </svg>
                                )}
                              </button>

                              {/* Details Block */}
                              <div className="fp-item-info">
                                <div className="fp-item-header">
                                  <span className="fp-item-id font-mono">{item.recording_id}</span>
                                  <span className="fp-item-source font-mono">{item.source_provider}</span>
                                  <span className="fp-item-category">
                                    {item.proposed_category?.replace(/_/g, ' ')}
                                  </span>
                                  <span className="fp-item-duration font-mono">{item.duration_seconds.toFixed(1)}s</span>
                                </div>
                                <div className="fp-item-title" title={item.original_title}>
                                  {item.original_title || 'Untitled recording'}
                                </div>
                                {item.reviewer_notes && (
                                  <div className="fp-item-notes">
                                    📝 <em>"{item.reviewer_notes}"</em>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Classification Badges */}
                            <div className="fp-error-item-outcomes">
                              <div className="outcome-pill-group">
                                <span className="outcome-label">Human Ground Truth:</span>
                                <span className={`badge-pill ${item.human_label === 'APPROVED_NON_SCREAM' ? 'badge-pill-emerald' : (item.human_label === 'SCREAM_PRESENT' ? 'badge-pill-alert' : 'badge-pill-amber')}`}>
                                  {item.human_label}
                                </span>
                              </div>

                              <div className="outcome-pill-group">
                                <span className="outcome-label">Model Prediction (@0.35):</span>
                                <span className={`badge-pill ${item.model_alert ? 'badge-pill-alert font-mono' : 'badge-pill-neutral font-mono'}`}>
                                  {item.predicted_label} ({item.model_score !== null ? (item.model_score * 100).toFixed(1) + '%' : 'N/A'})
                                </span>
                              </div>

                              <div className="outcome-pill-group">
                                <span className="outcome-label">Error Outcome:</span>
                                <span className={`badge-pill-bold ${item.classification_outcome === 'FP' ? 'pill-fp' : (item.classification_outcome === 'FN' ? 'pill-fn' : 'pill-ambiguous')}`}>
                                  {item.classification_outcome || item.human_label}
                                </span>
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Modal Footer Toolbar */}
        <div className="recovery-modal-footer fp-modal-footer">
          <div className="fp-footer-status">
            <span>Audit: 370 total candidates &bull; {audit?.audio_available} available &bull; {audit?.missing_model_scores} missing scores (unacquired) &bull; 0 reviewed missing</span>
          </div>

          <div className="fp-footer-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={handleRunEvaluation}
              disabled={isEvaluating}
              title="Evaluate any newly acquired or unscored reviewed audio recordings"
            >
              {isEvaluating ? (
                <>
                  <span className="spinner-sm" /> Running Inference...
                </>
              ) : (
                <>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <polyline points="1 20 1 14 7 14"></polyline>
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                  </svg>
                  Re-evaluate Unscored
                </>
              )}
            </button>

            <button
              type="button"
              className="btn-action-recovery"
              onClick={handleExportCSV}
              title="Export complete evaluation dataset with human labels, model scores, threshold, and errors as CSV"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              Export Evaluation CSV
            </button>

            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
