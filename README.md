# Ariva

Ariva is Sri Lanka Living Intelligence: one public-first signal desk for daily costs, places, mobility, and market context, powered by the existing Ardeno Studio price-intelligence domains:
FoodLK, Octane, PropertyLK, and AutoLens.

## Shape

- `backend/` - FastAPI API, domain adapters, central snapshot schema, affordability engine.
- `frontend/` - Vite React dashboard for the public Ariva UI.
- `.github/workflows/` - CI and snapshot refresh automation.

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8090
```

Useful local settings:

```env
DATABASE_URL=sqlite:///./life_platform.db
LIFE_USE_FIXTURES=false
LIFE_CACHE_SECONDS=180
FOOD_API_BASE=https://food-platform-backend.fly.dev/api/v1
FUEL_API_BASE=https://octane-api.fly.dev
PROPERTY_API_BASE=https://property-price-intelligence-an-ardeno-production.fly.dev
VEHICLE_API_BASE=https://vehicle-platform-backend.fly.dev/api/v1
```

Optional hybrid-account settings:

```env
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
# or FIREBASE_CREDENTIALS_PATH=C:\secure\firebase-service-account.json
LIFE_INTERNAL_TOKEN=replace-with-a-long-random-token
```

The public dashboard does not require auth. Firebase Auth only enables saved profile preferences, saved watch items, alert rules, and the in-app notification inbox.

## Frontend

```powershell
cd frontend
npm install
npm run lint
npm run test
npm run build
npm run dev
```

Default local frontend API base is `http://127.0.0.1:8090/api/v1`.
When backend and frontend are both running, `npm run test:e2e` runs the desktop/mobile Playwright smoke suite.

Set the `VITE_FIREBASE_*` values from the Firebase web app config to show the optional sign-in control. If they are absent, the UI remains public-only and hides account controls.

## Deployment

- Backend: Fly app from `backend/fly.toml`; run Alembic migrations before the Uvicorn server starts.
- Frontend: Vercel Vite build from `frontend/vercel.json`; set `VITE_API_URL` to the deployed backend `/api/v1` base.
- CI: `.github/workflows/ci.yml` runs backend tests, frontend lint, frontend tests, and frontend build.
- Snapshot refresh: `.github/workflows/snapshot-refresh.yml` can call the deployed Ariva API when `LIFE_API_BASE` is configured as a repository secret.

## Public API

- `GET /api/v1/life/overview`
- `GET /api/v1/life/domains`
- `GET /api/v1/life/search?q=rice`
- `GET /api/v1/life/affordability?district=Colombo&profile=family`
- `GET /api/v1/life/trends?domain=food`
- `GET /api/v1/life/pipeline`
- `GET /api/v1/me/life-pulse` with a Firebase ID token
- `GET/PUT /api/v1/me/profile` with a Firebase ID token
- `GET/POST/DELETE /api/v1/me/saved-items` with a Firebase ID token
- `GET/POST/PATCH/DELETE /api/v1/me/alerts` with a Firebase ID token
- `GET/PATCH /api/v1/me/notifications` with a Firebase ID token
- `POST /api/v1/internal/alerts/evaluate` with `LIFE_INTERNAL_TOKEN`

## Data Truth

Ariva is live-powered, not fake streaming. It calls the upstream domain APIs with short caching, records integration runs, and stores normalized domain snapshots for central history. If an upstream is unavailable, the API returns a degraded domain state with fixture-backed structure instead of breaking the dashboard. Personal account data never overrides source labels, confidence, or freshness notes.

## Docs

- `docs/architecture.md` - product and technical architecture.
- `docs/source-roadmap.md` - official source expansion and limitations.
- `docs/verification.md` - local and production smoke checks.
