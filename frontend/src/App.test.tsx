import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'
import { translations } from './i18n'
import type { AreaScoreResponse, DomainKey, DomainSignal, LifeOverviewResponse, LifePulseResponse, PipelineResponse, SourceReference } from './types'

const source: SourceReference = {
  key: 'dcs-ccpi',
  label: 'DCS CCPI',
  source_type: 'official',
  url: 'https://statistics.gov.lk',
  confidence: 'high',
  freshness_note: 'Official monthly release.',
  last_checked_at: '2026-05-21T06:00:00Z',
  labels: {},
}

function domain(key: DomainKey, label: string, value: number): DomainSignal {
  return {
    key,
    label,
    category: label,
    status: key === 'retail' ? 'degraded' : 'healthy',
    health_score: key === 'retail' ? 64 : 86,
    summary: `${label} public signal.`,
    api_base: 'https://example.com',
    source_url: 'https://example.com/source',
    homepage_url: 'https://example.com',
    last_updated_at: '2026-05-21T06:00:00Z',
    observed_at: '2026-05-21T06:10:00Z',
    freshness_note: 'Visible source freshness.',
    metrics: [{ label: 'Sample metric', value, unit: 'LKR', change: null, trend: 'flat', description: null }],
    highlights: [{ label: `${label} highlight`, value: String(value), severity: 'neutral', href: null }],
    top_items: [{ label, price: value }],
    sources: [source],
    errors: [],
  }
}

const domains: DomainSignal[] = [
  domain('food', 'FoodLK', 8650),
  domain('fuel', 'Octane', 410),
  domain('property', 'PropertyLK', 14500000),
  domain('vehicle', 'AutoLens', 7600000),
  domain('utilities', 'Utilities', 18500),
  domain('gas', 'LPG Gas', 3790),
  domain('transport', 'Public Transport', 650),
  domain('retail', 'Retail Offers', 320),
  domain('indices', 'Official Indices', 5.4),
  domain('areas', 'Area Life Scores', 68),
]

const overview: LifeOverviewResponse = {
  generated_at: '2026-05-21T06:10:00Z',
  headline: 'Ariva reads Sri Lanka living signals across food, fuel, property, vehicles, and daily costs.',
  freshness_note: 'Live-powered summaries with short caching.',
  domains,
  affordability: {
    district: 'Sri Lanka',
    profile: 'family',
    total_monthly_lkr: 192000,
    confidence: 'medium',
    generated_at: '2026-05-21T06:10:00Z',
    breakdown: [{ key: 'food', label: 'Food and groceries', monthly_lkr: 37455, confidence: 'medium', source_domains: ['food'], note: 'FoodLK basket.' }],
    assumptions: ['Planning index.'],
  },
  top_movers: [
    { label: 'Petrol 92', value: 'LKR 410', severity: 'neutral', href: null },
    { label: 'Retail quote', value: 'watch', severity: 'watch', href: null },
  ],
  source_health: { healthy: 9, degraded: 1, offline: 0, total: 10, average_score: 82.2 },
}

const costCommand = {
  generated_at: '2026-05-21T06:10:00Z',
  locale: 'en',
  district: 'Sri Lanka',
  profile: 'family',
  total_monthly_lkr: 248000,
  daily_lkr: 8158,
  items: [
    { key: 'food', label: 'Food and groceries', monthly_lkr: 37455, weekly_lkr: 8650, confidence: 'medium', source_type: 'platform', source_keys: ['food'], note: 'FoodLK basket.' },
    { key: 'gas', label: 'LPG gas', monthly_lkr: 4359, weekly_lkr: 1007, confidence: 'medium', source_type: 'official', source_keys: ['litro-lpg'], note: 'LPG planning reserve.' },
  ],
  savings_moves: [{ label: 'Swap retail vs market', value: 'Compare public quotes.', severity: 'good', href: null }],
  sources: [source],
  assumptions: ['Public only.'],
}

const areaScore: AreaScoreResponse = {
  generated_at: '2026-05-21T06:10:00Z',
  district: 'Sri Lanka',
  profile: 'family',
  score: 68,
  grade: 'C',
  confidence: 'medium',
  components: [
    { key: 'rent', label: 'Rent pressure', score: 58, value: '58/100', weight: 0.3, confidence: 'low' },
    { key: 'food', label: 'Food basket pressure', score: 66, value: '66/100', weight: 0.24, confidence: 'medium' },
  ],
  sources: [source],
}

const atlas = {
  generated_at: '2026-05-21T06:10:00Z',
  locale: 'en',
  district: 'Sri Lanka',
  profile: 'family',
  national_score: 68,
  selected: areaScore,
  district_scores: [areaScore, { ...areaScore, district: 'Colombo', score: 62, grade: 'C' }],
  heatmap: [],
  narrative: 'Sri Lanka scores 68/100 for the family profile.',
  sources: [source],
}

const pipeline: PipelineResponse = {
  generated_at: '2026-05-21T06:10:00Z',
  overall_status: 'degraded',
  domains: domains.map((item) => ({
    domain: item.key,
    label: item.label,
    status: item.status,
    health_score: item.health_score,
    last_updated_at: item.last_updated_at,
    freshness_note: item.freshness_note,
    errors: item.errors,
  })),
  recent_runs: [],
}

const lifePulse: LifePulseResponse = {
  generated_at: overview.generated_at,
  profile: {
    id: 1,
    auth_sub: 'test-user',
    email: 'test@ariva.local',
    display_name: 'Ariva Test User',
    photo_url: null,
    default_locale: 'en',
    district: 'Colombo',
    profile: 'commuter',
    created_at: overview.generated_at,
    updated_at: overview.generated_at,
  },
  overview,
  saved_items: [
    {
      id: 7,
      domain_key: 'food',
      label: 'Rice watch',
      query: 'rice',
      href: '/intelligence',
      payload: {},
      created_at: overview.generated_at,
    },
  ],
  alert_rules: [
    {
      id: 9,
      condition: 'source_degraded',
      created_at: overview.generated_at,
      domain_key: 'fuel',
      enabled: true,
      label: 'Fuel source watch',
      last_triggered_at: null,
      metric_label: null,
      threshold_value: null,
      updated_at: overview.generated_at,
    },
  ],
  notifications: [
    {
      id: 11,
      alert_rule_id: 9,
      created_at: overview.generated_at,
      message: 'Fuel source moved.',
      payload: {},
      read_at: null,
      severity: 'watch',
      source_domain: 'fuel',
      title: 'Fuel watch',
    },
  ],
  unread_count: 1,
}

function jsonResponse(payload: unknown) {
  return Promise.resolve(new Response(JSON.stringify(payload), { headers: { 'Content-Type': 'application/json' } }))
}

describe('Ariva', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)
        if (url.includes('/life/overview')) return jsonResponse(overview)
        if (url.includes('/life/domains')) return jsonResponse({ items: domains })
        if (url.includes('/life/search')) return jsonResponse([{ domain: 'fuel', label: 'Octane: Petrol 92', description: '410 LKR/litre', href: '/domains/fuel', score: 80 }])
        if (url.includes('/life/cost-command')) return jsonResponse(costCommand)
        if (url.includes('/life/atlas')) return jsonResponse(atlas)
        if (url.includes('/life/utilities')) return jsonResponse({ generated_at: overview.generated_at, district: 'Sri Lanka', electricity: [], water: [], gas: [], sources: [source] })
        if (url.includes('/life/transport')) return jsonResponse({ generated_at: overview.generated_at, from_area: 'Colombo', to_area: 'Kandy', options: [], sources: [source] })
        if (url.includes('/life/retail/offers')) return jsonResponse({ generated_at: overview.generated_at, query: null, district: 'Sri Lanka', offers: [], sources: [source] })
        if (url.includes('/life/insights')) return jsonResponse({ generated_at: overview.generated_at, domain: null, insights: [], sources: [source] })
        if (url.includes('/life/pipeline')) return jsonResponse(pipeline)
        if (url.includes('/me/life-pulse')) return jsonResponse(lifePulse)
        if (url.includes('/me/profile')) return jsonResponse(lifePulse.profile)
        if (url.includes('/me/saved-items')) return jsonResponse(lifePulse.saved_items[0])
        if (url.includes('/me/alerts')) return jsonResponse(lifePulse.alert_rules[0])
        if (url.includes('/me/notifications')) return jsonResponse({ ...lifePulse.notifications[0], read_at: overview.generated_at })
        return jsonResponse({})
      }),
    )
  })

  afterEach(() => {
    delete (globalThis as { __ARIVA_TEST_AUTH_TOKEN__?: string }).__ARIVA_TEST_AUTH_TOKEN__
    delete (globalThis as { __LIFELK_TEST_AUTH_TOKEN__?: string }).__LIFELK_TEST_AUTH_TOKEN__
    vi.unstubAllEnvs()
    vi.unstubAllGlobals()
  })

  it('renders the Ariva home and trilingual controls', async () => {
    render(<App />)
    expect(await screen.findByRole('heading', { name: 'Know how Sri Lanka lives, costs, and moves.' })).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /Cost Desk/i }).length).toBeGreaterThan(0)

    fireEvent.change(screen.getByRole('combobox', { name: 'Language' }), { target: { value: 'si' } })
    expect(await screen.findByRole('heading', { name: 'ශ්‍රී ලංකාව ජීවත්වන, වියදම් කරන, ගමන් කරන ආකාරය දැනගන්න.' })).toBeInTheDocument()
  })

  it('searches the central Ariva API and opens the signals result surface', async () => {
    render(<App />)
    const search = await screen.findByPlaceholderText(/Search food/i)
    fireEvent.change(search, { target: { value: 'petrol' } })
    expect(await screen.findByText('Octane: Petrol 92')).toBeInTheDocument()
  })

  it('ships complete translation keys for all public locales', () => {
    const englishKeys = Object.keys(translations.en).sort()
    expect(Object.keys(translations.si).sort()).toEqual(englishKeys)
    expect(Object.keys(translations.ta).sort()).toEqual(englishKeys)
  })

  it('renders logged-in My Ariva Pulse and account actions with test auth', async () => {
    ;(globalThis as { __ARIVA_TEST_AUTH_TOKEN__?: string }).__ARIVA_TEST_AUTH_TOKEN__ = 'life-test-token'
    render(<App />)

    expect(await screen.findByRole('heading', { name: 'My Ariva Pulse' })).toBeInTheDocument()
    expect(screen.getByText('Rice watch')).toBeInTheDocument()
    expect(screen.getByText('Fuel watch')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /Save filters/i }))
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/me/profile'), expect.objectContaining({ method: 'PUT' }))
    })

    fireEvent.click(screen.getByRole('button', { name: /Signals/i }))
    const saveButtons = await screen.findAllByRole('button', { name: /Save/i })
    fireEvent.click(saveButtons[0])
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/me/saved-items'), expect.objectContaining({ method: 'POST' }))
    })
  })
})
