import { useState } from 'react'

export function ReviewQueueTable({
  recordings,
  selectedId,
  onSelectRecording,
  sortBy,
  sortOrder,
  onSortChange,
  page,
  pageSize,
  totalPages,
  totalItems,
  onPageChange,
  onPageSizeChange,
  isLoading,
}) {
  const [selectedAdminIds, setSelectedAdminIds] = useState(new Set())

  const getStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED_NON_SCREAM':
        return <span className="status-badge badge-idle" title="Approved genuine non-scream">Approved</span>
      case 'SCREAM_PRESENT':
        return <span className="status-badge badge-alert" title="Scream vocalization present">Scream</span>
      case 'AMBIGUOUS':
        return <span className="status-badge badge-candidate" title="Ambiguous or borderline audio">Ambiguous</span>
      case 'EXCLUDED':
        return <span className="status-badge badge-cooldown" title="Excluded from dataset">Excluded</span>
      default:
        return <span className="status-badge badge-stopped" title="Pending human listening review">Pending</span>
    }
  }

  const getTriageBadge = (group) => {
    switch (group) {
      case 'LIKELY_NON_SCREAM':
        return <span className="triage-badge triage-likely" title="Strong alternative evidence, weak scream evidence">Likely Non-Scream</span>
      case 'POSSIBLE_SCREAM':
        return <span className="triage-badge triage-possible" title="Score ≥ 0.35 with scream tags or high prob">Possible Scream</span>
      case 'AMBIGUOUS':
        return <span className="triage-badge triage-ambiguous" title="Infant crying / mixed harmonics / near 0.35">Ambiguous</span>
      case 'REVIEW_REQUIRED':
      default:
        return <span className="triage-badge triage-required" title="Missing audio, clipping, silence, or error">Review Required</span>
    }
  }

  const getScoreBadge = (score, isAlert) => {
    if (score === null || score === undefined) {
      return <span className="score-badge score-none">Not evaluated</span>
    }
    const scorePct = (score * 100).toFixed(1)
    if (isAlert || score >= 0.35) {
      return (
        <span className="score-badge score-high" title={`Frozen model score: ${score.toFixed(4)} (Threshold: 0.35)`}>
          {scorePct}% <span className="alert-flag">ALERT</span>
        </span>
      )
    }
    return (
      <span className="score-badge score-low" title={`Frozen model score: ${score.toFixed(4)} (Threshold: 0.35)`}>
        {scorePct}%
      </span>
    )
  }

  const renderSortArrow = (columnKey) => {
    if (sortBy !== columnKey) return null
    return <span className="sort-indicator">{sortOrder === 'desc' ? ' ▼' : ' ▲'}</span>
  }

  const handleHeaderClick = (columnKey) => {
    if (sortBy === columnKey) {
      onSortChange(columnKey, sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      onSortChange(columnKey, columnKey === 'model_score' || columnKey === 'triage' ? 'desc' : 'asc')
    }
  }

  const toggleSelectAll = (e) => {
    if (e.target.checked) {
      const allIds = new Set(recordings.map((r) => r.recording_id))
      setSelectedAdminIds(allIds)
    } else {
      setSelectedAdminIds(new Set())
    }
  }

  const toggleSelectOne = (recId) => {
    const next = new Set(selectedAdminIds)
    if (next.has(recId)) {
      next.delete(recId)
    } else {
      next.add(recId)
    }
    setSelectedAdminIds(next)
  }

  const handleExportSelected = () => {
    if (selectedAdminIds.size === 0) return
    window.location.href = '/api/review/export.csv'
  }

  const allPageSelected = recordings.length > 0 && recordings.every((r) => selectedAdminIds.has(r.recording_id))

  return (
    <section className="review-queue-panel" data-testid="review-queue-panel">
      {/* Administrative Bulk Action Bar (Strictly administrative operations only) */}
      {selectedAdminIds.size > 0 && (
        <div className="admin-bulk-toolbar" data-testid="admin-bulk-toolbar">
          <div className="admin-bulk-info">
            <span className="admin-count-pill font-mono">{selectedAdminIds.size}</span>
            <span className="admin-bulk-text">Selected for administrative action</span>
          </div>
          <div className="admin-bulk-actions">
            <button
              type="button"
              className="btn-admin-export"
              onClick={handleExportSelected}
              title="Export selected candidates to CSV"
            >
              Export Selected ({selectedAdminIds.size})
            </button>
            <button
              type="button"
              className="btn-admin-clear"
              onClick={() => setSelectedAdminIds(new Set())}
            >
              Clear Selection
            </button>
          </div>
          <div className="admin-bulk-disclaimer">
            ⚠️ Administrative operations only. Automated bulk-approval based on model predictions is strictly prohibited.
          </div>
        </div>
      )}

      {/* Table Header with Sorting */}
      <div className="queue-table-wrapper">
        <table className="queue-table">
          <thead>
            <tr>
              <th className="col-checkbox" title="Administrative bulk selection only">
                <input
                  type="checkbox"
                  checked={allPageSelected}
                  onChange={toggleSelectAll}
                  aria-label="Select all recordings on this page for administrative export"
                />
              </th>
              <th
                className="col-sortable col-triage"
                onClick={() => handleHeaderClick('triage')}
                title="Click to sort by Triage Recommendation (Likely Non-Screams first)"
              >
                Triage {renderSortArrow('triage')}
              </th>
              <th
                className="col-sortable col-rec-id"
                onClick={() => handleHeaderClick('recording_id')}
                title="Click to sort by Recording ID"
              >
                Recording ID {renderSortArrow('recording_id')}
              </th>
              <th
                className="col-sortable col-category"
                onClick={() => handleHeaderClick('category')}
                title="Click to sort by Sound Category"
              >
                Category {renderSortArrow('category')}
              </th>
              <th
                className="col-sortable col-source"
                onClick={() => handleHeaderClick('source')}
                title="Click to sort by Source Provider"
              >
                Source / Lic {renderSortArrow('source')}
              </th>
              <th
                className="col-sortable col-score"
                onClick={() => handleHeaderClick('model_score')}
                title="Click to sort by Model Score"
              >
                Score (0.35) {renderSortArrow('model_score')}
              </th>
              <th
                className="col-sortable col-status"
                onClick={() => handleHeaderClick('status')}
                title="Click to sort by Review Status"
              >
                Status {renderSortArrow('status')}
              </th>
              <th
                className="col-sortable col-duration"
                onClick={() => handleHeaderClick('duration')}
                title="Click to sort by Duration"
              >
                Dur {renderSortArrow('duration')}
              </th>
              <th className="col-audio">Audio</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan="9" className="queue-empty-cell">
                  <div className="queue-loading-state">
                    <span className="spinner-sm" /> Loading candidate recordings...
                  </div>
                </td>
              </tr>
            ) : recordings.length === 0 ? (
              <tr>
                <td colSpan="9" className="queue-empty-cell">
                  <div className="queue-empty-state">
                    <p>No candidate recordings match the active filters.</p>
                    <span className="empty-sub">Try broadening your search term or clearing filter criteria.</span>
                  </div>
                </td>
              </tr>
            ) : (
              recordings.map((item) => {
                const isSelected = item.recording_id === selectedId
                const isAdminChecked = selectedAdminIds.has(item.recording_id)
                return (
                  <tr
                    key={item.recording_id}
                    className={`queue-row ${isSelected ? 'row-selected' : ''}`}
                    onClick={() => onSelectRecording(item.recording_id)}
                    tabIndex="0"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') onSelectRecording(item.recording_id)
                    }}
                  >
                    <td className="col-checkbox" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isAdminChecked}
                        onChange={() => toggleSelectOne(item.recording_id)}
                        aria-label={`Select ${item.recording_id} for administrative export`}
                      />
                    </td>
                    <td className="col-triage">
                      {getTriageBadge(item.triage_group)}
                    </td>
                    <td className="col-rec-id font-mono font-bold">
                      <div className="rec-id-text">{item.recording_id}</div>
                    </td>
                    <td className="col-category">
                      <span className="category-pill" title={item.proposed_category}>
                        {item.proposed_category ? item.proposed_category.replace(/_/g, ' ') : 'Unspecified'}
                      </span>
                    </td>
                    <td className="col-source">
                      <div className="source-info">
                        <span className="source-name">{item.source_provider}</span>
                        <span className="lic-sub font-mono">{item.commercial_compatibility || 'UNKNOWN'}</span>
                      </div>
                    </td>
                    <td className="col-score font-mono">
                      {getScoreBadge(item.model_score, item.model_alert)}
                    </td>
                    <td className="col-status">
                      {getStatusBadge(item.review_status)}
                    </td>
                    <td className="col-duration font-mono text-muted">
                      {item.duration_seconds ? `${item.duration_seconds.toFixed(1)}s` : '—'}
                    </td>
                    <td className="col-audio">
                      {item.has_audio ? (
                        <span className="audio-avail-badge avail-yes" title="Audio on local disk">● Local</span>
                      ) : (
                        <span className="audio-avail-badge avail-no" title="Audio not downloaded">○ None</span>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="queue-pagination-bar">
        <div className="pagination-info">
          Showing <span className="font-mono">{recordings.length > 0 ? (page - 1) * pageSize + 1 : 0}</span> to{' '}
          <span className="font-mono">{Math.min(page * pageSize, totalItems)}</span> of{' '}
          <span className="font-mono">{totalItems}</span> items
        </div>

        <div className="pagination-controls">
          <div className="page-size-select-wrap">
            <label htmlFor="select-page-size" className="page-size-label">Per page:</label>
            <select
              id="select-page-size"
              value={pageSize}
              onChange={(e) => onPageSizeChange(parseInt(e.target.value, 10))}
              className="page-size-select"
            >
              <option value="15">15</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>

          <button
            type="button"
            className="btn-page-nav"
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1 || isLoading}
            aria-label="Previous page"
          >
            ◀ Prev
          </button>

          <span className="page-current font-mono">
            {page} / {totalPages || 1}
          </span>

          <button
            type="button"
            className="btn-page-nav"
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages || isLoading}
            aria-label="Next page"
          >
            Next ▶
          </button>
        </div>
      </div>
    </section>
  )
}
