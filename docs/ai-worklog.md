# AI Worklog

This file preserves implementation context for future ChatGPT/Codex-style sessions.

## Active branch

`ai-improvement-pass`

## Active PR

PR #1: `Harden Ariva API operations, resilience, and developer workflow`

## Environment reality

The GitHub connector can read/write repository files and update PR metadata. The local execution environment used by ChatGPT may not always be able to clone GitHub or install dependencies, so do not claim local tests passed unless they were actually run. CI is the source of truth when local execution is unavailable.

## Work completed in this pass

### Backend

- Added `RequestContextMiddleware` for `X-Request-ID`, `X-Process-Time-Ms`, `X-Content-Type-Options`, and `Referrer-Policy`.
- Added `InMemoryRateLimitMiddleware` with configurable `RATE_LIMIT_ENABLED`, `RATE_LIMIT_REQUESTS`, and `RATE_LIMIT_WINDOW_SECONDS`.
- Ensured rate-limited 429 responses include retry metadata, request IDs, and security headers.
- Refactored `LifeService.get_domain_signals()` to fetch adapters concurrently with `asyncio.gather()`.
- Kept integration-run DB writes serial through `_start_integration_runs()` and `_finish_integration_runs()`.
- Added saved-item href validation to only allow internal Ariva paths.
- Added backend container `HEALTHCHECK` using `/health`.
- Added backend `.dockerignore`.

### Frontend

- Added API request timeout behavior using `VITE_API_TIMEOUT_MS`, defaulting to 15000 ms.
- Added backend JSON error-detail extraction so errors like rate limits become visible to the UI.
- Added API client tests for timeout, auth bearer token, and error detail.

### CI / maintenance

- Hardened CI permissions and added concurrency cancellation, job timeouts, and pip caching.
- Added Dependabot for GitHub Actions, backend pip, and frontend npm.
- Added `.editorconfig`.

### Docs / developer workflow

- Added `SECURITY.md`.
- Added `docs/production-readiness.md`.
- Added `docs/developer-workflow.md`.
- Added `scripts/dev-check.ps1` and `scripts/dev-check.sh`.
- Added `.devcontainer/devcontainer.json`.
- Added `AGENTS.md`.

## Tests added

- `backend/tests/test_operational_middleware.py`
- `backend/tests/test_rate_limit_middleware.py`
- `backend/tests/test_life_service_concurrency.py`
- `backend/tests/test_schema_validation.py`
- `frontend/src/lib/api.test.ts`

## Validation status

CI has been queued/pending/in progress across several pushed heads. Check the latest PR head before making readiness claims.

Use:

- GitHub PR checks in the web UI, or
- GitHub connector workflow-run lookup for the latest PR head SHA.

## Next recommended work

1. Inspect latest CI result and fix failures first.
2. Reduce snapshot/database writes from public GET endpoints.
3. Review Alembic env/model import coverage.
4. Add structured logging tied to `X-Request-ID`.
5. Improve frontend page-level error and retry UX.
6. Add deployment smoke workflow once production URLs are known.

## Do not forget

- Keep PR #1 as draft until CI is green.
- Do not merge without explicit user instruction.
- Do not claim background work or hidden long-running execution.
- Always update this worklog when adding meaningful project-level changes.
