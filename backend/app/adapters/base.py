from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import Settings
from app.schemas import DomainHighlight, DomainMetric, DomainSignal


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not isinstance(value, str):
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def as_number(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


class DomainAdapter(ABC):
    key: str
    label: str
    category: str
    homepage_url: str

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    @abstractmethod
    def api_base(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def fetch(self, client: httpx.AsyncClient) -> DomainSignal:
        raise NotImplementedError

    @abstractmethod
    def fixture_signal(self, *, error: str | None = None) -> DomainSignal:
        raise NotImplementedError

    async def get_json(self, client: httpx.AsyncClient, path: str, **params: Any) -> dict[str, Any]:
        url = f"{self.api_base.rstrip('/')}/{path.lstrip('/')}"
        response = await client.get(url, params={k: v for k, v in params.items() if v is not None})
        response.raise_for_status()
        return response.json()

    def degraded_fixture(self, message: str) -> DomainSignal:
        signal = self.fixture_signal(error=message)
        signal.status = "degraded"
        signal.health_score = min(signal.health_score, 45)
        signal.errors.append(message)
        signal.freshness_note = f"Using fallback structure because {self.label} could not be reached."
        return signal

    def metric(self, label: str, value: Any, unit: str | None = None, description: str | None = None) -> DomainMetric:
        return DomainMetric(label=label, value=value, unit=unit, description=description)

    def highlight(self, label: str, value: str, severity: str = "neutral", href: str | None = None) -> DomainHighlight:
        return DomainHighlight(label=label, value=value, severity=severity, href=href)
