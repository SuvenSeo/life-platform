# AGENTS.md

This file is for AI agents and long-running coding assistants working on Ariva.

## Mission

Ariva is a Sri Lanka living-intelligence platform. Improve it as a real production-grade full-stack product, not as a toy demo. Prioritize reliability, correctness, UX clarity, source transparency, and maintainability.

## Current working branch

Use `ai-improvement-pass` for the current hardening pass until PR #1 is merged or superseded.

## Repository shape

- `backend/` - FastAPI, SQLAlchemy, Alembic, source adapters, account APIs, tests.
- `frontend/` - Vite, React, TypeScript, React Query, Playwright, Vitest.
- `docs/` - architecture, verification, roadmap, production readiness, developer workflow.
- `.github/workflows/` - CI and snapshot refresh automation.

## Required workflow for agents

1. Inspect existing code before editing.
2. Make focused commits, not giant unrelated rewrites.
3. Add or update tests for behavior changes.
4. Keep the PR body current when meaningful scope changes.
5. Never claim tests passed unless an actual run confirms it.
6. Prefer draft PRs while work is still moving.
7. Do not commit secrets, `.env`, local DBs, build output, or credential JSON.
8. Keep public-data/source-confidence language honest.

## Local validation commands

Windows PowerShell:

```powershell
.\scripts\dev-check.ps1
```

macOS/Linux/WSL:

```bash
bash scripts/dev-check.sh
```

Backend only:

```bash
cd backend
pytest
```

Frontend only:

```bash
cd frontend
npm run lint
npm run test
npm run build
```

E2E smoke:

```bash
cd frontend
npm run test:e2e
```

## Current PR context

PR #1: `Harden Ariva API operations, resilience, and developer workflow`

Major changes already added in this pass:

- operational response headers
- configurable in-process API rate limiting
- concurrent upstream adapter fetching with serial DB writes
- frontend API timeout and error-detail extraction
- saved-item internal href validation
- Docker healthcheck and `.dockerignore`
- Dependabot
- production-readiness docs
- security policy
- long-session dev workflow
- devcontainer
- one-command quality scripts

## Known risk areas to keep improving

1. Reduce database writes from public GET routes. Several public endpoints still create snapshots during normal reads.
2. Review Alembic metadata/imports so all models are included intentionally.
3. Add stronger frontend page-level error states and retry affordances.
4. Add structured logging around request IDs, upstream adapter errors, and alert evaluation.
5. Add a non-volatile cache/backing store if Ariva grows beyond a single backend process.
6. Add upstream contract tests or fixtures for FoodLK, Octane, PropertyLK, and AutoLens adapters.
7. Add OpenAPI examples for key endpoints.
8. Add deployment smoke workflow after backend/frontend URLs are known.

## Style conventions

- Python: type hints, explicit return types for public functions, pytest coverage for behavior.
- TypeScript: prefer typed API wrappers, test API edge cases, avoid hiding backend failures.
- Docs: be clear about source freshness, derived estimates, and limitations.
- UX: never imply live truth when a value is fixture-backed, cached, derived, or degraded.

## ChatGPT-specific operating rule

When resuming from ChatGPT, read this file first, then inspect PR #1 and `docs/ai-worklog.md`. Continue from the top unfinished item in `docs/engineering-backlog.md` unless the user gives a different priority.
