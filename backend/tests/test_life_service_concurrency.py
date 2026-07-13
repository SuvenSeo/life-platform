import asyncio
from datetime import timezone
from typing import Any

import httpx
import pytest

from app.core.config import get_settings
from app.db.models import utc_now
from app.schemas import DomainSignal
from app.services.life_service import LifeService


class CoordinatedAdapter:
    category = "test"
    api_base = "https://example.test/api"
    homepage_url = "https://example.test"

    def __init__(self, key: str, label: str, state: dict[str, Any]):
        self.key = key
        self.label = label
        self.state = state

    async def fetch(self, client: httpx.AsyncClient):
        self.state["active"].add(self.key)
        if len(self.state["active"]) > 1:
            self.state["saw_parallel_fetch"] = True
        await asyncio.sleep(0)
        self.state["active"].remove(self.key)
        return DomainSignal(
            key=self.key,
            label=self.label,
            category=self.category,
            status="healthy",
            health_score=91,
            summary=f"{self.label} test signal.",
            api_base=self.api_base,
            source_url=self.homepage_url,
            homepage_url=self.homepage_url,
            last_updated_at=utc_now().astimezone(timezone.utc),
            observed_at=utc_now().astimezone(timezone.utc),
            freshness_note="Test freshness.",
            metrics=[],
            highlights=[],
            top_items=[],
            sources=[],
            errors=[],
        )

    def degraded_fixture(self, error: str):
        return DomainSignal(
            key=self.key,
            label=self.label,
            category=self.category,
            status="offline",
            health_score=0,
            summary="Fixture fallback.",
            api_base=self.api_base,
            source_url=self.homepage_url,
            homepage_url=self.homepage_url,
            last_updated_at=None,
            observed_at=utc_now().astimezone(timezone.utc),
            freshness_note="Fallback freshness.",
            metrics=[],
            highlights=[],
            top_items=[],
            sources=[],
            errors=[error],
        )


@pytest.mark.asyncio
async def test_domain_adapters_fetch_concurrently():
    state: dict[str, Any] = {"active": set(), "saw_parallel_fetch": False}
    service = LifeService(get_settings())
    service.adapters = [
        CoordinatedAdapter("food", "Food Test", state),
        CoordinatedAdapter("fuel", "Fuel Test", state),
    ]

    async with httpx.AsyncClient() as client:
        signals = await service._fetch_adapters_concurrently(client)

    assert state["saw_parallel_fetch"] is True
    assert [signal.key for signal in signals] == ["food", "fuel"]
