def test_life_overview_returns_all_domains(client):
    response = client.get("/api/v1/life/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["headline"].startswith("Today in Sri Lanka")
    assert {domain["key"] for domain in payload["domains"]} == {
        "food",
        "fuel",
        "property",
        "vehicle",
        "utilities",
        "gas",
        "transport",
        "retail",
        "indices",
        "areas",
    }
    assert payload["affordability"]["total_monthly_lkr"] > 0
    assert payload["source_health"]["total"] == 10


def test_life_domains_records_snapshots(client):
    response = client.get("/api/v1/life/domains?force_refresh=true")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 10

    trends = client.get("/api/v1/life/trends?domain=food")
    assert trends.status_code == 200
    assert len(trends.json()["points"]) >= 1


def test_life_search_finds_domain_and_metric(client):
    client.get("/api/v1/life/overview")
    response = client.get("/api/v1/life/search?q=petrol")
    assert response.status_code == 200
    results = response.json()
    assert any(item["domain"] == "fuel" for item in results)


def test_life_search_routes_vehicle_and_food_intents(client):
    client.get("/api/v1/life/overview")

    vehicle_response = client.get("/api/v1/life/search?q=Toyota%20Axio")
    assert vehicle_response.status_code == 200
    vehicle_results = vehicle_response.json()
    assert vehicle_results[0]["domain"] == "vehicle"
    assert not any(item["domain"] == "food" for item in vehicle_results[:3])

    food_response = client.get("/api/v1/life/search?q=rice")
    assert food_response.status_code == 200
    food_results = food_response.json()
    assert food_results[0]["domain"] == "food"


def test_life_affordability_profiles(client):
    response = client.get("/api/v1/life/affordability?district=Colombo&profile=commuter")
    assert response.status_code == 200
    payload = response.json()
    assert payload["district"] == "Colombo"
    assert payload["profile"] == "commuter"
    assert any(item["key"] == "fuel" for item in payload["breakdown"])


def test_life_pipeline_degrades_without_breaking(client):
    response = client.get("/api/v1/life/pipeline")
    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] in {"healthy", "degraded", "offline"}
    assert len(payload["domains"]) == 10


def test_living_atlas_v2_public_endpoints(client):
    cost = client.get("/api/v1/life/cost-command?district=Colombo&profile=family&locale=si")
    assert cost.status_code == 200
    cost_payload = cost.json()
    assert cost_payload["locale"] == "si"
    assert cost_payload["total_monthly_lkr"] > 0
    assert any(item["key"] == "gas" for item in cost_payload["items"])
    assert cost_payload["items"][0]["label"] == "ආහාර සහ සිල්ලර"

    atlas = client.get("/api/v1/life/atlas?district=Kandy&locale=ta")
    assert atlas.status_code == 200
    atlas_payload = atlas.json()
    assert atlas_payload["locale"] == "ta"
    assert atlas_payload["selected"]["district"] == "Kandy"
    assert len(atlas_payload["district_scores"]) >= 8
    assert "சுயவிவரத்திற்கு" in atlas_payload["narrative"]

    score = client.get("/api/v1/life/areas/score?district=Galle&profile=commuter&locale=si")
    assert score.status_code == 200
    assert score.json()["profile"] == "commuter"
    assert score.json()["components"][0]["label"] == "කුලී පීඩනය"

    utilities = client.get("/api/v1/life/utilities?district=Colombo")
    assert utilities.status_code == 200
    assert utilities.json()["electricity"]

    transport = client.get("/api/v1/life/transport?from=Gampaha&to=Colombo")
    assert transport.status_code == 200
    assert transport.json()["from_area"] == "Gampaha"
    assert transport.json()["to_area"] == "Colombo"
    assert any(item["mode"] == "bus" for item in transport.json()["options"])

    retail = client.get("/api/v1/life/retail/offers?q=rice&district=Sri%20Lanka")
    assert retail.status_code == 200
    assert any("Rice" in item["item_name"] for item in retail.json()["offers"])

    insights = client.get("/api/v1/life/insights?domain=indices")
    assert insights.status_code == 200
    assert insights.json()["insights"]


def test_life_i18n_has_three_locales(client):
    for locale in ["en", "si", "ta"]:
        response = client.get(f"/api/v1/life/i18n?locale={locale}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["locale"] == locale
        assert payload["labels"]["today"]
        assert payload["domains"]["utilities"]
        assert payload["sources"]["dcs-ccpi"]


def test_living_atlas_tables_exist(client):
    response = client.get("/api/v1/life/cost-command")
    assert response.status_code == 200
    pipeline = client.get("/api/v1/life/pipeline")
    assert pipeline.status_code == 200


def test_me_endpoints_require_auth(client):
    response = client.get("/api/v1/me/profile")
    assert response.status_code == 401


def test_hybrid_account_profile_saved_items_alerts_and_notifications(client):
    headers = {"Authorization": "Bearer life-test-token"}

    profile = client.get("/api/v1/me/profile", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["district"] == "Sri Lanka"

    updated = client.put(
        "/api/v1/me/profile",
        headers=headers,
        json={"district": "Colombo", "profile": "commuter", "default_locale": "si"},
    )
    assert updated.status_code == 200
    assert updated.json()["district"] == "Colombo"
    assert updated.json()["profile"] == "commuter"
    assert updated.json()["default_locale"] == "si"

    saved = client.post(
        "/api/v1/me/saved-items",
        headers=headers,
        json={"domain_key": "food", "label": "Rice watch", "query": "rice", "href": "/intelligence", "payload": {"unit": "1kg"}},
    )
    assert saved.status_code == 201
    saved_id = saved.json()["id"]
    assert client.get("/api/v1/me/saved-items", headers=headers).json()[0]["label"] == "Rice watch"

    alert = client.post(
        "/api/v1/me/alerts",
        headers=headers,
        json={
            "domain_key": "fuel",
            "label": "Petrol 92 ceiling",
            "metric_label": "Petrol 92",
            "condition": "above",
            "threshold_value": 100,
        },
    )
    assert alert.status_code == 201
    assert alert.json()["enabled"] is True

    pulse = client.get("/api/v1/me/life-pulse", headers=headers)
    assert pulse.status_code == 200
    payload = pulse.json()
    assert payload["profile"]["district"] == "Colombo"
    assert payload["saved_items"][0]["id"] == saved_id
    assert payload["unread_count"] == 1
    assert payload["notifications"][0]["source_domain"] == "fuel"

    notification_id = payload["notifications"][0]["id"]
    read = client.patch(f"/api/v1/me/notifications/{notification_id}", headers=headers, json={"read": True})
    assert read.status_code == 200
    assert read.json()["read_at"] is not None

    delete_saved = client.delete(f"/api/v1/me/saved-items/{saved_id}", headers=headers)
    assert delete_saved.status_code == 204


def test_internal_alert_evaluation_is_token_protected_and_idempotent(client):
    headers = {"Authorization": "Bearer life-test-token"}
    client.get("/api/v1/me/profile", headers=headers)
    client.post(
        "/api/v1/me/alerts",
        headers=headers,
        json={
            "domain_key": "fuel",
            "label": "Fuel watch",
            "metric_label": "Petrol 92",
            "condition": "above",
            "threshold_value": 100,
        },
    )

    forbidden = client.post("/api/v1/internal/alerts/evaluate")
    assert forbidden.status_code in {401, 403}

    internal_headers = {"Authorization": "Bearer internal-test-token"}
    first = client.post("/api/v1/internal/alerts/evaluate", headers=internal_headers)
    assert first.status_code == 200
    assert first.json()["users_checked"] == 1
    assert first.json()["notifications_created"] == 1

    second = client.post("/api/v1/internal/alerts/evaluate", headers=internal_headers)
    assert second.status_code == 200
    assert second.json()["notifications_created"] == 0
