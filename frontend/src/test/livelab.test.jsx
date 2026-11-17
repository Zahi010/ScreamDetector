import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../App'
import { MultiModelLiveLab } from '../components/MultiModelLiveLab'
import { Header } from '../components/Header'

// Mock global fetch
beforeEach(() => {
  global.fetch = vi.fn().mockImplementation((url) => {
    if (url.includes('/api/experimental/live/models')) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            status: 'success',
            primary_model_id: 'D_V4_FAMILY_A',
            production_model_id: 'PRODUCTION_BASELINE',
            models: [
              {
                model_id: 'D_V4_FAMILY_A',
                display_name: 'D_v4 + Family A (Turbulence)',
                stage: 'Stage 8.9.14',
                operating_threshold: 0.420,
                expected_feature_dims: 3080,
                is_primary: true,
                is_production: false,
                is_enabled: true,
                status: 'LOADED',
              },
              {
                model_id: 'D_V4_FAMILY_B',
                display_name: 'D_v4 + Family B (Spectral Dynamics)',
                stage: 'Stage 8.9.14',
                operating_threshold: 0.650,
                expected_feature_dims: 3080,
                is_primary: false,
                is_production: false,
                is_enabled: true,
                status: 'LOADED',
              },
              {
                model_id: 'F_V6_ACOUSTIC',
                display_name: 'F_v6 Acoustic Full (30 Features)',
                stage: 'Stage 8.9.14',
                operating_threshold: 0.360,
                expected_feature_dims: 3102,
                is_primary: false,
                is_production: false,
                is_enabled: true,
                status: 'LOADED',
              },
              {
                model_id: 'STAGE_8915_MODEL_A',
                display_name: 'Stage 8.9.15 Model A (Compact MLP)',
                stage: 'Stage 8.9.15',
                operating_threshold: 0.440,
                expected_feature_dims: 3102,
                is_primary: false,
                is_production: false,
                is_enabled: true,
                status: 'LOADED',
              },
              {
                model_id: 'STAGE_8915_MODEL_B',
                display_name: 'Stage 8.9.15 Model B (Temporal Dilated CNN)',
                stage: 'Stage 8.9.15',
                operating_threshold: 0.610,
                expected_feature_dims: 1024,
                is_primary: false,
                is_production: false,
                is_enabled: true,
                status: 'LOADED',
              },
              {
                model_id: 'STAGE_8915_MODEL_C',
                display_name: 'Stage 8.9.15 Model C (Learned Fusion)',
                stage: 'Stage 8.9.15',
                operating_threshold: 0.500,
                expected_feature_dims: 9,
                is_primary: false,
                is_production: false,
                is_enabled: true,
                status: 'LOADED',
              },
              {
                model_id: 'PRODUCTION_BASELINE',
                display_name: 'Production Baseline (Stage 5 LR)',
                stage: 'Production (Stage 5)',
                operating_threshold: 0.350,
                expected_feature_dims: 1024,
                is_primary: false,
                is_production: true,
                is_enabled: true,
                status: 'LOADED',
              },
            ],
          }),
      })
    }
    if (url.includes('/api/experimental/live/status')) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            status: 'success',
            lab_status: {
              is_running: false,
              mic_status: 'stopped',
              window_counter: 0,
              dropped_windows_total: 0,
              buffer_stats: { buffered_seconds: 0, dropped_samples: 0 },
              enabled_models: {},
            },
            audio_devices: [{ index: 0, name: 'Default Audio Device', is_default: true }],
          }),
      })
    }
    if (url.includes('/api/experimental/live/events')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: 'success', events: [] }),
      })
    }
    if (url.includes('/api/review/summary')) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ pending_review: 0 }),
      })
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({}),
    })
  })
})

describe('Multi-Model Live Lab Integration', () => {
  it('renders Multi-Model Live Lab navigation tab in Header', () => {
    render(
      <Header
        connectionStatus="connected"
        detectorStatus={{ is_running: false }}
        activeTab="live"
        onSelectTab={() => {}}
      />
    )
    expect(screen.getByText('Multi-Model Live Lab')).toBeInTheDocument()
    expect(screen.getByText(/LIVE 7-MODEL/i)).toBeInTheDocument()
  })

  it('renders MultiModelLiveLab component with Primary Model D_v4 + Family A', async () => {
    render(<MultiModelLiveLab />)

    // Check panel headers
    expect(screen.getByText(/Shared Microphone Capture & Audio Testing Stream/i)).toBeInTheDocument()
    expect(screen.getByText(/PRIMARY EXPERIMENTAL CANDIDATE/i)).toBeInTheDocument()
    expect(screen.getByText(/D_v4 \+ Family A — Acoustic Discriminability Model/i)).toBeInTheDocument()

    // Check Operating Threshold
    expect(screen.getAllByText(/0.4200/i)[0]).toBeInTheDocument()

    // Check Audio Injection Buttons
    expect(screen.getByText('Distress Scream')).toBeInTheDocument()
    expect(screen.getByText('High-Pitch Shout')).toBeInTheDocument()
    expect(screen.getByText('Crowd Cheering')).toBeInTheDocument()

    // Check Comparison Section
    expect(screen.getByText(/Experimental Candidate & Baseline Comparison Suite/i)).toBeInTheDocument()
    expect(screen.getByText(/Previously Verified Offline Benchmark/i)).toBeInTheDocument()
  })

  it('switches between tabs in App when clicking Multi-Model Live Lab', async () => {
    render(<App />)

    const labTabBtn = screen.getByText('Multi-Model Live Lab')
    fireEvent.click(labTabBtn)

    await waitFor(() => {
      expect(screen.getByText(/D_v4 \+ Family A — Acoustic Discriminability Model/i)).toBeInTheDocument()
    })
  })
})
