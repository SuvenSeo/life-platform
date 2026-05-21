import type {
  AffordabilityResponse,
  AlertRule,
  AlertRuleCreate,
  AtlasResponse,
  CostCommandResponse,
  DomainListResponse,
  I18nResponse,
  InsightsResponse,
  LifeOverviewResponse,
  LifePulseResponse,
  NotificationItem,
  PipelineResponse,
  Profile,
  LocaleCode,
  RetailOffersResponse,
  SavedItem,
  SavedItemCreate,
  SearchResult,
  TransportResponse,
  TrendsResponse,
  UserProfile,
  UserProfileUpdate,
  UtilitiesResponse,
} from '../types'

const API_BASE = (import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8090/api/v1').replace(/\/$/, '')

async function request<T>(
  path: string,
  options: RequestInit & { authToken?: string | null } = {},
): Promise<T> {
  const { authToken, headers, ...init } = options
  const requestHeaders = new Headers(headers)
  if (authToken) requestHeaders.set('Authorization', `Bearer ${authToken}`)
  if (init.body && !requestHeaders.has('Content-Type')) requestHeaders.set('Content-Type', 'application/json')
  const response = await fetch(`${API_BASE}${path}`, { ...init, headers: requestHeaders })
  if (!response.ok) {
    throw new Error(`Life API ${response.status}: ${response.statusText}`)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export function getOverview(district = 'Sri Lanka', profile: Profile = 'family') {
  const params = new URLSearchParams({ district, profile })
  return request<LifeOverviewResponse>(`/life/overview?${params}`)
}

export function getCostCommand(district = 'Sri Lanka', profile: Profile = 'family', locale: LocaleCode = 'en') {
  const params = new URLSearchParams({ district, profile, locale })
  return request<CostCommandResponse>(`/life/cost-command?${params}`)
}

export function getAtlas(district = 'Sri Lanka', profile: Profile = 'family', locale: LocaleCode = 'en') {
  const params = new URLSearchParams({ district, profile, locale })
  return request<AtlasResponse>(`/life/atlas?${params}`)
}

export function getUtilities(district = 'Sri Lanka') {
  const params = new URLSearchParams({ district })
  return request<UtilitiesResponse>(`/life/utilities?${params}`)
}

export function getTransport(fromArea = 'Colombo', toArea = 'Kandy') {
  const params = new URLSearchParams({ from: fromArea, to: toArea })
  return request<TransportResponse>(`/life/transport?${params}`)
}

export function getRetailOffers(q = '', district = 'Sri Lanka') {
  const params = new URLSearchParams({ district })
  if (q.trim()) params.set('q', q.trim())
  return request<RetailOffersResponse>(`/life/retail/offers?${params}`)
}

export function getInsights(domain?: string) {
  const params = new URLSearchParams()
  if (domain) params.set('domain', domain)
  const suffix = params.toString() ? `?${params}` : ''
  return request<InsightsResponse>(`/life/insights${suffix}`)
}

export function getI18n(locale: LocaleCode) {
  const params = new URLSearchParams({ locale })
  return request<I18nResponse>(`/life/i18n?${params}`)
}

export function getDomains(forceRefresh = false) {
  const params = new URLSearchParams({ force_refresh: String(forceRefresh) })
  return request<DomainListResponse>(`/life/domains?${params}`)
}

export function searchLife(q: string) {
  const params = new URLSearchParams({ q })
  return request<SearchResult[]>(`/life/search?${params}`)
}

export function getAffordability(district: string, profile: Profile) {
  const params = new URLSearchParams({ district, profile })
  return request<AffordabilityResponse>(`/life/affordability?${params}`)
}

export function getTrends(domain?: string, days = 90) {
  const params = new URLSearchParams({ days: String(days) })
  if (domain) params.set('domain', domain)
  return request<TrendsResponse>(`/life/trends?${params}`)
}

export function getPipeline() {
  return request<PipelineResponse>('/life/pipeline')
}

export function getLifePulse(authToken: string) {
  return request<LifePulseResponse>('/me/life-pulse', { authToken })
}

export function getMeProfile(authToken: string) {
  return request<UserProfile>('/me/profile', { authToken })
}

export function updateMeProfile(authToken: string, payload: UserProfileUpdate) {
  return request<UserProfile>('/me/profile', { authToken, body: JSON.stringify(payload), method: 'PUT' })
}

export function createSavedItem(authToken: string, payload: SavedItemCreate) {
  return request<SavedItem>('/me/saved-items', { authToken, body: JSON.stringify(payload), method: 'POST' })
}

export function deleteSavedItem(authToken: string, id: number) {
  return request<void>(`/me/saved-items/${id}`, { authToken, method: 'DELETE' })
}

export function createAlertRule(authToken: string, payload: AlertRuleCreate) {
  return request<AlertRule>('/me/alerts', { authToken, body: JSON.stringify(payload), method: 'POST' })
}

export function markNotification(authToken: string, id: number, read = true) {
  return request<NotificationItem>(`/me/notifications/${id}`, { authToken, body: JSON.stringify({ read }), method: 'PATCH' })
}
