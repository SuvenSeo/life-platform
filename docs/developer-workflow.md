# Developer Workflow

This workflow is designed for long implementation sessions on Ariva without losing context.

## One-command checks

From the repository root:

### Windows PowerShell

```powershell
.\scripts\dev-check.ps1
```

### macOS/Linux/WSL

```bash
bash scripts/dev-check.sh
```

Both scripts install backend and frontend dependencies, then run backend tests, frontend lint, frontend tests, and frontend build.

## Recommended long-session loop

1. Start from an isolated branch.
2. Run the one-command check before changing behavior.
3. Make one focused change at a time.
4. Add or update tests in the same pass.
5. Re-run the smallest relevant test first.
6. Run the full one-command check before opening or updating the PR.
7. Update the PR body with what changed and what remains risky.
8. Wait for CI before marking a draft PR ready.

## Local backend

```bash
cd backend
source .venv/bin/activate
export APP_ENV=development
export LIFE_USE_FIXTURES=true
export DATABASE_URL=sqlite:///./life_platform.db
uvicorn app.main:app --reload --port 8090
```

Windows PowerShell equivalent:

```powershell
cd backend
. .\.venv\Scripts\Activate.ps1
$env:APP_ENV = "development"
$env:LIFE_USE_FIXTURES = "true"
$env:DATABASE_URL = "sqlite:///./life_platform.db"
uvicorn app.main:app --reload --port 8090
```

## Local frontend

```bash
cd frontend
VITE_API_URL=http://127.0.0.1:8090/api/v1 npm run dev
```

Windows PowerShell equivalent:

```powershell
cd frontend
$env:VITE_API_URL = "http://127.0.0.1:8090/api/v1"
npm run dev
```

## Devcontainer

Open the repository in VS Code and choose **Reopen in Container**. The container installs Python 3.12, Node 24, backend dependencies, and frontend dependencies. Ports 8090, 3001, and 5173 are forwarded.

## PR discipline

Keep draft PRs open while implementation is still moving. Mark ready only when:

- backend tests pass
- frontend lint/test/build pass
- Playwright smoke passes or is intentionally deferred with a clear note
- docs/config changes are reflected in README or operational docs
