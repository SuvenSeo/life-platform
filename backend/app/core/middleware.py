from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach lightweight operational headers to every API response.

    The middleware is intentionally framework-level and dependency-free so it
    works in local development, tests, and Fly deployments without extra
    infrastructure. A caller-supplied X-Request-ID is preserved to support log
    correlation across a frontend, proxy, and API hop.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started_at = time.perf_counter()

        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started_at) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"

        if "X-Content-Type-Options" not in response.headers:
            response.headers["X-Content-Type-Options"] = "nosniff"
        if "Referrer-Policy" not in response.headers:
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """Small per-process rate limiter for public API protection.

    This is deliberately conservative: it protects a small Fly instance from
    accidental bursts and low-effort abuse without introducing Redis or another
    service. It is not a distributed quota system; production can replace it
    later with edge or Redis-backed limiting while keeping the same env names.
    """

    def __init__(
        self,
        app,
        *,
        enabled: bool,
        max_requests: int,
        window_seconds: int,
        path_predicate: Callable[[str], bool] | None = None,
    ) -> None:
        super().__init__(app)
        self.enabled = enabled and max_requests > 0 and window_seconds > 0
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.path_predicate = path_predicate or (lambda path: path.startswith("/api/"))
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled or not self.path_predicate(request.url.path):
            return await call_next(request)

        now = time.monotonic()
        bucket_key = self._bucket_key(request)
        bucket = self._buckets[bucket_key]
        cutoff = now - self.window_seconds

        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        remaining = max(self.max_requests - len(bucket), 0)
        reset_seconds = self.window_seconds if not bucket else max(int(bucket[0] + self.window_seconds - now), 1)

        if len(bucket) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "retry_after_seconds": reset_seconds,
                },
                headers={
                    "Retry-After": str(reset_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_seconds),
                },
            )

        bucket.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining - 1, 0))
        response.headers["X-RateLimit-Reset"] = str(reset_seconds)
        return response

    def _bucket_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client = forwarded_for.split(",", 1)[0].strip()
        elif request.client:
            client = request.client.host
        else:
            client = "unknown"
        return f"{client}:{request.url.path}"
