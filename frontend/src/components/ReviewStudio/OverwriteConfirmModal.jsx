import { useEffect } from 'react'

export function OverwriteConfirmModal({
  isOpen,
  recordingId,
  currentStatus,
  newStatus,
  onConfirm,
  onCancel,
}) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isOpen) return
      if (e.key === 'Escape') {
        onCancel()
      } else if (e.key === 'Enter') {
        onConfirm()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onConfirm, onCancel])

  if (!isOpen) return null

  const getStatusLabel = (s) => {
    switch (s) {
      case 'APPROVED_NON_SCREAM': return 'Approved Non-Scream'
      case 'SCREAM_PRESENT': return 'Scream Present'
      case 'AMBIGUOUS': return 'Ambiguous'
      case 'EXCLUDED': return 'Excluded'
      case 'UNREVIEWED': return 'Unreviewed'
      default: return s || 'Unknown'
    }
  }

  return (
    <div className="modal-overlay" data-testid="overwrite-modal-overlay">
      <div className="modal-card overwrite-modal" role="dialog" aria-modal="true" aria-labelledby="overwrite-dialog-title">
        <div className="modal-header">
          <div className="modal-title-wrap">
            <div className="modal-warning-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div>
              <h3 id="overwrite-dialog-title" className="modal-title">Confirm Review Decision Overwrite</h3>
              <div className="modal-subtitle">Recording ID: <span className="font-mono">{recordingId}</span></div>
            </div>
          </div>
          <button
            type="button"
            className="btn-modal-close"
            onClick={onCancel}
            aria-label="Close dialog"
          >
            ✕
          </button>
        </div>

        <div className="modal-body">
          <p className="overwrite-dialog-desc">
            This recording has already been reviewed by a human annotator. You are about to replace the existing decision.
          </p>

          <div className="overwrite-comparison-box">
            <div className="status-change-col">
              <span className="change-label">Current Finalized Status:</span>
              <span className="status-badge badge-prev font-mono">{getStatusLabel(currentStatus)}</span>
            </div>
            <div className="change-arrow">➔</div>
            <div className="status-change-col">
              <span className="change-label">New Review Decision:</span>
              <span className="status-badge badge-new font-mono">{getStatusLabel(newStatus)}</span>
            </div>
          </div>

          <div className="audit-preservation-notice">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <span>The previous decision and reviewer notes will be permanently retained in the immutable audit log.</span>
          </div>
        </div>

        <div className="modal-footer">
          <button
            type="button"
            className="btn-secondary"
            onClick={onCancel}
          >
            Cancel [Esc]
          </button>
          <button
            type="button"
            className="btn-primary-danger"
            onClick={onConfirm}
            autoFocus
          >
            Confirm Overwrite [Enter]
          </button>
        </div>
      </div>
    </div>
  )
}
