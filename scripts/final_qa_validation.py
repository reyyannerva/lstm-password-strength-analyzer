"""Final QA validation script for LSTM Password Strength Analyzer."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


TEST_PASSWORDS = [
    ("123456", "weak"),
    ("password123", "weak"),
    ("Password123", "medium"),
    ("Str0ng!Pass123", "strong"),
    ("A9!xK2#mQ7", "strong"),
]


def assert_success_response(response, endpoint_name):
    if response.status_code != 200:
        raise AssertionError(f"{endpoint_name} failed with status {response.status_code}")

    data = response.json()

    if not isinstance(data, dict):
        raise AssertionError(f"{endpoint_name} response is not a JSON object")

    if len(data) == 0:
        raise AssertionError(f"{endpoint_name} returned empty response")

    return data


def run_final_qa():
    print("Final QA validation started...")

    health_data = assert_success_response(client.get("/health"), "/health")
    print("[OK] /health:", health_data)

    for password, expected_group in TEST_PASSWORDS:
        score_data = assert_success_response(
            client.post("/score", json={"password": password}),
            "/score",
        )

        explain_data = assert_success_response(
            client.post("/explain", json={"password": password}),
            "/explain",
        )

        print(f"[OK] Password tested: {password} | Expected group: {expected_group}")
        print("     Score response keys:", list(score_data.keys()))
        print("     Explain response keys:", list(explain_data.keys()))

    generate_data = assert_success_response(
        client.post(
            "/generate",
            json={
                "length": 16,
                "use_uppercase": True,
                "use_lowercase": True,
                "use_digits": True,
                "use_special": True,
            },
        ),
        "/generate",
    )

    generated_password = (
        generate_data.get("password")
        or generate_data.get("generated_password")
        or generate_data.get("secure_password")
    )

    if not generated_password:
        raise AssertionError("Generated password could not be found in /generate response")

    print("[OK] Generated password:", generated_password)

    generated_score = assert_success_response(
        client.post("/score", json={"password": generated_password}),
        "/score generated password",
    )

    generated_explain = assert_success_response(
        client.post("/explain", json={"password": generated_password}),
        "/explain generated password",
    )

    print("[OK] Generated password can be scored.")
    print("[OK] Generated password can be explained.")
    print("     Generated score keys:", list(generated_score.keys()))
    print("     Generated explain keys:", list(generated_explain.keys()))

    print("Final QA validation completed successfully.")


if __name__ == "__main__":
    run_final_qa()
