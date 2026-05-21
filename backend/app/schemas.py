from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

DomainKey = Literal["food", "fuel", "property", "vehicle", "utilities", "gas", "transport", "retail", "indices", "areas"]
SourceStatus = Literal["healthy", "degraded", "offline"]
SourceType = Literal["official", "retail", "platform", "derived"]
Confidence = Literal["high", "medium", "low"]
LocaleCode = Literal["en", "si", "ta"]


class SourceReference(BaseModel):
    key: str
    label: str
    source_type: SourceType
    url: str
    confidence: Confidence
    freshness_note: str
    last_checked_at: datetime | None = None
    labels: dict[str, str] = Field(default_factory=dict)


class DomainMetric(BaseModel):
    label: str
    value: float | int | str | None
    unit: str | None = None
    change: float | None = None
    trend: Literal["up", "down", "flat", "unknown"] = "unknown"
    description: str | None = None


class DomainHighlight(BaseModel):
    label: str
    value: str
    severity: Literal["good", "watch", "risk", "neutral"] = "neutral"
    href: str | None = None


class DomainSignal(BaseModel):
    key: DomainKey
    label: str
    category: str
    status: SourceStatus
    health_score: float = Field(ge=0, le=100)
    summary: str
    api_base: str
    source_url: str
    homepage_url: str
    last_updated_at: datetime | None = None
    observed_at: datetime
    freshness_note: str
    metrics: list[DomainMetric] = Field(default_factory=list)
    highlights: list[DomainHighlight] = Field(default_factory=list)
    top_items: list[dict] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AffordabilityBreakdownItem(BaseModel):
    key: str
    label: str
    monthly_lkr: float
    confidence: Confidence
    source_domains: list[str]
    note: str


class AffordabilityResponse(BaseModel):
    district: str
    profile: Literal["single", "family", "commuter"]
    total_monthly_lkr: float
    confidence: Confidence
    generated_at: datetime
    breakdown: list[AffordabilityBreakdownItem]
    assumptions: list[str]


class LifeOverviewResponse(BaseModel):
    generated_at: datetime
    headline: str
    freshness_note: str
    domains: list[DomainSignal]
    affordability: AffordabilityResponse
    top_movers: list[DomainHighlight]
    source_health: dict[str, int | float]


class SearchResult(BaseModel):
    domain: str
    label: str
    description: str
    href: str | None = None
    score: int


class PipelineDomainStatus(BaseModel):
    domain: str
    label: str
    status: str
    health_score: float
    last_updated_at: datetime | None
    freshness_note: str
    errors: list[str]


class PipelineResponse(BaseModel):
    generated_at: datetime
    overall_status: SourceStatus
    domains: list[PipelineDomainStatus]
    recent_runs: list[dict]


class CostCommandItem(BaseModel):
    key: str
    label: str
    monthly_lkr: float
    weekly_lkr: float
    confidence: Confidence
    source_type: SourceType
    source_keys: list[str]
    note: str


class CostCommandResponse(BaseModel):
    generated_at: datetime
    locale: LocaleCode
    district: str
    profile: Literal["single", "family", "commuter"]
    total_monthly_lkr: float
    daily_lkr: float
    items: list[CostCommandItem]
    savings_moves: list[DomainHighlight]
    sources: list[SourceReference]
    assumptions: list[str]


class AreaScoreComponent(BaseModel):
    key: str
    label: str
    score: float = Field(ge=0, le=100)
    value: str
    weight: float
    confidence: Confidence


class AreaScoreResponse(BaseModel):
    generated_at: datetime
    district: str
    profile: Literal["single", "family", "commuter"]
    score: float = Field(ge=0, le=100)
    grade: str
    confidence: Confidence
    components: list[AreaScoreComponent]
    sources: list[SourceReference]


class AtlasResponse(BaseModel):
    generated_at: datetime
    locale: LocaleCode
    district: str
    profile: Literal["single", "family", "commuter"]
    national_score: float
    selected: AreaScoreResponse
    district_scores: list[AreaScoreResponse]
    heatmap: list[dict]
    narrative: str
    sources: list[SourceReference]


class UtilityItem(BaseModel):
    key: str
    label: str
    amount_lkr: float
    unit: str
    source_key: str
    confidence: Confidence
    note: str


class UtilitiesResponse(BaseModel):
    generated_at: datetime
    district: str
    electricity: list[UtilityItem]
    water: list[UtilityItem]
    gas: list[UtilityItem]
    sources: list[SourceReference]


class TransportOption(BaseModel):
    mode: str
    from_area: str
    to_area: str
    fare_lkr: float
    confidence: Confidence
    source_key: str
    note: str


class TransportResponse(BaseModel):
    generated_at: datetime
    from_area: str
    to_area: str
    options: list[TransportOption]
    sources: list[SourceReference]


class RetailOffer(BaseModel):
    item_name: str
    retailer: str
    district: str
    price_lkr: float
    unit: str
    source_key: str
    source_type: SourceType = "retail"
    confidence: Confidence
    note: str


class RetailOffersResponse(BaseModel):
    generated_at: datetime
    query: str | None = None
    district: str
    offers: list[RetailOffer]
    sources: list[SourceReference]


class PublicInsight(BaseModel):
    id: str
    domain: str
    title: str
    message: str
    severity: Literal["good", "watch", "risk", "neutral"]
    confidence: Confidence
    source_keys: list[str]
    observed_at: datetime


class InsightsResponse(BaseModel):
    generated_at: datetime
    domain: str | None = None
    insights: list[PublicInsight]
    sources: list[SourceReference]


class I18nResponse(BaseModel):
    locale: LocaleCode
    labels: dict[str, str]
    domains: dict[str, str]
    sources: dict[str, str]


AlertCondition = Literal["above", "below", "source_degraded", "movement_changed"]


class UserProfileUpdate(BaseModel):
    default_locale: LocaleCode | None = None
    district: str | None = Field(default=None, min_length=1, max_length=128)
    profile: Literal["single", "family", "commuter"] | None = None
    display_name: str | None = Field(default=None, max_length=160)


class UserProfileResponse(BaseModel):
    id: int
    auth_sub: str
    email: str | None = None
    display_name: str | None = None
    photo_url: str | None = None
    default_locale: LocaleCode
    district: str
    profile: Literal["single", "family", "commuter"]
    created_at: datetime
    updated_at: datetime


class SavedItemCreate(BaseModel):
    domain_key: DomainKey
    label: str = Field(min_length=1, max_length=180)
    query: str | None = Field(default=None, max_length=160)
    href: str | None = Field(default=None, max_length=512)
    payload: dict = Field(default_factory=dict)


class SavedItemResponse(BaseModel):
    id: int
    domain_key: DomainKey
    label: str
    query: str | None = None
    href: str | None = None
    payload: dict
    created_at: datetime


class AlertRuleCreate(BaseModel):
    domain_key: DomainKey | None = None
    label: str = Field(min_length=1, max_length=180)
    metric_label: str | None = Field(default=None, max_length=120)
    condition: AlertCondition
    threshold_value: float | None = None
    enabled: bool = True

    @model_validator(mode="after")
    def threshold_required_for_metric_conditions(self):
        if self.condition in {"above", "below"} and self.threshold_value is None:
            raise ValueError("threshold_value is required for above/below alerts")
        return self


class AlertRuleUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=1, max_length=180)
    metric_label: str | None = Field(default=None, max_length=120)
    condition: AlertCondition | None = None
    threshold_value: float | None = None
    enabled: bool | None = None


class AlertRuleResponse(BaseModel):
    id: int
    domain_key: DomainKey | None = None
    label: str
    metric_label: str | None = None
    condition: AlertCondition
    threshold_value: float | None = None
    enabled: bool
    created_at: datetime
    updated_at: datetime
    last_triggered_at: datetime | None = None


class NotificationUpdate(BaseModel):
    read: bool = True


class NotificationResponse(BaseModel):
    id: int
    alert_rule_id: int | None = None
    title: str
    message: str
    severity: Literal["good", "watch", "risk", "neutral"]
    source_domain: DomainKey | None = None
    read_at: datetime | None = None
    payload: dict
    created_at: datetime


class LifePulseResponse(BaseModel):
    generated_at: datetime
    profile: UserProfileResponse
    overview: LifeOverviewResponse
    saved_items: list[SavedItemResponse]
    alert_rules: list[AlertRuleResponse]
    notifications: list[NotificationResponse]
    unread_count: int


class AlertEvaluationResponse(BaseModel):
    generated_at: datetime
    users_checked: int
    alerts_checked: int
    notifications_created: int
