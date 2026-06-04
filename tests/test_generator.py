"""Password generator tests."""

from src.security.generator import generate_password


def test_generate_password_default_length():
    result = generate_password()

    assert isinstance(result, dict)
    assert result["length"] == 16
    assert len(result["password"]) == 16
    assert result["weak_patterns"] == []


def test_generate_password_custom_length():
    result = generate_password(length=20)

    assert result["length"] == 20
    assert len(result["password"]) == 20
    assert result["weak_patterns"] == []


def test_generate_password_enforces_minimum_length():
    result = generate_password(length=5)

    assert result["length"] >= 8
    assert len(result["password"]) >= 8


def test_generate_password_contains_required_character_types():
    result = generate_password(length=12)
    password = result["password"]

    assert any(c.isupper() for c in password)
    assert any(c.islower() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password)


def test_generate_password_multiple_calls_produce_unique_results():
    first = generate_password()["password"]
    second = generate_password()["password"]

    assert first != second
