def test_health_includes_operational_headers(client):
    response = client.get("/health", headers={"X-Request-ID": "smoke-test-request"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "smoke-test-request"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert float(response.headers["X-Process-Time-Ms"]) >= 0
