from unittest.mock import patch

from fastapi.testclient import TestClient

from app.dependencies import enforce_rate_limit
from app.main import app


def test_create_link_allowed_when_under_limit(client: TestClient) -> None:
    # Re-enable the real dependency (conftest disables it by default).
    del app.dependency_overrides[enforce_rate_limit]
    with patch("app.dependencies.is_rate_limited", return_value=False):
        response = client.post("/links", json={"target_url": "https://example.com"})
    assert response.status_code == 201


def test_create_link_blocked_when_over_limit(client: TestClient) -> None:
    del app.dependency_overrides[enforce_rate_limit]
    with patch("app.dependencies.is_rate_limited", return_value=True):
        response = client.post("/links", json={"target_url": "https://example.com"})
    assert response.status_code == 429
