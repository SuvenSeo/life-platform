# Architecture

Ariva is a public-first Sri Lanka living-intelligence product. It does not copy scraper code from the existing domain platforms in v1. FoodLK, Octane, PropertyLK, and AutoLens remain the source-of-truth systems, while Ariva adapts their public APIs into one national signal desk and central warehouse.

Hybrid accounts are optional. The public atlas, search, source registry, and affordability views continue to work without login. Firebase Auth only unlocks saved profile preferences, watchlists, alert rules, and in-app notifications.

## Runtime Shape

- Frontend: Vite React app deployed on Vercel.
- Backend: FastAPI app deployed on Fly.
- Database: Postgres in production, SQLite-compatible local development.
- ORM and migrations: SQLAlchemy and Alembic.
- CI: backend pytest plus frontend lint, tests, and build.

## Backend Flow

1. A public Ariva API request enters `/api/v1/life/*`.
2. `LifeService` asks each domain adapter for a normalized `DomainSignal`.
3. Each adapter calls its upstream API with a timeout and returns a degraded fallback signal if the upstream is unavailable.
4. The service records an `integration_runs` row for each adapter call.
5. Normalized summaries are stored in `domain_snapshots`.
6. Affordability calculations are stored in `life_index_snapshots`.
7. Authenticated `/me/*` requests verify Firebase ID tokens, upsert `user_profiles`, and combine the public overview with user-owned saved items, alert rules, and notifications.

## Central Tables

- `domains`: registry of source domains, API bases, platform URLs, and enabled flags.
- `domain_snapshots`: normalized time-series summaries, metrics, highlights, and source timestamps.
- `life_index_snapshots`: household-profile affordability outputs by district.
- `integration_runs`: per-domain adapter execution status, errors, and payload summaries.
- `source_registry`, `tariff_snapshots`, `retail_offer_snapshots`, `transport_fare_snapshots`, `area_score_snapshots`, `public_insight_snapshots`: public source, tariff, transport, area-score, and insight history.
- `user_profiles`: Firebase subject, display metadata, saved locale, district, and household profile.
- `saved_items`: user-owned saved public-domain searches, source watches, or item references.
- `alert_rules`: user-owned source/metric alert conditions.
- `notifications`: in-app alert results with read state and user-level idempotency.

## Public API

- `GET /api/v1/life/overview`
- `GET /api/v1/life/domains`
- `GET /api/v1/life/search?q=...`
- `GET /api/v1/life/affordability?district=...&profile=...`
- `GET /api/v1/life/trends?domain=...`
- `GET /api/v1/life/pipeline`
- `GET/PUT /api/v1/me/profile`
- `GET/POST/DELETE /api/v1/me/saved-items`
- `GET/POST/PATCH/DELETE /api/v1/me/alerts`
- `GET/PATCH /api/v1/me/notifications`
- `GET /api/v1/me/life-pulse`
- `POST /api/v1/internal/alerts/evaluate`

## Product Rules

- Sri Lanka, LKR, district-aware data, and source transparency are defaults.
- Live-powered means short-cache live API calls plus visible freshness, not fake streaming.
- Food uses scheduled-refresh language.
- Fuel can be checked more frequently, but still carries a timestamp and source state.
- v1 stores normalized summaries and time-series snapshots first, not every raw listing or raw market quote.
- Auth is additive: missing Firebase frontend config hides sign-in controls, and missing backend Firebase config only affects authenticated endpoints.
- Personal alerts are in-app for v1; email, WhatsApp, and push are later notification channels.
