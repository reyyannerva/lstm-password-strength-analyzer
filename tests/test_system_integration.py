"""End-to-end system integration tests for the LSTM password strength analyzer."""

from pathlib import Path

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def _extract_generated_password(data: dict):
    """Extract generated password from different possible API response schemas."""
    if not isinstance(data, dict):
        return None

    for key in ["password", "generated_password", "secure_password"]:
        value = data.get(key)
        if isinstance(value, str) and value:
            return value

    for nested_key in ["result", "data", "generation", "metadata"]:
        nested = data.get(nested_key)
        if isinstance(nested, dict):
            value = _extract_generated_password(nested)
            if value:
                return value

    return None


def _assert_non_empty_json_response(response):
    """Validate successful non-empty JSON API response."""
    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert len(data) > 0

    return data


def test_complete_api_flow_health_score_explain_generate():
    """Validate that core API endpoints work together without critical errors."""
    health_data = _assert_non_empty_json_response(client.get("/health"))
    assert isinstance(health_data, dict)

    score_data = _assert_non_empty_json_response(
        client.post("/score", json={"password": "Str0ng!Pass123"})
    )
    assert isinstance(score_data, dict)

    explain_data = _assert_non_empty_json_response(
        client.post("/explain", json={"password": "password123"})
    )
    assert isinstance(explain_data, dict)

    generate_data = _assert_non_empty_json_response(
        client.post("/generate", json={"length": 16})
    )
    generated_password = _extract_generated_password(generate_data)

    assert generated_password is not None
    assert isinstance(generated_password, str)
    assert len(generated_password) >= 8


def test_generated_password_can_be_analyzed_again():
    """Validate that a generated password can be passed back into analysis endpoints."""
    generate_data = _assert_non_empty_json_response(
        client.post(
            "/generate",
            json={
                "length": 16,
                "use_uppercase": True,
                "use_lowercase": True,
                "use_digits": True,
                "use_special": True,
            },
        )
    )

    generated_password = _extract_generated_password(generate_data)

    assert generated_password is not None
    assert isinstance(generated_password, str)
    assert len(generated_password) >= 8

    score_data = _assert_non_empty_json_response(
        client.post("/score", json={"password": generated_password})
    )
    assert isinstance(score_data, dict)

    explain_data = _assert_non_empty_json_response(
        client.post("/explain", json={"password": generated_password})
    )
    assert isinstance(explain_data, dict)


def test_frontend_files_exist_and_reference_api_endpoints():
    """Validate that frontend files exist and reference backend API endpoints."""
    index_path = Path("frontend/index.html")
    script_path = Path("frontend/script.js")

    assert index_path.exists()
    assert script_path.exists()

    index_content = index_path.read_text(encoding="utf-8").lower()
    script_content = script_path.read_text(encoding="utf-8").lower()

    assert "<html" in index_content
    assert "script" in index_content
    assert "fetch" in script_content
    assert "/score" in script_content
    assert "/explain" in script_content
    assert "/generate" in script_content


def test_security_modules_are_importable_and_callable():
    """Validate that core security modules can be imported and called together."""
    from src.security.generator import generate_password
    from src.security.patterns import detect_patterns
    from src.security.risk_scorer import calculate_hybrid_score

    generated_result = generate_password(length=16)

    assert isinstance(generated_result, dict)

    generated_password = _extract_generated_password(generated_result)

    assert generated_password is not None
    assert isinstance(generated_password, str)
    assert len(generated_password) >= 8

    patterns = detect_patterns("password123")
    assert isinstance(patterns, list)

    score = calculate_hybrid_score("Str0ng!Pass123")
    assert isinstance(score, dict)
    assert len(score) > 0
    assert "security_level" in score or "final_score" in score


def test_invalid_generate_length_does_not_break_system():
    """Validate that invalid generate requests are handled safely."""
    response = client.post("/generate", json={"length": 3})

    assert response.status_code in [200, 400, 422]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
