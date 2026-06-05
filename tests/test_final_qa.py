"""Final QA tests for release readiness."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_final_release_core_endpoints_are_available():
    health = client.get("/health")
    assert health.status_code == 200
    assert isinstance(health.json(), dict)

    score = client.post("/score", json={"password": "Str0ng!Pass123"})
    assert score.status_code == 200
    assert isinstance(score.json(), dict)

    explain = client.post("/explain", json={"password": "password123"})
    assert explain.status_code == 200
    assert isinstance(explain.json(), dict)

    generate = client.post("/generate", json={"length": 16})
    assert generate.status_code == 200
    assert isinstance(generate.json(), dict)


def test_final_release_generated_password_flow():
    generate = client.post(
        "/generate",
        json={
            "length": 16,
            "use_uppercase": True,
            "use_lowercase": True,
            "use_digits": True,
            "use_special": True,
        },
    )

    assert generate.status_code == 200

    data = generate.json()
    password = (
        data.get("password")
        or data.get("generated_password")
        or data.get("secure_password")
    )

    assert password is not None
    assert isinstance(password, str)
    assert len(password) >= 8

    score = client.post("/score", json={"password": password})
    assert score.status_code == 200
    assert isinstance(score.json(), dict)

    explain = client.post("/explain", json={"password": password})
    assert explain.status_code == 200
    assert isinstance(explain.json(), dict)


def test_final_release_frontend_files_exist():
    with open("frontend/index.html", "r", encoding="utf-8") as file:
        index_content = file.read().lower()

    with open("frontend/script.js", "r", encoding="utf-8") as file:
        script_content = file.read().lower()

    assert "<html" in index_content
    assert "script" in index_content
    assert "fetch" in script_content
    assert "/score" in script_content
    assert "/explain" in script_content
    assert "/generate" in script_content
