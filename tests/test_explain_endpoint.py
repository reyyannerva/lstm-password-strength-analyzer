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

def test_explain_endpoint_weak_password_contains_warnings():
    response = client.post("/explain", json={"password": "123456"})
    assert response.status_code == 200

    data = response.json()

    assert data["password"] == "123456"
    assert data["is_strong"] is False
    assert data["security_level"] in ["Çok Zayıf", "Zayıf", "Orta"]
    assert len(data["missing_requirements"]) > 0 or len(data["pattern_warnings"]) > 0
    assert isinstance(data["suggestions"], list)


def test_explain_endpoint_strong_password_structure():
    response = client.post("/explain", json={"password": "Str0ng!Pass123"})
    assert response.status_code == 200

    data = response.json()

    assert data["password"] == "Str0ng!Pass123"
    assert "security_level" in data
    assert "assessment" in data
    assert isinstance(data["missing_requirements"], list)
    assert isinstance(data["pattern_warnings"], list)
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["is_strong"], bool)


def test_explain_endpoint_rejects_whitespace_password():
    response = client.post("/explain", json={"password": "     "})
    assert response.status_code == 422
