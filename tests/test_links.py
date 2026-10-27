from fastapi.testclient import TestClient


def test_create_link_returns_201(client: TestClient) -> None:
    response = client.post("/links", json={"target_url": "https://example.com"})
    assert response.status_code == 201
    body = response.json()
    assert body["target_url"] == "https://example.com/"
    assert body["click_count"] == 0
    assert len(body["short_code"]) == 7


def test_create_link_rejects_non_http_scheme(client: TestClient) -> None:
    response = client.post("/links", json={"target_url": "javascript:alert(1)"})
    assert response.status_code == 422


def test_create_link_rejects_missing_url(client: TestClient) -> None:
    response = client.post("/links", json={})
    assert response.status_code == 422


def test_short_code_is_not_exposed_as_id(client: TestClient) -> None:
    response = client.post("/links", json={"target_url": "https://example.com"})
    assert "id" not in response.json()  # internal id must stay hidden
