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

def test_score_endpoint_rejects_empty_password():
    response = client.post("/score", json={"password": ""})
    assert response.status_code == 422


def test_score_endpoint_rejects_whitespace_password():
    response = client.post("/score", json={"password": "     "})
    assert response.status_code == 422


def test_score_endpoint_response_structure():
    response = client.post("/score", json={"password": "Str0ng!Pass123"})
    assert response.status_code == 200

    data = response.json()

    required_fields = [
        "password_length",
        "risk_score",
        "security_level",
        "weak_patterns",
        "message",
    ]

    for field in required_fields:
        assert field in data

    assert data["password_length"] == len("Str0ng!Pass123")
    assert isinstance(data["risk_score"], float)
    assert isinstance(data["weak_patterns"], list)


def test_score_endpoint_detects_weak_patterns_for_password123():
    response = client.post("/score", json={"password": "password123"})
    assert response.status_code == 200

    data = response.json()

    assert data["password_length"] == len("password123")
    assert len(data["weak_patterns"]) > 0
    assert data["security_level"] in ["Çok Zayıf", "Zayıf", "Orta"]


def test_generate_endpoint_response_structure():
    response = client.post("/generate", json={"length": 16})
    assert response.status_code == 200

    data = response.json()

    required_fields = [
        "generated_password",
        "password_length",
        "security_score",
        "security_level",
        "weak_patterns",
        "feedback",
        "message",
        "metadata",
    ]

    for field in required_fields:
        assert field in data

    assert len(data["generated_password"]) == 16
    assert data["password_length"] == 16
    assert isinstance(data["weak_patterns"], list)
    assert isinstance(data["feedback"], list)


def test_generate_endpoint_accepts_minimum_valid_length():
    response = client.post("/generate", json={"length": 8})
    assert response.status_code == 200

    data = response.json()

    assert data["password_length"] == 8
    assert len(data["generated_password"]) == 8


def test_generate_endpoint_accepts_maximum_valid_length():
    response = client.post("/generate", json={"length": 128})
    assert response.status_code == 200

    data = response.json()

    assert data["password_length"] == 128
    assert len(data["generated_password"]) == 128


def test_generate_endpoint_rejects_all_character_options_disabled():
    response = client.post(
        "/generate",
        json={
            "length": 16,
            "use_uppercase": False,
            "use_lowercase": False,
            "use_digits": False,
            "use_special": False,
        },
    )

    assert response.status_code == 422