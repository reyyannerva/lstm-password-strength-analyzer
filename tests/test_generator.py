"""Password generator tests."""

import re

from src.security.generator import _meets_criteria, generate_password
from src.security.patterns import detect_patterns


def test_meets_criteria_returns_false_for_weak_password():
    assert not _meets_criteria("password")
    assert not _meets_criteria("12345678")


def test_meets_criteria_returns_true_for_strong_password():
    assert _meets_criteria("Ab1!fHr9")


def test_generate_password_default_length_and_structure():
    result = generate_password()
    password = result["password"]

    assert isinstance(result, dict)
    assert result["length"] == 16
    assert len(password) == 16
    assert re.search(r"[A-Z]", password)
    assert re.search(r"[a-z]", password)
    assert re.search(r"\d", password)
    assert re.search(r"[^a-zA-Z0-9]", password)
    assert result["weak_patterns"] == []


def test_generate_password_custom_length():
    result = generate_password(length=20)

    assert result["length"] == 20
    assert len(result["password"]) == 20
    assert result["weak_patterns"] == []


def test_generate_password_minimum_length_enforced():
    result = generate_password(length=4)

    assert result["length"] >= 8
    assert len(result["password"]) >= 8


def test_generate_password_contains_required_character_types():
    result = generate_password(length=12)
    password = result["password"]

    assert any(c.isupper() for c in password)
    assert any(c.islower() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password)


def test_generate_password_has_no_detected_weak_patterns():
    result = generate_password(length=16)

    assert detect_patterns(result["password"]) == []
    assert result["weak_patterns"] == []


def test_generate_password_multiple_calls_produce_unique_results():
    first = generate_password()["password"]
    second = generate_password()["password"]

    assert first != second