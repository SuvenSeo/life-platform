export type DomainKey = 'food' | 'fuel' | 'property' | 'vehicle' | 'utilities' | 'gas' | 'transport' | 'retail' | 'indices' | 'areas'
export type SourceStatus = 'healthy' | 'degraded' | 'offline'
export type Trend = 'up' | 'down' | 'flat' | 'unknown'
export type Confidence = 'high' | 'medium' | 'low'
export type Profile = 'single' | 'family' | 'commuter'
export type LocaleCode = 'en' | 'si' | 'ta'
export type SourceType = 'official' | 'retail' | 'platform' | 'derived'

export interface SourceReference {
  key: string
  label: string
  source_type: SourceType
  url: string
  confidence: Confidence
  freshness_note: string
  last_checked_at: string | null
  labels: Record<string, string>
}

export interface DomainMetric {
  label: string
  value: number | string | null
  unit: string | null
  change: number | null
  trend: Trend
  description: string | null
}

export interface DomainHighlight {
  label: string
  value: string
  severity: 'good' | 'watch' | 'risk' | 'neutral'
  href: string | null
}

export interface DomainSignal {
  key: DomainKey
  label: string
  category: string
  status: SourceStatus
  health_score: number
  summary: string
  api_base: string
  source_url: string
  homepage_url: string
  last_updated_at: string | null
  observed_at: string
  freshness_note: string
  metrics: DomainMetric[]
  highlights: DomainHighlight[]
  top_items: Record<string, unknown>[]
  sources: SourceReference[]
  errors: string[]
}

export interface AffordabilityBreakdownItem {
  key: string
  label: string
  monthly_lkr: number
  confidence: Confidence
  source_domains: string[]
  note: string
}

export interface AffordabilityResponse {
  district: string
  profile: Profile
  total_monthly_lkr: number
  confidence: Confidence
  generated_at: string
  breakdown: AffordabilityBreakdownItem[]
  assumptions: string[]
}

export interface LifeOverviewResponse {
  generated_at: string
  headline: string
  freshness_note: string
  domains: DomainSignal[]
  affordability: AffordabilityResponse
  top_movers: DomainHighlight[]
  source_health: {
    healthy: number
    degraded: number
    offline: number
    total: number
    average_score: number
  }
}

export interface SearchResult {
  domain: string
  label: string
  description: string
  href: string | null
  score: number
}

export interface DomainListResponse {
  items: DomainSignal[]
}

export interface TrendPoint {
  domain: DomainKey
  observed_at: string
  health_score: number
  status: SourceStatus
  metrics: DomainMetric[]
}

export interface TrendsResponse {
  domain: DomainKey | 'all'
  days: number
  points: TrendPoint[]
}

export interface PipelineDomainStatus {
  domain: DomainKey
  label: string
  status: SourceStatus
  health_score: number
  last_updated_at: string | null
  freshness_note: string
  errors: string[]
}

export interface PipelineResponse {
  generated_at: string
  overall_status: SourceStatus
  domains: PipelineDomainStatus[]
  recent_runs: Array<{
    id: number
    domain: string
    status: string
    started_at: string | null
    finished_at: string | null
    error_message: string | null
  }>
}

export interface CostCommandItem {
  key: string
  label: string
  monthly_lkr: number
  weekly_lkr: number
  confidence: Confidence
  source_type: SourceType
  source_keys: string[]
  note: string
}

export interface CostCommandResponse {
  generated_at: string
  locale: LocaleCode
  district: string
  profile: Profile
  total_monthly_lkr: number
  daily_lkr: number
  items: CostCommandItem[]
  savings_moves: DomainHighlight[]
  sources: SourceReference[]
  assumptions: string[]
}

export interface AreaScoreComponent {
  key: string
  label: string
  score: number
  value: string
  weight: number
  confidence: Confidence
}

export interface AreaScoreResponse {
  generated_at: string
  district: string
  profile: Profile
  score: number
  grade: string
  confidence: Confidence
  components: AreaScoreComponent[]
  sources: SourceReference[]
}

export interface AtlasResponse {
  generated_at: string
  locale: LocaleCode
  district: string
  profile: Profile
  national_score: number
  selected: AreaScoreResponse
  district_scores: AreaScoreResponse[]
  heatmap: Array<Record<string, number | string>>
  narrative: string
  sources: SourceReference[]
}

export interface UtilityItem {
  key: string
  label: string
  amount_lkr: number
  unit: string
  source_key: string
  confidence: Confidence
  note: string
}

export interface UtilitiesResponse {
  generated_at: string
  district: string
  electricity: UtilityItem[]
  water: UtilityItem[]
  gas: UtilityItem[]
  sources: SourceReference[]
}

export interface TransportOption {
  mode: string
  from_area: string
  to_area: string
  fare_lkr: number
  confidence: Confidence
  source_key: string
  note: string
}

export interface TransportResponse {
  generated_at: string
  from_area: string
  to_area: string
  options: TransportOption[]
  sources: SourceReference[]
}

export interface RetailOffer {
  item_name: string
  retailer: string
  district: string
  price_lkr: number
  unit: string
  source_key: string
  source_type: SourceType
  confidence: Confidence
  note: string
}

export interface RetailOffersResponse {
  generated_at: string
  query: string | null
  district: string
  offers: RetailOffer[]
  sources: SourceReference[]
}

export interface PublicInsight {
  id: string
  domain: string
  title: string
  message: string
  severity: 'good' | 'watch' | 'risk' | 'neutral'
  confidence: Confidence
  source_keys: string[]
  observed_at: string
}

export interface InsightsResponse {
  generated_at: string
  domain: string | null
  insights: PublicInsight[]
  sources: SourceReference[]
}

export interface I18nResponse {
  locale: LocaleCode
  labels: Record<string, string>
  domains: Record<string, string>
  sources: Record<string, string>
}

export type AlertCondition = 'above' | 'below' | 'source_degraded' | 'movement_changed'

export interface UserProfile {
  id: number
  auth_sub: string
  email: string | null
  display_name: string | null
  photo_url: string | null
  default_locale: LocaleCode
  district: string
  profile: Profile
  created_at: string
  updated_at: string
}

export interface UserProfileUpdate {
  default_locale?: LocaleCode
  district?: string
  profile?: Profile
  display_name?: string | null
}

export interface SavedItem {
  id: number
  domain_key: DomainKey
  label: string
  query: string | null
  href: string | null
  payload: Record<string, unknown>
  created_at: string
}

export interface SavedItemCreate {
  domain_key: DomainKey
  label: string
  query?: string | null
  href?: string | null
  payload?: Record<string, unknown>
}

export interface AlertRule {
  id: number
  domain_key: DomainKey | null
  label: string
  metric_label: string | null
  condition: AlertCondition
  threshold_value: number | null
  enabled: boolean
  created_at: string
  updated_at: string
  last_triggered_at: string | null
}

export interface AlertRuleCreate {
  domain_key?: DomainKey | null
  label: string
  metric_label?: string | null
  condition: AlertCondition
  threshold_value?: number | null
  enabled?: boolean
}

export interface NotificationItem {
  id: number
  alert_rule_id: number | null
  title: string
  message: string
  severity: 'good' | 'watch' | 'risk' | 'neutral'
  source_domain: DomainKey | null
  read_at: string | null
  payload: Record<string, unknown>
  created_at: string
}

export interface LifePulseResponse {
  generated_at: string
  profile: UserProfile
  overview: LifeOverviewResponse
  saved_items: SavedItem[]
  alert_rules: AlertRule[]
  notifications: NotificationItem[]
  unread_count: number
}

export type PageKey = 'home' | 'cost' | 'atlas' | 'intelligence' | 'sources'
