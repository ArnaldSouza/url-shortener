import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def _create_link(client: TestClient, url: str = "https://example.com") -> str:
    response = client.post("/links", json={"target_url": url})
    assert response.status_code == 201
    return response.json()["short_code"]


def test_most_clicked_cache_miss_queries_db_and_caches(client: TestClient) -> None:
    short_code = _create_link(client, "https://example.com")

    mock_redis = MagicMock()
    mock_redis.get.return_value = None  # cache miss
    with patch("app.services.stats.redis_client", mock_redis):
        response = client.get("/stats/most-clicked")

    assert response.status_code == 200
    assert response.json()["short_code"] == short_code
    mock_redis.set.assert_called_once()  # result was written to cache


def test_most_clicked_cache_hit_skips_db(client: TestClient) -> None:
    cached_payload = {
        "short_code": "cached1",
        "target_url": "https://cached.example.com/",
        "click_count": 99,
    }
    mock_redis = MagicMock()
    mock_redis.get.return_value = json.dumps(cached_payload)  # cache hit
    with patch("app.services.stats.redis_client", mock_redis):
        response = client.get("/stats/most-clicked")

    assert response.status_code == 200
    assert response.json() == cached_payload
    mock_redis.set.assert_not_called()  # nothing re-cached on a hit


def test_most_clicked_empty_db_returns_404(client: TestClient) -> None:
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    with patch("app.services.stats.redis_client", mock_redis):
        response = client.get("/stats/most-clicked")

    assert response.status_code == 404
