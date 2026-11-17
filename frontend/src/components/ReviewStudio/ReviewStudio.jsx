import { useState, useEffect, useCallback, useMemo } from 'react'
import { ReviewSummaryCards } from './ReviewSummaryCards'
import { ReviewFilters } from './ReviewFilters'
import { ReviewQueueTable } from './ReviewQueueTable'
import { ReviewDetailPanel } from './ReviewDetailPanel'
import { OverwriteConfirmModal } from './OverwriteConfirmModal'
import { MissingAudioRecoveryPanel } from './MissingAudioRecoveryPanel'
import { FalsePositiveAnalysisModal } from './FalsePositiveAnalysisModal'

export function ReviewStudio() {
  // Global summary state
  const [summary, setSummary] = useState(null)
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [isTriaging, setIsTriaging] = useState(false)
  const [isRecoveryOpen, setIsRecoveryOpen] = useState(false)
  const [isEvaluationOpen, setIsEvaluationOpen] = useState(false)
  const [feedbackMsg, setFeedbackMsg] = useState(null)

  // Filters state (persisted in session)
  const [filters, setFilters] = useState(() => {
    try {
      const saved = localStorage.getItem('review_filters')
      return saved ? JSON.parse(saved) : {
        category: 'all',
        source: 'all',
        license: 'all',
        status: 'all',
        triage_group: 'all',
        audio: 'all',
        score_filter: 'all',
        search: '',
      }
    } catch {
      return {
        category: 'all',
        source: 'all',
        license: 'all',
        status: 'all',
        triage_group: 'all',
        audio: 'all',
        score_filter: 'all',
        search: '',
      }
    }
  })

  // Sorting & Pagination state
  const [sortBy, setSortBy] = useState('priority')
  const [sortOrder, setSortOrder] = useState('asc')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  // Queue recordings list state
  const [recordings, setRecordings] = useState([])
  const [totalItems, setTotalItems] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoadingQueue, setIsLoadingQueue] = useState(false)

  // Selected recording & detail state
  const [selectedId, setSelectedId] = useState(null)
  const [selectedRecording, setSelectedRecording] = useState(null)
  const [recordingHistory, setRecordingHistory] = useState([])
  const [isSavingDecision, setIsSavingDecision] = useState(false)

  // Auto-advance preference
  const [autoAdvance, setAutoAdvance] = useState(() => {
    return localStorage.getItem('review_auto_advance') !== 'false'
  })

  // Overwrite confirmation modal state
  const [pendingOverwrite, setPendingOverwrite] = useState(null)

  // Save filters to localStorage
  useEffect(() => {
    localStorage.setItem('review_filters', JSON.stringify(filters))
  }, [filters])

  // Save autoAdvance preference
  const handleToggleAutoAdvance = (val) => {
    setAutoAdvance(val)
    localStorage.setItem('review_auto_advance', val ? 'true' : 'false')
  }

  // Fetch summary counters
  const fetchSummary = useCallback(async () => {
    try {
      const res = await fetch('/api/review/summary')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setSummary(data)
    } catch (err) {
      console.error('Failed to load review summary:', err)
    }
  }, [])

  // Fetch queue recordings with current filters
  const fetchRecordings = useCallback(async () => {
    setIsLoadingQueue(true)
    try {
      const params = new URLSearchParams()
      if (filters.category && filters.category !== 'all') params.append('category', filters.category)
      if (filters.source && filters.source !== 'all') params.append('source', filters.source)
      if (filters.license && filters.license !== 'all') params.append('license', filters.license)
      if (filters.status && filters.status !== 'all') params.append('status', filters.status)
      if (filters.triage_group && filters.triage_group !== 'all') params.append('triage_group', filters.triage_group)
      if (filters.audio && filters.audio !== 'all') params.append('audio', filters.audio)
      if (filters.score_filter && filters.score_filter !== 'all') params.append('score_filter', filters.score_filter)
      if (filters.search && filters.search.trim()) params.append('search', filters.search.trim())

      params.append('sort_by', sortBy)
      params.append('sort_order', sortOrder)
      params.append('page', page.toString())
      params.append('page_size', pageSize.toString())

      const res = await fetch(`/api/review/recordings?${params.toString()}`)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()

      setRecordings(data.items || [])
      setTotalItems(data.total || 0)
      setTotalPages(data.total_pages || 1)

      // If nothing selected or selected item is no longer in page, select first
      if (data.items && data.items.length > 0) {
        if (!selectedId || !data.items.some(r => r.recording_id === selectedId)) {
          setSelectedId(data.items[0].recording_id)
        }
      } else {
        setSelectedId(null)
      }
    } catch (err) {
      console.error('Failed to fetch recordings:', err)
      setRecordings([])
    } finally {
      setIsLoadingQueue(false)
    }
  }, [filters, sortBy, sortOrder, page, pageSize, selectedId])

  // Fetch selected recording details and audit history
  const fetchSelectedDetail = useCallback(async (recId) => {
    if (!recId) {
      setSelectedRecording(null)
      setRecordingHistory([])
      return
    }
    try {
      const [resDetail, resHist] = await Promise.all([
        fetch(`/api/review/recordings/${recId}`),
        fetch(`/api/review/recordings/${recId}/history`),
      ])

      if (resDetail.ok) {
        const detailData = await resDetail.json()
        setSelectedRecording(detailData)
      }
      if (resHist.ok) {
        const histData = await resHist.json()
        setRecordingHistory(histData.history || [])
      }
    } catch (err) {
      console.error(`Failed to fetch details for ${recId}:`, err)
    }
  }, [])

  // Initial load
  useEffect(() => {
    fetchSummary()
  }, [fetchSummary])

  useEffect(() => {
    fetchRecordings()
  }, [fetchRecordings])

  useEffect(() => {
    if (selectedId) {
      fetchSelectedDetail(selectedId)
    } else {
      setSelectedRecording(null)
      setRecordingHistory([])
    }
  }, [selectedId, fetchSelectedDetail])

  // Current queue index calculations for next/prev
  const currentIndex = useMemo(() => {
    if (!selectedId || !recordings.length) return -1
    return recordings.findIndex(r => r.recording_id === selectedId)
  }, [selectedId, recordings])

  const hasPrevClip = currentIndex > 0
  const hasNextClip = currentIndex >= 0 && currentIndex < recordings.length - 1

  const handlePrevClip = useCallback(() => {
    if (hasPrevClip) {
      setSelectedId(recordings[currentIndex - 1].recording_id)
    }
  }, [hasPrevClip, currentIndex, recordings])

  const handleNextClip = useCallback(() => {
    if (hasNextClip) {
      setSelectedId(recordings[currentIndex + 1].recording_id)
    }
  }, [hasNextClip, currentIndex, recordings])

  // Submit decision execution
  const executeDecisionSubmission = async (decision, reasonCode, notes, confirmOverwrite = false) => {
    if (!selectedId) return

    setIsSavingDecision(true)
    try {
      const res = await fetch(`/api/review/recordings/${selectedId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          reason_code: reasonCode || null,
          notes: notes || null,
          reviewer: 'human_reviewer',
          confirm_overwrite: confirmOverwrite,
        }),
      })

      if (res.status === 409) {
        // Confirmation required
        const errData = await res.json()
        setPendingOverwrite({
          recordingId: selectedId,
          currentStatus: errData.detail?.current_status || selectedRecording?.review_status || 'REVIEWED',
          newStatus: decision,
          reasonCode,
          notes,
        })
        setIsSavingDecision(false)
        return
      }

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || `HTTP ${res.status}`)
      }

      const data = await res.json()
      const updatedRec = data.recording

      // Update selected recording
      setSelectedRecording(updatedRec)

      // Update in local queue list
      setRecordings(prev => prev.map(item => item.recording_id === updatedRec.recording_id ? updatedRec : item))

      // Refresh summary counters
      await fetchSummary()

      // Refresh audit history
      await fetchSelectedDetail(selectedId)

      // Feedback message
      setFeedbackMsg({
        type: 'success',
        text: `Recorded decision: ${decision.replace(/_/g, ' ')} for ${selectedId}`,
      })
      setTimeout(() => setFeedbackMsg(null), 3500)

      // Auto-advance to next clip if enabled
      if (autoAdvance && hasNextClip) {
        handleNextClip()
      }
    } catch (err) {
      console.error('Failed to submit review decision:', err)
      setFeedbackMsg({
        type: 'error',
        text: `Error saving decision: ${err.message}`,
      })
      setTimeout(() => setFeedbackMsg(null), 5000)
    } finally {
      setIsSavingDecision(false)
    }
  }

  // Handle Save Decision click
  const handleSaveDecision = (decision, reasonCode, notes) => {
    if (!selectedRecording) return

    const currentStatus = selectedRecording.review_status
    // Check if overwrite confirmation is needed
    if (currentStatus && currentStatus !== 'UNREVIEWED' && currentStatus !== decision) {
      setPendingOverwrite({
        recordingId: selectedRecording.recording_id,
        currentStatus,
        newStatus: decision,
        reasonCode,
        notes,
      })
      return
    }

    executeDecisionSubmission(decision, reasonCode, notes, false)
  }

  // Confirm Overwrite Modal handler
  const handleConfirmOverwrite = () => {
    if (!pendingOverwrite) return
    const { newStatus, reasonCode, notes } = pendingOverwrite
    setPendingOverwrite(null)
    executeDecisionSubmission(newStatus, reasonCode, notes, true)
  }

  // Trigger explicit evaluation of local audio
  const handleTriggerEvaluation = async () => {
    setIsEvaluating(true)
    try {
      const res = await fetch('/api/review/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batch_size: 100, only_missing: true }),
      })
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()

      setFeedbackMsg({
        type: 'success',
        text: `Successfully evaluated ${data.evaluated_count} clips (${data.alerts_count} candidate alerts at 0.35).`,
      })
      setTimeout(() => setFeedbackMsg(null), 5000)

      // Refresh summary and queue
      await fetchSummary()
      await fetchRecordings()
      if (selectedId) await fetchSelectedDetail(selectedId)
    } catch (err) {
      console.error('Evaluation failed:', err)
      setFeedbackMsg({
        type: 'error',
        text: `Evaluation failed: ${err.message}`,
      })
      setTimeout(() => setFeedbackMsg(null), 5000)
    } finally {
      setIsEvaluating(false)
    }
  }

  // Trigger automated hard-negative triage analysis (YAMNet + frozen 0.35)
  const handleTriggerTriage = async () => {
    setIsTriaging(true)
    try {
      const res = await fetch('/api/review/triage/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batch_size: 500, only_untriaged: false }),
      })
      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || `HTTP ${res.status}`)
      }
      const data = await res.json()

      setFeedbackMsg({
        type: 'success',
        text: `Automated triage complete: ${data.triaged_count} clips categorized (${data.triage_counts?.LIKELY_NON_SCREAM || 0} likely non-screams).`,
      })
      setTimeout(() => setFeedbackMsg(null), 5000)

      await fetchSummary()
      await fetchRecordings()
      if (selectedId) await fetchSelectedDetail(selectedId)
    } catch (err) {
      console.error('Triage run failed:', err)
      setFeedbackMsg({
        type: 'error',
        text: `Triage run failed: ${err.message}`,
      })
      setTimeout(() => setFeedbackMsg(null), 5000)
    } finally {
      setIsTriaging(false)
    }
  }

  // Filter change handlers
  const handleChangeFilter = (key, val) => {
    setFilters(prev => ({ ...prev, [key]: val }))
    setPage(1) // Reset to first page
  }

  const handleApplyPreset = (preset) => {
    const nextFilters = { ...filters }
    let nextSortBy = sortBy
    let nextSortOrder = sortOrder

    Object.entries(preset).forEach(([k, v]) => {
      if (k === 'sort_by') {
        nextSortBy = v
      } else if (k === 'sort_order') {
        nextSortOrder = v
      } else {
        nextFilters[k] = v
      }
    })

    setFilters(nextFilters)
    setSortBy(nextSortBy)
    setSortOrder(nextSortOrder)
    setPage(1)
  }

  const handleResetFilters = () => {
    setFilters({
      category: 'all',
      source: 'all',
      license: 'all',
      status: 'all',
      triage_group: 'all',
      audio: 'all',
      score_filter: 'all',
      search: '',
    })
    setPage(1)
  }

  // Sort change handler
  const handleSortChange = (newSortBy, newSortOrder) => {
    setSortBy(newSortBy)
    setSortOrder(newSortOrder)
  }

  // Keyboard shortcut listener
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Do not trigger shortcuts if user is currently typing in an input or textarea
      const tag = document.activeElement?.tagName
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') {
        return
      }

      if (e.key === 'ArrowLeft') {
        e.preventDefault()
        handlePrevClip()
      } else if (e.key === 'ArrowRight') {
        e.preventDefault()
        handleNextClip()
      } else if (e.key === '1') {
        e.preventDefault()
        handleSaveDecision('APPROVED_NON_SCREAM', '', selectedRecording?.reviewer_notes || '')
      } else if (e.key === '2') {
        e.preventDefault()
        handleSaveDecision('SCREAM_PRESENT', '', selectedRecording?.reviewer_notes || '')
      } else if (e.key === '3') {
        e.preventDefault()
        handleSaveDecision('AMBIGUOUS', '', selectedRecording?.reviewer_notes || '')
      } else if (e.key === '4') {
        e.preventDefault()
        handleSaveDecision('EXCLUDED', '', selectedRecording?.reviewer_notes || '')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handlePrevClip, handleNextClip, handleSaveDecision, selectedRecording])

  return (
    <div className="review-studio-container" data-testid="review-studio">
      {/* Feedback Banner */}
      {feedbackMsg && (
        <div className={`review-feedback-banner feedback-${feedbackMsg.type}`}>
          <span>{feedbackMsg.text}</span>
          <button
            type="button"
            className="btn-feedback-dismiss"
            onClick={() => setFeedbackMsg(null)}
          >
            ✕
          </button>
        </div>
      )}

      {/* Top 10 Summary Cards & Action Bar */}
      <ReviewSummaryCards
        summary={summary}
        onApplyPreset={handleApplyPreset}
        onTriggerEvaluation={handleTriggerEvaluation}
        isEvaluating={isEvaluating}
        onTriggerTriage={handleTriggerTriage}
        isTriaging={isTriaging}
        onOpenRecovery={() => setIsRecoveryOpen(true)}
        onOpenEvaluation={() => setIsEvaluationOpen(true)}
      />

      {/* Main 3-Panel Layout */}
      <div className="review-three-panel-layout">
        {/* Left: Filters */}
        <ReviewFilters
          filters={filters}
          onChangeFilter={handleChangeFilter}
          onResetFilters={handleResetFilters}
          totalMatching={totalItems}
        />

        {/* Centre: Queue Table */}
        <ReviewQueueTable
          recordings={recordings}
          selectedId={selectedId}
          onSelectRecording={setSelectedId}
          sortBy={sortBy}
          sortOrder={sortOrder}
          onSortChange={handleSortChange}
          page={page}
          pageSize={pageSize}
          totalPages={totalPages}
          totalItems={totalItems}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
          isLoading={isLoadingQueue}
        />

        {/* Right: Selected Recording Details & Review Decision */}
        <ReviewDetailPanel
          recording={selectedRecording}
          history={recordingHistory}
          onSaveDecision={handleSaveDecision}
          onPrevClip={handlePrevClip}
          onNextClip={handleNextClip}
          hasPrevClip={hasPrevClip}
          hasNextClip={hasNextClip}
          isSaving={isSavingDecision}
          autoAdvance={autoAdvance}
          onToggleAutoAdvance={handleToggleAutoAdvance}
        />
      </div>

      {/* Overwrite Confirmation Modal */}
      {pendingOverwrite && (
        <OverwriteConfirmModal
          isOpen={true}
          recordingId={pendingOverwrite.recordingId}
          currentStatus={pendingOverwrite.currentStatus}
          newStatus={pendingOverwrite.newStatus}
          onConfirm={handleConfirmOverwrite}
          onCancel={() => setPendingOverwrite(null)}
        />
      )}

      {/* Missing Audio Recovery Panel Modal */}
      <MissingAudioRecoveryPanel
        isOpen={isRecoveryOpen}
        onClose={() => setIsRecoveryOpen(false)}
        onRecoveryComplete={async () => {
          await fetchSummary()
          await fetchRecordings()
          if (selectedId) await fetchSelectedDetail(selectedId)
        }}
      />

      {/* Stage 8.9.3 Human-Verified False-Positive Analysis Modal */}
      <FalsePositiveAnalysisModal
        isOpen={isEvaluationOpen}
        onClose={() => setIsEvaluationOpen(false)}
        onSelectRecording={(recId) => {
          setSelectedId(recId)
          setIsEvaluationOpen(false)
        }}
      />
    </div>
  )
}
