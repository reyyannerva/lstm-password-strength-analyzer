"""End-to-end system integration tests."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_score_explain_generate_flow():
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert isinstance(health_response.json(), dict)

    score_response = client.post(
        "/score",
        json={"password": "Str0ng!Pass123"},
    )
    assert score_response.status_code == 200
    assert isinstance(score_response.json(), dict)
    assert len(score_response.json()) > 0

    explain_response = client.post(
        "/explain",
        json={"password": "password123"},
    )
    assert explain_response.status_code == 200
    assert isinstance(explain_response.json(), dict)
    assert len(explain_response.json()) > 0

    generate_response = client.post(
        "/generate",
        json={"length": 16},
    )
    assert generate_response.status_code == 200
    generate_data = generate_response.json()

    assert isinstance(generate_data, dict)
    assert len(generate_data) > 0
    assert "password" in str(generate_data).lower()


def test_generated_password_can_be_scored_and_explained():
    generate_response = client.post(
        "/generate",
        json={
            "length": 16,
            "use_uppercase": True,
            "use_lowercase": True,
            "use_digits": True,
            "use_special": True,
        },
    )

    assert generate_response.status_code == 200

    generate_data = generate_response.json()
    generated_password = (
        generate_data.get("password")
        or generate_data.get("generated_password")
        or generate_data.get("secure_password")
    )

    assert generated_password is not None
    assert isinstance(generated_password, str)
    assert len(generated_password) >= 8

    score_response = client.post(
        "/score",
        json={"password": generated_password},
    )

    assert score_response.status_code == 200
    assert isinstance(score_response.json(), dict)

    explain_response = client.post(
        "/explain",
        json={"password": generated_password},
    )

    assert explain_response.status_code == 200
    assert isinstance(explain_response.json(), dict)


def test_frontend_files_exist_and_contain_api_integration():
    index_path = "frontend/index.html"
    script_path = "frontend/script.js"

    with open(index_path, "r", encoding="utf-8") as file:
        index_content = file.read().lower()

    with open(script_path, "r", encoding="utf-8") as file:
        script_content = file.read().lower()

    assert "<html" in index_content
    assert "script.js" in index_content
    assert "fetch" in script_content
    assert "/score" in script_content
    assert "/explain" in script_content
    assert "/generate" in script_content


def test_security_modules_are_importable():
    from src.security.generator import generate_password
    from src.security.patterns import detect_patterns
    from src.security.risk_scorer import calculate_hybrid_score

    generated = generate_password(length=16)
    password = generated.get("password") or generated.get("generated_password")

    assert password is not None
    assert isinstance(password, str)

    patterns = detect_patterns("password123")
    assert isinstance(patterns, list)

    score = calculate_hybrid_score("Str0ng!Pass123")
    assert isinstance(score, dict)
    assert "security_level" in score
