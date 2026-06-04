"""Test the /explain FastAPI endpoint."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_explain_endpoint_returns_explanation():
    response = client.post("/explain", json={"password": "Test123!"})
    assert response.status_code == 200
    data = response.json()
    assert data["password"] == "Test123!"
    assert "security_level" in data
    assert "assessment" in data
    assert isinstance(data["missing_requirements"], list)
    assert isinstance(data["pattern_warnings"], list)
    assert isinstance(data["suggestions"], list)
    assert "is_strong" in data


def test_explain_endpoint_requires_password():
    response = client.post("/explain", json={"password": ""})
    assert response.status_code == 422
