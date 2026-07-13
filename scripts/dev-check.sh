#!/usr/bin/env bash
set -euo pipefail

echo "== Ariva local quality check =="

if [ ! -d "backend" ]; then
  echo "Run this script from the repository root." >&2
  exit 1
fi

echo "== Backend dependencies =="
cd backend
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "== Backend tests =="
export APP_ENV=test
export LIFE_USE_FIXTURES=true
export LIFE_TEST_AUTH_TOKEN=life-test-token
export LIFE_INTERNAL_TOKEN=internal-test-token
export DATABASE_URL=sqlite:///./life_platform_dev_check.db
pytest
cd ..

echo "== Frontend dependencies =="
cd frontend
npm ci

echo "== Frontend lint/test/build =="
npm run lint
npm run test
npm run build
cd ..

echo "== Done =="
