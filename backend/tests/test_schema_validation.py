import pytest
from pydantic import ValidationError

from app.schemas import AlertRuleCreate, SavedItemCreate


def test_saved_item_rejects_external_href():
    with pytest.raises(ValidationError, match="href must be an internal Ariva path"):
        SavedItemCreate(domain_key="food", label="Bad link", href="https://evil.example/phish")


@pytest.mark.parametrize("href", ["/", "/?page=intelligence", "/domains/food"])
def test_saved_item_allows_internal_href(href):
    payload = SavedItemCreate(domain_key="food", label="Rice watch", href=href)

    assert payload.href == href


def test_metric_alert_requires_threshold():
    with pytest.raises(ValidationError, match="threshold_value is required"):
        AlertRuleCreate(domain_key="fuel", label="Fuel ceiling", metric_label="Petrol 92", condition="above")
