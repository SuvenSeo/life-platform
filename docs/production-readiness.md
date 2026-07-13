# Production Readiness Checklist

Use this checklist before promoting Ariva backend or frontend changes to production.

## Backend API

- [ ] `APP_ENV=production` is set in the deployed environment.
- [ ] `DATABASE_URL` points to the production Postgres database, not local SQLite.
- [ ] `CORS_ORIGINS` only includes the production frontend origin and approved preview origins.
- [ ] `LIFE_INTERNAL_TOKEN` is set to a long random secret before enabling internal alert evaluation.
- [ ] `RATE_LIMIT_ENABLED=true` unless an edge or Redis-backed limiter is replacing the in-process guard.
- [ ] `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` match expected traffic and demo load.
- [ ] `/health` returns `200` from the deployed backend.
- [ ] API responses include `X-Request-ID`, `X-Process-Time-Ms`, `X-Content-Type-Options`, and `Referrer-Policy`.

## Data and integrations

- [ ] FoodLK, Octane, PropertyLK, and AutoLens upstream base URLs are current.
- [ ] `/api/v1/life/pipeline` shows no unexpected offline sources.
- [ ] Degraded sources show explicit freshness and fallback messaging.
- [ ] Snapshot refresh has `LIFE_API_BASE` configured if deployed refresh automation is needed.
- [ ] Alert evaluation only runs with `Authorization: Bearer <LIFE_INTERNAL_TOKEN>`.

## Frontend

- [ ] `VITE_API_URL` points to the deployed backend `/api/v1` base.
- [ ] `VITE_API_TIMEOUT_MS` is set deliberately; default is 15000 ms.
- [ ] Optional `VITE_FIREBASE_*` values are only enabled when Firebase auth is ready.
- [ ] The public UI still works with Firebase config absent.
- [ ] Search, Cost Desk, Atlas, Intelligence, and Sources pages load against production data.

## Security and abuse resistance

- [ ] No `.env`, `.vercel`, local DB, or credential files are committed.
- [ ] Saved item hrefs only store internal Ariva paths.
- [ ] Rate-limited responses return 429 with `Retry-After` and `X-RateLimit-*` headers.
- [ ] Authenticated `/me/*` endpoints reject missing or invalid bearer tokens.
- [ ] Internal `/internal/*` endpoints reject missing or invalid internal tokens.

## CI and release

- [ ] GitHub Actions backend, frontend, and Playwright smoke jobs are green.
- [ ] Dependabot is enabled for GitHub Actions, backend pip, and frontend npm dependencies.
- [ ] The backend container healthcheck passes after deployment.
- [ ] Rollback path is known for both Fly backend and Vercel frontend.
