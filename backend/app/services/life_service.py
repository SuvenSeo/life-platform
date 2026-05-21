from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import httpx
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.adapters import (
    AreaScoreAdapter,
    FoodAdapter,
    FuelAdapter,
    GasAdapter,
    IndicesAdapter,
    PropertyAdapter,
    RetailAdapter,
    TransportAdapter,
    UtilitiesAdapter,
    VehicleAdapter,
)
from app.core.config import Settings
from app.db.models import (
    AreaScoreSnapshot,
    Domain,
    DomainSnapshot,
    IntegrationRun,
    LifeIndexSnapshot,
    PublicInsightSnapshot,
    RetailOfferSnapshot,
    SourceRegistry,
    TariffSnapshot,
    TransportFareSnapshot,
    utc_now,
)
from app.schemas import (
    AffordabilityBreakdownItem,
    AffordabilityResponse,
    AreaScoreComponent,
    AreaScoreResponse,
    AtlasResponse,
    CostCommandItem,
    CostCommandResponse,
    DomainHighlight,
    DomainSignal,
    I18nResponse,
    InsightsResponse,
    LifeOverviewResponse,
    PipelineDomainStatus,
    PipelineResponse,
    PublicInsight,
    RetailOffer,
    RetailOffersResponse,
    SearchResult,
    SourceReference,
    TransportOption,
    TransportResponse,
    UtilitiesResponse,
    UtilityItem,
)
from app.services.living_atlas_data import (
    AREA_BASE,
    DISTRICTS,
    DOMAIN_TRANSLATIONS,
    GAS_TARIFFS,
    I18N_LABELS,
    RETAIL_OFFERS,
    SOURCE_DEFINITIONS,
    TRANSPORT_OPTIONS,
    UTILITY_TARIFFS,
    grade_for,
    source_refs,
)


PROFILE_FACTORS = {
    "single": {"food_baskets": 2.1, "fuel_litres": 28, "housing": 0.55, "vehicle": 0.35, "utilities": 18000},
    "family": {"food_baskets": 4.33, "fuel_litres": 55, "housing": 1.0, "vehicle": 0.75, "utilities": 32000},
    "commuter": {"food_baskets": 2.6, "fuel_litres": 85, "housing": 0.7, "vehicle": 0.85, "utilities": 22000},
}


DISTRICT_RENT_BASE = {
    "Colombo": 95000,
    "Gampaha": 62000,
    "Kandy": 58000,
    "Galle": 56000,
    "Jaffna": 52000,
    "Matara": 48000,
    "Kurunegala": 46000,
    "Sri Lanka": 55000,
}


LOCALES = {"en", "si", "ta"}

COST_ITEM_LABELS = {
    "si": {
        "education": "අධ්‍යාපන සංචිතය",
        "food": "ආහාර සහ සිල්ලර",
        "fuel": "ඉන්ධන",
        "gas": "LPG ගෑස්",
        "health": "සෞඛ්‍ය සහ පුද්ගලික සත්කාර",
        "household_goods": "ගෘහ භාණ්ඩ",
        "housing": "නිවාස පීඩනය",
        "transport": "පොදු ප්‍රවාහන සංචිතය",
        "utilities": "උපයෝගිතා සහ සන්නිවේදන",
        "vehicle": "වාහන හිමිකම් සංචිතය",
    },
    "ta": {
        "education": "கல்வி இருப்பு",
        "food": "உணவு மற்றும் மளிகை",
        "fuel": "எரிபொருள்",
        "gas": "LPG எரிவாயு",
        "health": "சுகாதாரம் மற்றும் தனிப்பட்ட பராமரிப்பு",
        "household_goods": "வீட்டு பொருட்கள்",
        "housing": "வீட்டு அழுத்தம்",
        "transport": "பொது போக்குவரத்து இருப்பு",
        "utilities": "பயன்பாடுகள் மற்றும் தொடர்பாடல்",
        "vehicle": "வாகன உரிமை இருப்பு",
    },
}

AREA_COMPONENT_LABELS = {
    "si": {
        "food": "ආහාර බාස්කට් පීඩනය",
        "rent": "කුලී පීඩනය",
        "source": "මූලාශ්‍ර ආවරණය",
        "transport": "ප්‍රවාහන පීඩනය",
        "utilities": "උපයෝගිතා පීඩනය",
    },
    "ta": {
        "food": "உணவு கூடை அழுத்தம்",
        "rent": "வாடகை அழுத்தம்",
        "source": "மூலக் கவரேஜ்",
        "transport": "போக்குவரத்து அழுத்தம்",
        "utilities": "பயன்பாட்டு அழுத்தம்",
    },
}

PROFILE_LABELS = {
    "si": {"single": "තනි", "family": "පවුල", "commuter": "ගමන්කරන"},
    "ta": {"single": "ஒற்றை", "family": "குடும்பம்", "commuter": "பயணி"},
}

DOMAIN_SEARCH_HINTS = {
    "vehicle": {
        "alto",
        "aqua",
        "axio",
        "car",
        "cars",
        "civic",
        "fit",
        "hybrid",
        "honda",
        "jeep",
        "lancer",
        "mazda",
        "prado",
        "suzuki",
        "toyota",
        "van",
        "vehicle",
        "vehicles",
        "vezel",
        "wagon",
    },
    "food": {
        "beef",
        "big onion",
        "bread",
        "chicken",
        "coconut",
        "dhal",
        "egg",
        "fish",
        "food",
        "grocery",
        "milk",
        "onion",
        "rice",
        "samba",
        "sugar",
        "vegetable",
    },
    "fuel": {"diesel", "fuel", "kerosene", "octane", "petrol", "trip"},
    "property": {"apartment", "house", "land", "property", "rent", "rental", "sale"},
    "utilities": {"electricity", "pucsl", "tariff", "utility", "water"},
    "gas": {"gas", "laugfs", "litro", "lpg"},
    "transport": {"bus", "commute", "fare", "rail", "train", "transport"},
    "retail": {"offer", "offers", "retail", "supermarket"},
}


def normalize_locale(locale: str) -> str:
    return locale if locale in LOCALES else "en"


def localized_cost_label(locale: str, key: str, fallback: str) -> str:
    return COST_ITEM_LABELS.get(locale, {}).get(key, fallback)


def localized_area_label(locale: str, key: str, fallback: str) -> str:
    return AREA_COMPONENT_LABELS.get(locale, {}).get(key, fallback)


def localized_profile_label(locale: str, profile: str) -> str:
    return PROFILE_LABELS.get(locale, {}).get(profile, profile)


def atlas_narrative(locale: str, district: str, score: float, profile: str) -> str:
    profile_label = localized_profile_label(locale, profile)
    if locale == "si":
        return f"{district} {profile_label} පැතිකඩ සඳහා {score}/100ක් ලබා ගනී. කුලිය, ආහාර, ප්‍රවාහනය, උපයෝගිතා සහ මූලාශ්‍ර ආවරණය වෙන වෙනම පෙන්වයි."
    if locale == "ta":
        return f"{district} {profile_label} சுயவிவரத்திற்கு {score}/100 பெறுகிறது. வாடகை, உணவு, போக்குவரத்து, பயன்பாடுகள் மற்றும் மூலக் கவரேஜ் தனியாக காட்டப்படுகின்றன."
    return f"{district} scores {score}/100 for the {profile} profile, with rent, food, transport, utilities, and source coverage shown separately."


def query_tokens(query: str) -> set[str]:
    return {part for part in query.replace("/", " ").replace("-", " ").lower().split() if part}


def infer_search_domains(query: str) -> set[str]:
    normalized = " ".join(query.lower().split())
    tokens = query_tokens(normalized)
    matches: set[str] = set()
    for domain, hints in DOMAIN_SEARCH_HINTS.items():
        if tokens.intersection(hints) or any(" " in hint and hint in normalized for hint in hints):
            matches.add(domain)
    return matches


class LifeService:
    _cache: dict[str, tuple[datetime, list[DomainSignal]]] = {}

    def __init__(self, settings: Settings):
        self.settings = settings
        self.adapters = [
            FoodAdapter(settings),
            FuelAdapter(settings),
            PropertyAdapter(settings),
            VehicleAdapter(settings),
            UtilitiesAdapter(settings),
            GasAdapter(settings),
            TransportAdapter(settings),
            RetailAdapter(settings),
            IndicesAdapter(settings),
            AreaScoreAdapter(settings),
        ]

    async def get_domain_signals(self, db: Session, *, force_refresh: bool = False) -> list[DomainSignal]:
        cache_key = "domains"
        now = utc_now()
        cached = self._cache.get(cache_key)
        if cached and not force_refresh:
            cached_at, payload = cached
            if (now - cached_at).total_seconds() < self.settings.life_cache_seconds:
                return payload

        await self.ensure_domains(db)
        self.ensure_sources(db)
        timeout = httpx.Timeout(self.settings.upstream_timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            signals = [await self._fetch_adapter(adapter, client, db) for adapter in self.adapters]

        self._cache[cache_key] = (now, signals)
        self.store_domain_snapshots(db, signals)
        return signals

    async def _fetch_adapter(self, adapter, client: httpx.AsyncClient, db: Session) -> DomainSignal:
        run = IntegrationRun(domain_key=adapter.key, status="running")
        db.add(run)
        db.commit()
        db.refresh(run)
        try:
            signal = await adapter.fetch(client)
            run.status = "completed" if signal.status != "offline" else "failed"
            run.finished_at = utc_now()
            run.payload_summary = {
                "status": signal.status,
                "health_score": signal.health_score,
                "metrics_count": len(signal.metrics),
                "errors": signal.errors,
            }
            db.commit()
            return signal
        except Exception as exc:
            run.status = "failed"
            run.finished_at = utc_now()
            run.error_message = str(exc)
            db.commit()
            return adapter.degraded_fixture(str(exc))

    async def ensure_domains(self, db: Session) -> None:
        changed = False
        for adapter in self.adapters:
            existing = db.get(Domain, adapter.key)
            if existing is None:
                db.add(
                    Domain(
                        key=adapter.key,
                        label=adapter.label,
                        category=adapter.category,
                        api_base=adapter.api_base,
                        homepage_url=adapter.homepage_url,
                        enabled=True,
                    )
                )
                changed = True
            else:
                existing.label = adapter.label
                existing.category = adapter.category
                existing.api_base = adapter.api_base
                existing.homepage_url = adapter.homepage_url
                existing.updated_at = utc_now()
                changed = True
        if changed:
            db.commit()

    def ensure_sources(self, db: Session) -> None:
        changed = False
        now = utc_now()
        for row in SOURCE_DEFINITIONS:
            existing = db.get(SourceRegistry, row["key"])
            if existing is None:
                db.add(
                    SourceRegistry(
                        key=row["key"],
                        label=row["label"],
                        source_type=row["source_type"],
                        domain_key=row["domain_key"],
                        url=row["url"],
                        confidence=row["confidence"],
                        freshness_note=row["freshness_note"],
                        status="healthy",
                        locale_labels=row.get("labels", {}),
                        last_checked_at=now,
                    )
                )
                changed = True
            else:
                existing.label = row["label"]
                existing.source_type = row["source_type"]
                existing.domain_key = row["domain_key"]
                existing.url = row["url"]
                existing.confidence = row["confidence"]
                existing.freshness_note = row["freshness_note"]
                existing.locale_labels = row.get("labels", {})
                existing.updated_at = now
                changed = True
        if changed:
            db.commit()

    def store_domain_snapshots(self, db: Session, signals: Iterable[DomainSignal]) -> None:
        for signal in signals:
            db.add(
                DomainSnapshot(
                    domain_key=signal.key,
                    status=signal.status,
                    health_score=signal.health_score,
                    summary={"text": signal.summary, "freshness_note": signal.freshness_note, "errors": signal.errors},
                    metrics=[metric.model_dump() for metric in signal.metrics],
                    highlights=[highlight.model_dump() for highlight in signal.highlights],
                    source_updated_at=signal.last_updated_at,
                    observed_at=signal.observed_at,
                )
            )
        db.commit()

    async def overview(self, db: Session, *, district: str = "Sri Lanka", profile: str = "family") -> LifeOverviewResponse:
        domains = await self.get_domain_signals(db)
        affordability = self.affordability_from_signals(db, domains, district=district, profile=profile)
        health = self.source_health(domains)
        movers = self.top_movers(domains)
        freshness_note = "Live-powered summaries with short caching; each domain exposes its own source freshness."
        return LifeOverviewResponse(
            generated_at=utc_now(),
            headline="Ariva reads Sri Lanka living signals across food, fuel, property, vehicles, and daily costs.",
            freshness_note=freshness_note,
            domains=domains,
            affordability=affordability,
            top_movers=movers,
            source_health=health,
        )

    def affordability_from_signals(
        self,
        db: Session,
        domains: list[DomainSignal],
        *,
        district: str = "Sri Lanka",
        profile: str = "family",
    ) -> AffordabilityResponse:
        if profile not in PROFILE_FACTORS:
            profile = "family"
        factors = PROFILE_FACTORS[profile]
        domain_map = {domain.key: domain for domain in domains}

        food_basket = self._metric_value(domain_map.get("food"), "Essentials basket") or 8650
        petrol_92 = self._metric_value(domain_map.get("fuel"), "Petrol 92") or 410
        avg_property_price = self._metric_value(domain_map.get("property"), "Average price")
        avg_vehicle_price = self._metric_value(domain_map.get("vehicle"), "Average price")

        rent_base = DISTRICT_RENT_BASE.get(district, DISTRICT_RENT_BASE.get("Sri Lanka", 55000))
        if avg_property_price and avg_property_price > 1_000_000:
            # A conservative monthly rental proxy when a rental endpoint is not available.
            rent_base = max(rent_base, min(avg_property_price * 0.0022, 185000))

        vehicle_monthly = 0
        if avg_vehicle_price and avg_vehicle_price > 500_000:
            vehicle_monthly = min(max(avg_vehicle_price * 0.0045, 22000), 85000)
        else:
            vehicle_monthly = 28000

        food_monthly = food_basket * factors["food_baskets"]
        fuel_monthly = petrol_92 * factors["fuel_litres"]
        housing_monthly = rent_base * factors["housing"]
        vehicle_monthly = vehicle_monthly * factors["vehicle"]
        utilities_monthly = factors["utilities"]
        public_transport_monthly = 9000 if profile != "commuter" else 16500

        breakdown = [
            AffordabilityBreakdownItem(
                key="food",
                label="Food and groceries",
                monthly_lkr=round(food_monthly, 0),
                confidence="medium",
                source_domains=["food"],
                note="Derived from FoodLK essentials basket multiplied by household profile.",
            ),
            AffordabilityBreakdownItem(
                key="housing",
                label="Housing pressure",
                monthly_lkr=round(housing_monthly, 0),
                confidence="low",
                source_domains=["property"],
                note="Uses a rental proxy until district rental-yield signals are normalized centrally.",
            ),
            AffordabilityBreakdownItem(
                key="fuel",
                label="Fuel",
                monthly_lkr=round(fuel_monthly, 0),
                confidence="high",
                source_domains=["fuel"],
                note="Uses latest Petrol 92 rate and profile-specific litres per month.",
            ),
            AffordabilityBreakdownItem(
                key="vehicle",
                label="Vehicle ownership reserve",
                monthly_lkr=round(vehicle_monthly, 0),
                confidence="low",
                source_domains=["vehicle"],
                note="Planning reserve derived from vehicle market average, not a loan quote.",
            ),
            AffordabilityBreakdownItem(
                key="utilities",
                label="Utilities and communications",
                monthly_lkr=round(utilities_monthly, 0),
                confidence="low",
                source_domains=["official-roadmap"],
                note="Static v1 assumption until PUCSL, water, gas, and telecom feeds are added.",
            ),
            AffordabilityBreakdownItem(
                key="transport",
                label="Public transport buffer",
                monthly_lkr=round(public_transport_monthly, 0),
                confidence="low",
                source_domains=["official-roadmap"],
                note="Static v1 assumption until NTC and railway tariff snapshots are added.",
            ),
        ]
        total = round(sum(item.monthly_lkr for item in breakdown), 0)
        confidence = "medium" if all(domain.status != "offline" for domain in domains) else "low"
        response = AffordabilityResponse(
            district=district,
            profile=profile,
            total_monthly_lkr=total,
            confidence=confidence,
            generated_at=utc_now(),
            breakdown=breakdown,
            assumptions=[
                "This is a planning index, not financial advice or a formal cost-of-living statistic.",
                "Food and fuel use upstream price signals; housing and vehicle costs are conservative v1 proxies.",
                "Utilities, gas, transport, and import/tax feeds are staged after the core platform.",
            ],
        )
        db.add(
            LifeIndexSnapshot(
                profile=profile,
                district=district,
                total_lkr=total,
                confidence=confidence,
                breakdown={item.key: item.model_dump() for item in breakdown},
                assumptions=response.assumptions,
                observed_at=response.generated_at,
            )
        )
        db.commit()
        return response

    def source_health(self, domains: list[DomainSignal]) -> dict[str, int | float]:
        healthy = sum(1 for domain in domains if domain.status == "healthy")
        degraded = sum(1 for domain in domains if domain.status == "degraded")
        offline = sum(1 for domain in domains if domain.status == "offline")
        avg_score = round(sum(domain.health_score for domain in domains) / max(len(domains), 1), 1)
        return {"healthy": healthy, "degraded": degraded, "offline": offline, "total": len(domains), "average_score": avg_score}

    def top_movers(self, domains: list[DomainSignal]) -> list[DomainHighlight]:
        rows: list[DomainHighlight] = []
        for domain in domains:
            rows.extend(domain.highlights[:2])
        return rows[:8]

    async def search(self, db: Session, query: str) -> list[SearchResult]:
        domains = await self.get_domain_signals(db)
        q = query.strip().lower()
        if not q:
            return []
        hinted_domains = infer_search_domains(q)
        results: list[SearchResult] = []
        for domain in domains:
            domain_is_hinted = domain.key in hinted_domains
            haystacks = [domain.label, domain.category, domain.summary, *(h.label for h in domain.highlights)]
            if any(q in str(value).lower() for value in haystacks):
                results.append(
                    SearchResult(
                        domain=domain.key,
                        label=domain.label,
                        description=domain.summary,
                        href=f"/domains/{domain.key}",
                        score=110 if domain_is_hinted else 90,
                    )
                )
            elif domain_is_hinted:
                results.append(
                    SearchResult(
                        domain=domain.key,
                        label=domain.label,
                        description=domain.summary,
                        href=f"/domains/{domain.key}",
                        score=95,
                    )
                )
            for metric in domain.metrics:
                if q in metric.label.lower():
                    results.append(
                        SearchResult(
                            domain=domain.key,
                            label=f"{domain.label}: {metric.label}",
                            description=f"{metric.value} {metric.unit or ''}".strip(),
                            href=f"/domains/{domain.key}",
                            score=100 if domain_is_hinted else 80,
                        )
                    )
            for item in domain.top_items:
                label = str(item.get("label") or item.get("item_name") or item.get("fuel_type") or item.get("title") or "")
                if label and q in label.lower():
                    results.append(
                        SearchResult(
                            domain=domain.key,
                            label=label,
                            description=f"Found in {domain.label}",
                            href=f"/domains/{domain.key}",
                            score=90 if domain_is_hinted else 70,
                        )
                    )
        deduped: dict[tuple[str, str], SearchResult] = {}
        for result in results:
            key = (result.domain, result.label)
            if key not in deduped or result.score > deduped[key].score:
                deduped[key] = result
        return sorted(deduped.values(), key=lambda result: result.score, reverse=True)[:20]

    def trends(self, db: Session, domain: str | None = None, days: int = 90) -> dict[str, Any]:
        cutoff = utc_now() - timedelta(days=days)
        query = select(DomainSnapshot).where(DomainSnapshot.observed_at >= cutoff).order_by(DomainSnapshot.observed_at.asc())
        if domain:
            query = query.where(DomainSnapshot.domain_key == domain)
        snapshots = db.scalars(query).all()
        return {
            "domain": domain or "all",
            "days": days,
            "points": [
                {
                    "domain": snapshot.domain_key,
                    "observed_at": snapshot.observed_at.isoformat(),
                    "health_score": snapshot.health_score,
                    "status": snapshot.status,
                    "metrics": snapshot.metrics,
                }
                for snapshot in snapshots
            ],
        }

    async def pipeline(self, db: Session) -> PipelineResponse:
        domains = await self.get_domain_signals(db)
        health = self.source_health(domains)
        if health["offline"]:
            overall = "offline"
        elif health["degraded"]:
            overall = "degraded"
        else:
            overall = "healthy"
        recent_runs = db.scalars(select(IntegrationRun).order_by(desc(IntegrationRun.started_at)).limit(20)).all()
        return PipelineResponse(
            generated_at=utc_now(),
            overall_status=overall,
            domains=[
                PipelineDomainStatus(
                    domain=domain.key,
                    label=domain.label,
                    status=domain.status,
                    health_score=domain.health_score,
                    last_updated_at=domain.last_updated_at,
                    freshness_note=domain.freshness_note,
                    errors=domain.errors,
                )
                for domain in domains
            ],
            recent_runs=[
                {
                    "id": run.id,
                    "domain": run.domain_key,
                    "status": run.status,
                    "started_at": run.started_at.isoformat() if run.started_at else None,
                    "finished_at": run.finished_at.isoformat() if run.finished_at else None,
                    "error_message": run.error_message,
                }
                for run in recent_runs
            ],
        )

    async def cost_command(
        self,
        db: Session,
        *,
        district: str = "Sri Lanka",
        profile: str = "family",
        locale: str = "en",
    ) -> CostCommandResponse:
        locale = normalize_locale(locale)
        profile = profile if profile in PROFILE_FACTORS else "family"
        domains = await self.get_domain_signals(db)
        affordability = self.affordability_from_signals(db, domains, district=district, profile=profile)
        gas_monthly = GAS_TARIFFS[0]["amount_lkr"] * (1.15 if profile == "family" else 0.65)
        health_monthly = 12500 if profile == "single" else 28500 if profile == "family" else 17000
        education_monthly = 32000 if profile == "family" else 5500
        household_goods = 14500 if profile == "family" else 7800

        extra_items = [
            CostCommandItem(
                key="gas",
                label=localized_cost_label(locale, "gas", "LPG gas"),
                monthly_lkr=round(gas_monthly, 0),
                weekly_lkr=round(gas_monthly / 4.33, 0),
                confidence="medium",
                source_type="official",
                source_keys=["litro-lpg", "laugfs-lpg"],
                note="Cooking-gas planning input from public LPG price references.",
            ),
            CostCommandItem(
                key="health",
                label=localized_cost_label(locale, "health", "Health and personal care"),
                monthly_lkr=round(health_monthly, 0),
                weekly_lkr=round(health_monthly / 4.33, 0),
                confidence="low",
                source_type="derived",
                source_keys=["dcs-hies"],
                note="Derived from household expenditure structure until health-price sources are normalized.",
            ),
            CostCommandItem(
                key="education",
                label=localized_cost_label(locale, "education", "Education buffer"),
                monthly_lkr=round(education_monthly, 0),
                weekly_lkr=round(education_monthly / 4.33, 0),
                confidence="low",
                source_type="derived",
                source_keys=["dcs-hies"],
                note="Family profile includes stronger education pressure; public-only planning signal.",
            ),
            CostCommandItem(
                key="household_goods",
                label=localized_cost_label(locale, "household_goods", "Household goods"),
                monthly_lkr=round(household_goods, 0),
                weekly_lkr=round(household_goods / 4.33, 0),
                confidence="low",
                source_type="derived",
                source_keys=["dcs-hies", "retail-public-pages"],
                note="Durable and household goods reserve from HIES structure plus retail-offer queue.",
            ),
        ]
        base_items = [
            CostCommandItem(
                key=item.key,
                label=localized_cost_label(locale, item.key, item.label),
                monthly_lkr=item.monthly_lkr,
                weekly_lkr=round(item.monthly_lkr / 4.33, 0),
                confidence=item.confidence,
                source_type="platform" if item.source_domains and item.source_domains[0] in {"food", "fuel", "property", "vehicle"} else "derived",
                source_keys=item.source_domains,
                note=item.note,
            )
            for item in affordability.breakdown
        ]
        items = base_items + extra_items
        total = round(sum(item.monthly_lkr for item in items), 0)
        snapshot_source_map = {
            "food": "foodlk-platform",
            "fuel": "cpc-fuel",
            "property": "dcs-hies",
            "vehicle": "cpc-fuel",
            "official-roadmap": "dcs-hies",
            "utilities": "pucsl-electricity",
            "gas": "litro-lpg",
            "transport": "ntc-bus-fares",
        }
        for item in items:
            source_key = snapshot_source_map.get(item.source_keys[0], item.source_keys[0]) if item.source_keys else "dcs-hies"
            db.add(
                TariffSnapshot(
                    domain_key=item.key,
                    source_key=source_key,
                    district=district,
                    category=item.label,
                    amount_lkr=item.monthly_lkr,
                    unit="LKR/month",
                    confidence=item.confidence,
                    payload=item.model_dump(mode="json"),
                )
            )
        db.commit()
        return CostCommandResponse(
            generated_at=utc_now(),
            locale=locale,
            district=district,
            profile=profile,
            total_monthly_lkr=total,
            daily_lkr=round(total / 30.4, 0),
            items=items,
            savings_moves=[
                DomainHighlight(label="Swap retail vs market", value="Compare supermarket quotes with FoodLK market quotes before basket buys.", severity="good", href="/?page=intelligence"),
                DomainHighlight(label="Commute mode check", value="Compare NTC bus fares with private fuel-only trip costs.", severity="watch", href="/?page=atlas"),
                DomainHighlight(label="Gas cadence", value="Track LPG cylinder replacement as a monthly reserve, not a surprise expense.", severity="neutral", href="/?page=cost"),
            ],
            sources=self.public_sources(),
            assumptions=[
                "This is a public planning estimate, not a personal finance account.",
                "All filters are query-driven and shareable; no user profile is stored.",
                "Official, retail, platform, and derived inputs are labelled separately.",
            ],
        )

    def utilities(self, db: Session, *, district: str = "Sri Lanka") -> UtilitiesResponse:
        self.ensure_sources(db)
        now = utc_now()
        items = [
            UtilityItem(**item)
            for item in UTILITY_TARIFFS
        ]
        gas = [UtilityItem(**item) for item in GAS_TARIFFS]
        for item in items + gas:
            db.add(
                TariffSnapshot(
                    domain_key="utilities" if item.key.startswith(("electricity", "water")) else "gas",
                    source_key=item.source_key,
                    district=district,
                    category=item.label,
                    amount_lkr=item.amount_lkr,
                    unit=item.unit,
                    confidence=item.confidence,
                    payload=item.model_dump(mode="json"),
                    observed_at=now,
                )
            )
        db.commit()
        return UtilitiesResponse(
            generated_at=now,
            district=district,
            electricity=[item for item in items if item.key.startswith("electricity")],
            water=[item for item in items if item.key.startswith("water")],
            gas=gas,
            sources=self.public_sources("utilities") + self.public_sources("gas"),
        )

    def transport(self, db: Session, *, from_area: str = "Colombo", to_area: str = "Kandy") -> TransportResponse:
        self.ensure_sources(db)
        now = utc_now()
        options = [
            TransportOption(**item)
            for item in TRANSPORT_OPTIONS
            if {item["from_area"].lower(), item["to_area"].lower()} == {from_area.lower(), to_area.lower()}
        ]
        if not options:
            options = [TransportOption(**item) for item in TRANSPORT_OPTIONS[:2]]
        for option in options:
            db.add(
                TransportFareSnapshot(
                    source_key=option.source_key,
                    mode=option.mode,
                    from_area=option.from_area,
                    to_area=option.to_area,
                    fare_lkr=option.fare_lkr,
                    confidence=option.confidence,
                    payload=option.model_dump(mode="json"),
                    observed_at=now,
                )
            )
        db.commit()
        return TransportResponse(
            generated_at=now,
            from_area=from_area,
            to_area=to_area,
            options=options,
            sources=self.public_sources("transport") + self.public_sources("fuel"),
        )

    def retail_offers(self, db: Session, *, query: str | None = None, district: str = "Sri Lanka") -> RetailOffersResponse:
        self.ensure_sources(db)
        now = utc_now()
        q = (query or "").strip().lower()
        rows = [
            item
            for item in RETAIL_OFFERS
            if (not q or q in item["item_name"].lower()) and item["district"] in {district, "Sri Lanka"}
        ]
        if not rows and q:
            rows = [item for item in RETAIL_OFFERS if q in item["item_name"].lower()]
        offers = [RetailOffer(**item) for item in rows]
        for offer in offers:
            db.add(
                RetailOfferSnapshot(
                    source_key=offer.source_key,
                    item_name=offer.item_name,
                    retailer=offer.retailer,
                    district=offer.district,
                    price_lkr=offer.price_lkr,
                    unit=offer.unit,
                    confidence=offer.confidence,
                    payload=offer.model_dump(mode="json"),
                    observed_at=now,
                )
            )
        db.commit()
        return RetailOffersResponse(
            generated_at=now,
            query=query,
            district=district,
            offers=offers,
            sources=self.public_sources("retail"),
        )

    def area_score(self, db: Session, *, district: str = "Sri Lanka", profile: str = "family", locale: str = "en") -> AreaScoreResponse:
        self.ensure_sources(db)
        locale = normalize_locale(locale)
        base = AREA_BASE.get(district, AREA_BASE["Sri Lanka"])
        if profile not in PROFILE_FACTORS:
            profile = "family"
        weights = {"rent": 0.3, "food": 0.24, "transport": 0.18, "utilities": 0.14, "source": 0.14}
        if profile == "commuter":
            weights = {"rent": 0.24, "food": 0.2, "transport": 0.28, "utilities": 0.12, "source": 0.16}
        components = [
            AreaScoreComponent(key="rent", label=localized_area_label(locale, "rent", "Rent pressure"), score=base["rent"], value=f"{base['rent']}/100", weight=weights["rent"], confidence="low"),
            AreaScoreComponent(key="food", label=localized_area_label(locale, "food", "Food basket pressure"), score=base["food"], value=f"{base['food']}/100", weight=weights["food"], confidence="medium"),
            AreaScoreComponent(key="transport", label=localized_area_label(locale, "transport", "Transport pressure"), score=base["transport"], value=f"{base['transport']}/100", weight=weights["transport"], confidence="medium"),
            AreaScoreComponent(key="utilities", label=localized_area_label(locale, "utilities", "Utility pressure"), score=base["utilities"], value=f"{base['utilities']}/100", weight=weights["utilities"], confidence="low"),
            AreaScoreComponent(key="source", label=localized_area_label(locale, "source", "Source coverage"), score=base["source"], value=f"{base['source']}/100", weight=weights["source"], confidence="medium"),
        ]
        score = round(sum(component.score * component.weight for component in components), 1)
        response = AreaScoreResponse(
            generated_at=utc_now(),
            district=district,
            profile=profile,
            score=score,
            grade=grade_for(score),
            confidence="medium",
            components=components,
            sources=self.public_sources("areas") + self.public_sources("indices"),
        )
        db.add(
            AreaScoreSnapshot(
                district=district,
                profile=profile,
                score=score,
                grade=response.grade,
                confidence=response.confidence,
                components=[component.model_dump(mode="json") for component in components],
                observed_at=response.generated_at,
            )
        )
        db.commit()
        return response

    def atlas(self, db: Session, *, district: str = "Sri Lanka", profile: str = "family", locale: str = "en") -> AtlasResponse:
        locale = normalize_locale(locale)
        selected = self.area_score(db, district=district, profile=profile, locale=locale)
        district_scores = [self.area_score(db, district=item, profile=profile, locale=locale) for item in DISTRICTS]
        heatmap = [
            {
                "district": item.district,
                "score": item.score,
                "grade": item.grade,
                "rent": next(component.score for component in item.components if component.key == "rent"),
                "food": next(component.score for component in item.components if component.key == "food"),
                "transport": next(component.score for component in item.components if component.key == "transport"),
            }
            for item in district_scores
        ]
        national = next((item.score for item in district_scores if item.district == "Sri Lanka"), selected.score)
        return AtlasResponse(
            generated_at=utc_now(),
            locale=locale,
            district=district,
            profile=profile if profile in PROFILE_FACTORS else "family",
            national_score=national,
            selected=selected,
            district_scores=district_scores,
            heatmap=heatmap,
            narrative=atlas_narrative(locale, district, selected.score, profile),
            sources=self.public_sources(),
        )

    async def insights(self, db: Session, *, domain: str | None = None) -> InsightsResponse:
        domains = await self.get_domain_signals(db)
        now = utc_now()
        source_map = {source.key: source for source in self.public_sources()}
        rows = [
            PublicInsight(
                id="cost-non-food-pressure",
                domain="indices",
                title="Non-food costs are the bigger monthly load",
                message="HIES context shows the household basket is broader than food, so utilities, transport, health, education, and household goods are first-class Ariva inputs.",
                severity="watch",
                confidence="high",
                source_keys=["dcs-hies"],
                observed_at=now,
            ),
            PublicInsight(
                id="food-substitution",
                domain="food",
                title="Food basket needs substitutions, not just cheapest sorting",
                message="Retail and market quote comparison should highlight reasonable substitutes when staples move quickly.",
                severity="watch",
                confidence="medium",
                source_keys=["foodlk-platform", "cbsl-price-report", "harti-daily"],
                observed_at=now,
            ),
            PublicInsight(
                id="source-degraded-visible",
                domain="sources",
                title="Source confidence is part of the product",
                message="When retail pages block access or official formats change, the domain should degrade visibly without breaking the dashboard.",
                severity="good",
                confidence="high",
                source_keys=list(source_map)[:4],
                observed_at=now,
            ),
        ]
        for signal in domains:
            if signal.status != "healthy":
                rows.append(
                    PublicInsight(
                        id=f"{signal.key}-degraded",
                        domain=signal.key,
                        title=f"{signal.label} needs attention",
                        message=f"{signal.label} is currently {signal.status}; Ariva is still serving degraded public signals with visible freshness.",
                        severity="watch",
                        confidence="medium",
                        source_keys=[source.key for source in signal.sources] or [signal.key],
                        observed_at=now,
                    )
                )
        filtered = [row for row in rows if domain is None or row.domain == domain]
        for item in filtered:
            db.add(
                PublicInsightSnapshot(
                    insight_key=item.id,
                    domain_key=item.domain,
                    title=item.title,
                    severity=item.severity,
                    message=item.message,
                    confidence=item.confidence,
                    source_keys=item.source_keys,
                    observed_at=item.observed_at,
                )
            )
        db.commit()
        keys = {key for item in filtered for key in item.source_keys}
        return InsightsResponse(
            generated_at=now,
            domain=domain,
            insights=filtered,
            sources=[source for source in self.public_sources() if source.key in keys],
        )

    def i18n(self, *, locale: str = "en") -> I18nResponse:
        if locale not in {"en", "si", "ta"}:
            locale = "en"
        source_labels = {
            row["key"]: row.get("labels", {}).get(locale, row["label"])
            for row in SOURCE_DEFINITIONS
        }
        return I18nResponse(
            locale=locale,
            labels=I18N_LABELS[locale],
            domains=DOMAIN_TRANSLATIONS[locale],
            sources=source_labels,
        )

    def public_sources(self, domain: str | None = None) -> list[SourceReference]:
        return source_refs(domain)

    def _metric_value(self, domain: DomainSignal | None, label: str) -> float | None:
        if domain is None:
            return None
        for metric in domain.metrics:
            if metric.label == label:
                try:
                    return float(metric.value) if metric.value is not None else None
                except (TypeError, ValueError):
                    return None
        return None
