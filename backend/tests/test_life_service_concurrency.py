import asyncio
from datetime import timezone

import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import IntegrationRun, utc_now
from app.db.session import SessionLocal
from app.schemas import DomainSignal
from app.services.life_service import LifeService


class CoordinatedAdapter:
    category = "test"
    api_base = "https://example.test/api"
    homepage_url = "https://example.test"

    def __init__(self, key: str, label: str, state: dict):
        self.key = key
        self.label = label
        self.state = state

    async def fetch(self, client):
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
async def test_domain_adapters_fetch_concurrently_and_record_runs():
    state = {"active": set(), "saw_parallel_fetch": False}
    service = LifeService(get_settings())
    service._cache.clear()
    service.adapters = [
        CoordinatedAdapter("food", "Food Test", state),
        CoordinatedAdapter("fuel", "Fuel Test", state),
    ]

    with SessionLocal() as db:
        signals = await service.get_domain_signals(db, force_refresh=True)
        runs = db.scalars(select(IntegrationRun).order_by(IntegrationRun.domain_key)).all()

    assert state["saw_parallel_fetch"] is True
    assert [signal.key for signal in signals] == ["food", "fuel"]
    assert [run.domain_key for run in runs] == ["food", "fuel"]
    assert all(run.status == "completed" for run in runs)
