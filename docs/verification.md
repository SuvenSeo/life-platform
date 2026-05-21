# Verification

## Backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8090
```

Smoke checks:

```powershell
Invoke-WebRequest http://127.0.0.1:8090/api/v1/life/overview
Invoke-WebRequest http://127.0.0.1:8090/api/v1/life/pipeline
Invoke-WebRequest "http://127.0.0.1:8090/api/v1/life/search?q=petrol"
```

Authenticated local smoke with test auth:

```powershell
$headers = @{ Authorization = "Bearer life-test-token" }
$env:APP_ENV="test"
$env:LIFE_TEST_AUTH_TOKEN="life-test-token"
$env:LIFE_INTERNAL_TOKEN="internal-test-token"
Invoke-WebRequest http://127.0.0.1:8090/api/v1/me/profile -Headers $headers
Invoke-WebRequest http://127.0.0.1:8090/api/v1/me/life-pulse -Headers $headers
Invoke-WebRequest http://127.0.0.1:8090/api/v1/internal/alerts/evaluate -Method POST -Headers @{ Authorization = "Bearer internal-test-token" }
```

## Frontend

```powershell
cd frontend
npm install
npm run lint
npm run test
npm run build
npm run dev
```

Smoke checks:

- Dashboard renders Ariva and Sri Lanka Living Intelligence.
- Four domains appear: Food, Fuel, Property, Vehicle.
- Search finds a fuel or food signal.
- Sources page shows upstream health and limitations.
- With `VITE_FIREBASE_*` configured, sign-in appears; without it, public pages render and account controls stay hidden.
- With `VITE_LIFE_TEST_AUTH_TOKEN`, My Ariva Pulse renders saved profile, watches, alert rules, and notifications in tests.
- Compare and affordability views do not overflow on mobile widths.

Playwright smoke after backend and frontend are running:

```powershell
$env:LIFE_E2E_BASE_URL="http://127.0.0.1:3001"
npm run test:e2e
```

## Production

- `GET /api/v1/life/overview` returns all four domains.
- `GET /api/v1/life/pipeline` returns a domain status list, even if one upstream is degraded.
- `GET /api/v1/me/profile` returns 401 without a Firebase ID token.
- `POST /api/v1/internal/alerts/evaluate` is protected by `LIFE_INTERNAL_TOKEN`.
- Dashboard renders from the deployed Vercel frontend with `VITE_API_URL` pointing to the Fly backend.
