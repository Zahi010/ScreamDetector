import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ReviewStudio } from '../components/ReviewStudio/ReviewStudio'
import { ReviewSummaryCards } from '../components/ReviewStudio/ReviewSummaryCards'
import { ReviewFilters } from '../components/ReviewStudio/ReviewFilters'
import { ReviewQueueTable } from '../components/ReviewStudio/ReviewQueueTable'
import { ReviewDetailPanel } from '../components/ReviewStudio/ReviewDetailPanel'
import { AudioPlayer } from '../components/ReviewStudio/AudioPlayer'
import { OverwriteConfirmModal } from '../components/ReviewStudio/OverwriteConfirmModal'
import { MissingAudioRecoveryPanel } from '../components/ReviewStudio/MissingAudioRecoveryPanel'


// Mock fetch globally
const mockSummaryData = {
  total_candidates: 370,
  audio_available: 185,
  reviewed_count: 10,
  reviewed_percentage: 2.7,
  pending_review: 360,
  approved_non_scream: 6,
  scream_present: 2,
  ambiguous: 1,
  excluded: 1,
  missing_audio: 185,
  missing_model_scores: 194,
  model_alerts_awaiting_review: 15,
  category_counts: { whistles_and_squeaks: 52 },
  license_counts: { CC0_VERIFIED: 331 },
  source_counts: { fsd50k: 320 },
  operating_threshold: 0.35,
}

const mockRecordingsList = {
  items: [
    {
      recording_id: 'rec_test_01',
      source_provider: 'fsd50k',
      original_source_id: '1234',
      original_source_url: 'https://freesound.org/s/1234/',
      has_audio: true,
      original_filename: 'whistle.wav',
      original_title_description: 'Referee slide whistle',
      clip_license: 'CC0',
      commercial_compatibility: 'CC0_VERIFIED',
      duration_seconds: 2.5,
      sample_rate: 16000,
      channels: 1,
      proposed_category: 'whistles_and_squeaks',
      review_status: 'UNREVIEWED',
      model_score: null, // explicit missing score
      model_alert: null,
      reviewer_notes: null,
    },
    {
      recording_id: 'rec_test_02',
      source_provider: 'fsd50k',
      original_source_id: '5678',
      original_source_url: 'https://freesound.org/s/5678/',
      has_audio: false,
      original_filename: 'crowd.wav',
      original_title_description: 'Cheering stadium crowd',
      clip_license: 'CC BY 3.0',
      commercial_compatibility: 'CC_BY_VERIFIED',
      duration_seconds: 4.0,
      sample_rate: 16000,
      channels: 1,
      proposed_category: 'crowd_cheering_applause',
      review_status: 'APPROVED_NON_SCREAM',
      model_score: 0.8842, // high score alert
      model_alert: true,
      reviewer_notes: 'Reviewed and safe',
    },
  ],
  total: 2,
  page: 1,
  page_size: 25,
  total_pages: 1,
}

describe('ReviewSummaryCards Component', () => {
  it('renders all 10 live summary counters and threshold', () => {
    const onApplyPreset = vi.fn()
    const onTriggerEval = vi.fn()

    render(
      <ReviewSummaryCards
        summary={mockSummaryData}
        onApplyPreset={onApplyPreset}
        onTriggerEvaluation={onTriggerEval}
        isEvaluating={false}
      />
    )

    expect(screen.getByText('Total Discovered')).toBeInTheDocument()
    expect(screen.getByText('370')).toBeInTheDocument()
    expect(screen.getByText('Audio Available')).toBeInTheDocument()
    expect(screen.getAllByText('185')).toHaveLength(2) // in Audio Available and Missing Audio
    expect(screen.getByText('Pending Review')).toBeInTheDocument()
    expect(screen.getByText('360')).toBeInTheDocument()
    expect(screen.getByText('Approved Non-Screams')).toBeInTheDocument()
    expect(screen.getByText('6')).toBeInTheDocument()
    expect(screen.getByText('Missing Scores')).toBeInTheDocument()
    expect(screen.getByText('194')).toBeInTheDocument()
  })

  it('triggers quick filter preset when clicking preset button', () => {
    const onApplyPreset = vi.fn()

    render(
      <ReviewSummaryCards
        summary={mockSummaryData}
        onApplyPreset={onApplyPreset}
        onTriggerEvaluation={() => {}}
        isEvaluating={false}
      />
    )

    const highRiskBtn = screen.getByText(/High-Score Unreviewed/i)
    fireEvent.click(highRiskBtn)
    expect(onApplyPreset).toHaveBeenCalledWith({
      score_filter: 'high_risk',
      status: 'UNREVIEWED',
      audio: 'available',
    })
  })
})

describe('ReviewQueueTable Component', () => {
  it('renders queue items with formatted categories and explicit Not evaluated badge', () => {
    const onSelect = vi.fn()
    const onSort = vi.fn()

    render(
      <ReviewQueueTable
        recordings={mockRecordingsList.items}
        selectedId="rec_test_01"
        onSelectRecording={onSelect}
        sortBy="priority"
        sortOrder="asc"
        onSortChange={onSort}
        page={1}
        pageSize={25}
        totalPages={1}
        totalItems={2}
        onPageChange={() => {}}
        onPageSizeChange={() => {}}
        isLoading={false}
      />
    )

    expect(screen.getByText('rec_test_01')).toBeInTheDocument()
    expect(screen.getByText('rec_test_02')).toBeInTheDocument()

    // rec_test_01 has no score -> "Not evaluated"
    expect(screen.getByText('Not evaluated')).toBeInTheDocument()

    // rec_test_02 has score 0.8842 -> "88.4%" + "ALERT"
    expect(screen.getByText(/88.4%/i)).toBeInTheDocument()
    expect(screen.getByText('ALERT')).toBeInTheDocument()
  })

  it('triggers sort change when column header is clicked', () => {
    const onSort = vi.fn()

    render(
      <ReviewQueueTable
        recordings={mockRecordingsList.items}
        selectedId="rec_test_01"
        onSelectRecording={() => {}}
        sortBy="priority"
        sortOrder="asc"
        onSortChange={onSort}
        page={1}
        pageSize={25}
        totalPages={1}
        totalItems={2}
        onPageChange={() => {}}
        onPageSizeChange={() => {}}
        isLoading={false}
      />
    )

    const scoreHeader = screen.getByText(/Score \(0.35\)/i)
    fireEvent.click(scoreHeader)
    expect(onSort).toHaveBeenCalledWith('model_score', 'desc')
  })
})

describe('AudioPlayer Component', () => {
  it('renders audio player controls when audio is available', () => {
    render(
      <AudioPlayer
        recordingId="rec_test_01"
        hasAudio={true}
        onPrev={() => {}}
        onNext={() => {}}
        hasPrev={false}
        hasNext={true}
      />
    )

    expect(screen.getByTestId('review-audio-player')).toBeInTheDocument()
    expect(screen.getByLabelText(/Play recording/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Audio timeline position/i)).toBeInTheDocument()
  })

  it('renders audio missing message when audio is not available locally', () => {
    render(
      <AudioPlayer
        recordingId="rec_test_02"
        hasAudio={false}
        onPrev={() => {}}
        onNext={() => {}}
        hasPrev={true}
        hasNext={false}
      />
    )

    expect(screen.getByTestId('audio-player-missing')).toBeInTheDocument()
    expect(screen.getByText(/Audio File Unavailable Locally/i)).toBeInTheDocument()
  })
})

describe('ReviewDetailPanel & Decision Actions', () => {
  it('renders recording metadata and triggers decision when button clicked', () => {
    const onSave = vi.fn()

    render(
      <ReviewDetailPanel
        recording={mockRecordingsList.items[0]}
        history={[]}
        onSaveDecision={onSave}
        onPrevClip={() => {}}
        onNextClip={() => {}}
        hasPrevClip={false}
        hasNextClip={true}
        isSaving={false}
        autoAdvance={true}
        onToggleAutoAdvance={() => {}}
      />
    )

    expect(screen.getByText('rec_test_01')).toBeInTheDocument()
    expect(screen.getByText('Referee slide whistle')).toBeInTheDocument()

    // Click Approve Non-Scream
    const approveBtn = screen.getByTitle(/Confirm genuine non-scream sound/i)
    fireEvent.click(approveBtn)

    expect(onSave).toHaveBeenCalledWith('APPROVED_NON_SCREAM', '', '')
  })

  it('renders unsaved notes indicator when notes are modified', () => {
    render(
      <ReviewDetailPanel
        recording={mockRecordingsList.items[0]}
        history={[]}
        onSaveDecision={() => {}}
        onPrevClip={() => {}}
        onNextClip={() => {}}
        hasPrevClip={false}
        hasNextClip={true}
        isSaving={false}
        autoAdvance={true}
        onToggleAutoAdvance={() => {}}
      />
    )

    const textarea = screen.getByPlaceholderText(/Document acoustic characteristics/i)
    fireEvent.change(textarea, { target: { value: 'Auditory check confirmed zero scream harmonics.' } })

    expect(screen.getByText(/● Unsaved edits/i)).toBeInTheDocument()
  })
})

describe('OverwriteConfirmModal Component', () => {
  it('renders comparison between previous and new status and calls confirm/cancel', () => {
    const onConfirm = vi.fn()
    const onCancel = vi.fn()

    render(
      <OverwriteConfirmModal
        isOpen={true}
        recordingId="rec_test_02"
        currentStatus="APPROVED_NON_SCREAM"
        newStatus="SCREAM_PRESENT"
        onConfirm={onConfirm}
        onCancel={onCancel}
      />
    )

    expect(screen.getByText(/Confirm Review Decision Overwrite/i)).toBeInTheDocument()
    expect(screen.getByText('Approved Non-Scream')).toBeInTheDocument()
    expect(screen.getByText('Scream Present')).toBeInTheDocument()

    // Test Confirm click
    const confirmBtn = screen.getByText(/Confirm Overwrite/i)
    fireEvent.click(confirmBtn)
    expect(onConfirm).toHaveBeenCalled()

    // Test Cancel click
    const cancelBtn = screen.getByText(/Cancel/i)
    fireEvent.click(cancelBtn)
    expect(onCancel).toHaveBeenCalled()
  })
})

describe('ReviewStudio Integration Component', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn((url) => {
      if (url.includes('/api/review/summary')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockSummaryData),
        })
      }
      if (url.includes('/api/review/recordings/rec_test_01/history')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ recording_id: 'rec_test_01', history: [] }),
        })
      }
      if (url.includes('/api/review/recordings/rec_test_01')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRecordingsList.items[0]),
        })
      }
      if (url.includes('/api/review/recordings')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRecordingsList),
        })
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
    }))
  })

  it('renders complete Review Studio with summary cards, table, and details', async () => {
    render(<ReviewStudio />)

    await waitFor(() => {
      expect(screen.getByTestId('review-studio')).toBeInTheDocument()
      expect(screen.getByTestId('review-summary-cards')).toBeInTheDocument()
      expect(screen.getByTestId('review-filters-panel')).toBeInTheDocument()
      expect(screen.getByTestId('review-queue-panel')).toBeInTheDocument()
      expect(screen.getByText('Referee slide whistle')).toBeInTheDocument()
    })
  })

  it('renders Stage 8.9.1 triage cards and triggers Likely Non-Screams first preset', async () => {
    render(<ReviewStudio />)

    await waitFor(() => {
      expect(screen.getByTestId('triage_likely_non_scream')).toBeInTheDocument()
      expect(screen.getByText(/Likely Non-Screams First/i)).toBeInTheDocument()
    })

    const likelyBtn = screen.getByText(/Likely Non-Screams First/i)
    fireEvent.click(likelyBtn)

    await waitFor(() => {
      expect(screen.getByTestId('review-queue-panel')).toBeInTheDocument()
    })
  })

  it('supports administrative bulk selection with strict non-approval disclaimer', () => {
    render(
      <ReviewQueueTable
        recordings={mockRecordingsList.items}
        selectedId="rec_test_01"
        onSelectRecording={() => {}}
        sortBy="priority"
        sortOrder="asc"
        onSortChange={() => {}}
        page={1}
        pageSize={25}
        totalPages={1}
        totalItems={2}
        onPageChange={() => {}}
        onPageSizeChange={() => {}}
        isLoading={false}
      />
    )

    const selectAllCheckbox = screen.getByLabelText(/Select all recordings on this page/i)
    fireEvent.click(selectAllCheckbox)

    expect(screen.getByTestId('admin-bulk-toolbar')).toBeInTheDocument()
    expect(screen.getByText(/Selected for administrative action/i)).toBeInTheDocument()
    expect(screen.getByText(/Automated bulk-approval based on model predictions is strictly prohibited/i)).toBeInTheDocument()
  })

  it('renders MissingAudioRecoveryPanel with audit stats and recovery controls', async () => {
    const mockRecoveryStatus = {
      total_candidates: 370,
      audio_available: 343,
      missing_audio: 27,
      missing_by_source: { audioset: 22, freesound: 0, fsd50k: 5 },
      existing_on_disk: 139,
      never_downloaded: 19,
      download_failed: 0,
      licence_restricted: 22,
      source_unavailable: 5,
      recovered_successfully: 343,
      preserved_human_reviews: {
        total_reviewed: 185,
        approved_non_scream: 181,
        scream_present: 2,
        ambiguous: 2,
      },
      freesound_api_key_configured: true,
    }

    global.fetch = vi.fn().mockImplementation((url) => {
      if (url.includes('/api/review/recovery/status')) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockRecoveryStatus),
        })
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      })
    })

    const onClose = vi.fn()
    render(<MissingAudioRecoveryPanel isOpen={true} onClose={onClose} onRecoveryComplete={() => {}} />)

    await waitFor(() => {
      expect(screen.getByTestId('missing-audio-recovery-modal')).toBeInTheDocument()
      expect(screen.getByText('Missing Audio Recovery Hub')).toBeInTheDocument()
      expect(screen.getByText('Existing on E: Disk')).toBeInTheDocument()
      expect(screen.getByText('Eligible Freesound API')).toBeInTheDocument()
      expect(screen.getAllByText('Licence Restricted').length).toBeGreaterThanOrEqual(1)
      expect(screen.getByText('Source Unavailable')).toBeInTheDocument()
      expect(screen.getByTestId('btn-run-recovery')).toBeInTheDocument()
    })
  })
})



