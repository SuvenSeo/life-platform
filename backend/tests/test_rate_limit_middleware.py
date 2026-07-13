from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware import InMemoryRateLimitMiddleware


def test_rate_limiter_returns_429_after_limit():
    app = FastAPI()
    app.add_middleware(
        InMemoryRateLimitMiddleware,
        enabled=True,
        max_requests=1,
        window_seconds=60,
        path_predicate=lambda path: path.startswith("/api/"),
    )

    @app.get("/api/ping")
    def ping():
        return {"status": "ok"}

    with TestClient(app) as client:
        first = client.get("/api/ping")
        second = client.get("/api/ping", headers={"X-Request-ID": "rate-limit-test"})

    assert first.status_code == 200
    assert first.headers["X-RateLimit-Limit"] == "1"
    assert first.headers["X-RateLimit-Remaining"] == "0"
    assert second.status_code == 429
    assert second.json()["detail"] == "Rate limit exceeded"
    assert second.headers["Retry-After"]
    assert second.headers["X-Request-ID"] == "rate-limit-test"
    assert second.headers["X-Content-Type-Options"] == "nosniff"
    assert second.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_rate_limiter_ignores_non_matching_paths():
    app = FastAPI()
    app.add_middleware(
        InMemoryRateLimitMiddleware,
        enabled=True,
        max_requests=1,
        window_seconds=60,
        path_predicate=lambda path: path.startswith("/api/"),
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    with TestClient(app) as client:
        first = client.get("/health")
        second = client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 200
    assert "X-RateLimit-Limit" not in first.headers
