from fastapi.testclient import TestClient


def _create_link(client: TestClient, url: str = "https://example.com") -> str:
    response = client.post("/links", json={"target_url": url})
    assert response.status_code == 201
    return response.json()["short_code"]


def test_redirect_returns_307_with_location(client: TestClient) -> None:
    short_code = _create_link(client, "https://example.com")
    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"


def test_redirect_unknown_code_returns_404(client: TestClient) -> None:
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == 404


def test_redirect_is_case_sensitive(client: TestClient) -> None:
    short_code = _create_link(client)
    response = client.get(f"/{short_code.swapcase()}", follow_redirects=False)
    assert response.status_code == 404  # base62 codes are case-sensitive
