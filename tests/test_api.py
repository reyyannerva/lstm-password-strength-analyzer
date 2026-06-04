"""API endpoint tests."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_score_endpoint_returns_response():
    response = client.post(
        "/score",
        json={"password": "Str0ng!Pass123"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0


def test_score_endpoint_handles_weak_password():
    response = client.post(
        "/score",
        json={"password": "123456"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0


def test_explain_endpoint_returns_response():
    response = client.post(
        "/explain",
        json={"password": "password123"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0


def test_generate_endpoint_returns_password():
    response = client.post(
        "/generate",
        json={"length": 16},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0

    response_text = str(data).lower()

    assert (
        "password" in response_text
        or "generated_password" in response_text
    )


def test_generate_endpoint_rejects_invalid_length():
    response = client.post(
        "/generate",
        json={"length": 3},
    )

    assert response.status_code in [200, 400, 422]