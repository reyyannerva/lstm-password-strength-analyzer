"""
Rule-based password analysis tests.
"""

import pytest

try:
    from src.security.rules import (
        check_length,
        check_uppercase,
        check_lowercase,
        check_digits,
        check_special_chars,
        analyze_rules,
    )
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


@pytest.fixture
def skip_if_unavailable():
    if not AVAILABLE:
        pytest.skip("src/security/rules.py modülü mevcut değil.")


def test_check_length_valid(skip_if_unavailable):
    result = check_length("password123", min_length=8, max_length=128)
    assert result["passed"] is True
    assert "details" in result


def test_check_length_too_short(skip_if_unavailable):
    result = check_length("short", min_length=8, max_length=128)
    assert result["passed"] is False
    assert "details" in result


def test_check_length_too_long(skip_if_unavailable):
    result = check_length("a" * 200, min_length=8, max_length=128)
    assert result["passed"] is False
    assert "details" in result


def test_check_uppercase_present(skip_if_unavailable):
    result = check_uppercase("Password")
    assert result["passed"] is True
    assert "details" in result


def test_check_uppercase_absent(skip_if_unavailable):
    result = check_uppercase("password")
    assert result["passed"] is False
    assert "details" in result


def test_check_uppercase_empty(skip_if_unavailable):
    result = check_uppercase("")
    assert result["passed"] is False
    assert "details" in result


def test_check_lowercase_present(skip_if_unavailable):
    result = check_lowercase("Password")
    assert result["passed"] is True
    assert "details" in result


def test_check_lowercase_absent(skip_if_unavailable):
    result = check_lowercase("PASSWORD")
    assert result["passed"] is False
    assert "details" in result


def test_check_lowercase_empty(skip_if_unavailable):
    result = check_lowercase("")
    assert result["passed"] is False
    assert "details" in result


def test_check_digits_present(skip_if_unavailable):
    result = check_digits("Password123")
    assert result["passed"] is True
    assert "details" in result


def test_check_digits_absent(skip_if_unavailable):
    result = check_digits("PasswordABC")
    assert result["passed"] is False
    assert "details" in result


def test_check_digits_empty(skip_if_unavailable):
    result = check_digits("")
    assert result["passed"] is False
    assert "details" in result


def test_check_special_chars_present(skip_if_unavailable):
    result = check_special_chars("Password123!")
    assert result["passed"] is True
    assert "details" in result


def test_check_special_chars_absent(skip_if_unavailable):
    result = check_special_chars("Password123")
    assert result["passed"] is False
    assert "details" in result


def test_check_special_chars_empty(skip_if_unavailable):
    result = check_special_chars("")
    assert result["passed"] is False
    assert "details" in result


def test_analyze_rules_strong_password(skip_if_unavailable):
    result = analyze_rules("SecurePass123!")
    assert result["password"] == "SecurePass123!"
    assert "checks" in result
    assert "passed_count" in result
    assert "total_checks" in result
    assert "score" in result
    assert result["total_checks"] == 5


def test_analyze_rules_weak_password(skip_if_unavailable):
    result = analyze_rules("weak")
    assert result["password"] == "weak"
    assert result["passed_count"] < result["total_checks"]
    assert result["score"] < 100


def test_analyze_rules_empty_password(skip_if_unavailable):
    result = analyze_rules("")
    assert result["password"] == ""
    assert result["passed_count"] == 0


def test_analyze_rules_all_checks_present(skip_if_unavailable):
    result = analyze_rules("P@ssw0rd")
    expected_checks = ["length", "uppercase", "lowercase", "digits", "special_chars"]
    assert set(result["checks"].keys()) == set(expected_checks)


def test_analyze_rules_none_password(skip_if_unavailable):
    result = analyze_rules(None)
    assert result["password"] == ""
    assert result["passed_count"] >= 0


def test_analyze_rules_numeric_password(skip_if_unavailable):
    result = analyze_rules("12345678")
    assert result["checks"]["digits"]["passed"] is True
    assert result["checks"]["uppercase"]["passed"] is False
    assert result["checks"]["lowercase"]["passed"] is False
    assert result["checks"]["special_chars"]["passed"] is False


def test_analyze_rules_custom_length_requirements(skip_if_unavailable):
    result = analyze_rules("short", min_length=4, max_length=10)
    assert result["checks"]["length"]["passed"] is True
