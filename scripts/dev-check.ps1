$ErrorActionPreference = "Stop"

Write-Host "== Ariva local quality check ==" -ForegroundColor Cyan

if (-not (Test-Path "backend")) {
  throw "Run this script from the repository root."
}

Write-Host "== Backend dependencies ==" -ForegroundColor Cyan
Push-Location backend
if (-not (Test-Path ".venv")) {
  py -3.12 -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "== Backend tests ==" -ForegroundColor Cyan
$env:APP_ENV = "test"
$env:LIFE_USE_FIXTURES = "true"
$env:LIFE_TEST_AUTH_TOKEN = "life-test-token"
$env:LIFE_INTERNAL_TOKEN = "internal-test-token"
$env:DATABASE_URL = "sqlite:///./life_platform_dev_check.db"
pytest
Pop-Location

Write-Host "== Frontend dependencies ==" -ForegroundColor Cyan
Push-Location frontend
npm ci

Write-Host "== Frontend lint/test/build ==" -ForegroundColor Cyan
npm run lint
npm run test
npm run build
Pop-Location

Write-Host "== Done ==" -ForegroundColor Green
