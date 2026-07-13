# Engineering Backlog

This backlog is ordered for AI-assisted long sessions. Work from the highest priority unfinished item unless the user gives a different priority.

## P0 - correctness and merge readiness

- [ ] Inspect latest CI result for PR #1 and fix all failures.
- [ ] Verify backend tests, frontend lint/test/build, and Playwright smoke pass.
- [ ] Review the full PR diff for accidental large rewrites or formatting churn.
- [ ] Keep PR #1 in draft until checks are green.

## P1 - backend production correctness

- [ ] Reduce writes from public GET endpoints. Snapshot/history writes should move toward explicit refresh jobs or internal refresh endpoints.
- [ ] Review Alembic metadata/model imports so all persisted models are covered intentionally.
- [ ] Add structured logging with request ID, route, status code, process time, and upstream adapter status.
- [ ] Add upstream adapter contract fixtures for FoodLK, Octane, PropertyLK, and AutoLens.
- [ ] Add database pruning/retention strategy for snapshot tables.
- [ ] Add stricter validation for alert labels, metric labels, and payload sizes.

## P1 - frontend product quality

- [ ] Add page-level error states with retry buttons for Overview, Cost, Atlas, Intelligence, and Sources.
- [ ] Show rate-limit errors clearly without crashing the page.
- [ ] Add stale/degraded data badges consistently across cards.
- [ ] Add loading skeletons for high-latency API calls.
- [ ] Add tests for API failure states in main pages.

## P2 - operations and deployment

- [ ] Add a deployment smoke workflow once backend and frontend production URLs are known.
- [ ] Add PR template and issue templates.
- [ ] Add release checklist for Fly and Vercel.
- [ ] Add branch protection recommendation docs.
- [ ] Add Docker build CI job if backend containers become the primary deployment path.

## P2 - data/source credibility

- [ ] Add OpenAPI examples for core public endpoints.
- [ ] Add source confidence explanation in the frontend Sources page.
- [ ] Add source freshness timeline to Intelligence.
- [ ] Add stronger distinction between live, cached, fixture-backed, and derived values.

## P3 - scale and architecture

- [ ] Replace in-memory cache with Redis or persisted snapshot cache if running more than one API process.
- [ ] Replace in-process rate limiting with edge or Redis-backed limiting if traffic grows.
- [ ] Add background worker path for scheduled refresh and alert evaluation.
- [ ] Add observability export path for metrics/logs.

## Definition of done for AI implementation passes

A pass is complete only when:

- code changes are committed to the working branch
- relevant tests are added or updated
- docs are updated if behavior/config changed
- PR body is updated if scope changed
- validation status is stated honestly
- `docs/ai-worklog.md` is updated for meaningful changes
