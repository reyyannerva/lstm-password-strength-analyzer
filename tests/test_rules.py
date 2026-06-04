"""
Security rule and hybrid risk scorer tests.

This test module validates:
- Rule-based password analysis functions from src.security.rules
- Hybrid risk scoring functions from src.security.risk_scorer
"""

import pytest

from src.security.rules import (
    check_length,
    check_uppercase,
    check_lowercase,
    check_digits,
    check_special_chars,
    analyze_rules,
)

from src.security.risk_scorer import (
    HybridRiskScorer,
    calculate_hybrid_score,
)


def test_check_length_valid():
    result = check_length("Password123!", min_length=8, max_length=128)

    assert result["passed"] is True
    assert "details" in result
    assert result["current_length"] == 12


def test_check_length_too_short():
    result = check_length("short", min_length=8, max_length=128)

    assert result["passed"] is False
    assert "details" in result
    assert result["current_length"] == 5


def test_check_length_too_long():
    result = check_length("a" * 200, min_length=8, max_length=128)

    assert result["passed"] is False
    assert "details" in result
    assert result["current_length"] == 200


def test_check_uppercase_present():
    result = check_uppercase("Password")

    assert result["passed"] is True
    assert result["count"] >= 1
    assert "details" in result


def test_check_uppercase_absent():
    result = check_uppercase("password")

    assert result["passed"] is False
    assert result["count"] == 0
    assert "details" in result


def test_check_lowercase_present():
    result = check_lowercase("PASSWORDa")

    assert result["passed"] is True
    assert result["count"] >= 1
    assert "details" in result


def test_check_lowercase_absent():
    result = check_lowercase("PASSWORD")

    assert result["passed"] is False
    assert result["count"] == 0
    assert "details" in result


def test_check_digits_present():
    result = check_digits("Password123")

    assert result["passed"] is True
    assert result["count"] >= 1
    assert "details" in result


def test_check_digits_absent():
    result = check_digits("PasswordABC")

    assert result["passed"] is False
    assert result["count"] == 0
    assert "details" in result


def test_check_special_chars_present():
    result = check_special_chars("Password123!")

    assert result["passed"] is True
    assert result["count"] >= 1
    assert "details" in result


def test_check_special_chars_absent():
    result = check_special_chars("Password123")

    assert result["passed"] is False
    assert result["count"] == 0
    assert "details" in result


def test_analyze_rules_strong_password():
    result = analyze_rules("SecurePass123!")

    assert result["password"] == "SecurePass123!"
    assert "checks" in result
    assert "passed_count" in result
    assert "total_checks" in result
    assert "score" in result
    assert "security_level" in result
    assert "details" in result
    assert "recommendations" in result
    assert result["score"] > 60


def test_analyze_rules_weak_password():
    result = analyze_rules("weak")

    assert result["password"] == "weak"
    assert result["passed_count"] < result["total_checks"]
    assert result["score"] < 100
    assert result["all_passed"] is False


def test_analyze_rules_empty_password():
    result = analyze_rules("")

    assert result["password"] == ""
    assert result["passed_count"] == 0
    assert result["score"] == 0


def test_analyze_rules_none_password():
    result = analyze_rules(None)

    assert result["password"] == ""
    assert result["passed_count"] == 0


def test_analyze_rules_numeric_password():
    result = analyze_rules("12345678")

    assert result["checks"]["digits"]["passed"] is True
    assert result["checks"]["uppercase"]["passed"] is False
    assert result["checks"]["lowercase"]["passed"] is False
    assert result["checks"]["special_chars"]["passed"] is False
    assert result["all_passed"] is False


def test_analyze_rules_custom_length_requirements():
    result = analyze_rules("short", min_length=4, max_length=10)

    assert result["checks"]["length"]["passed"] is True


def test_analyze_rules_contains_extended_checks():
    result = analyze_rules("P@ssw0rd")

    expected_checks = {
        "length",
        "uppercase",
        "lowercase",
        "digits",
        "special_chars",
        "repeated_characters",
        "sequential_patterns",
        "common_words",
        "character_diversity",
        "only_letters_or_digits",
    }

    assert set(result["checks"].keys()) == expected_checks


def test_calculate_rule_score_strong_password():
    scorer = HybridRiskScorer()
    score, feedback = scorer.calculate_rule_score("Str0ng!Pass123")

    assert score > 60
    assert isinstance(feedback, list)
    assert all(isinstance(item, str) for item in feedback)


def test_calculate_rule_score_weak_password():
    scorer = HybridRiskScorer()
    score, feedback = scorer.calculate_rule_score("weak")

    assert score < 40
    assert "Parola en az 8 karakter olmalı." in feedback
    assert "Büyük harf ekleyin." in feedback
    assert "Özel karakter ekleyin." in feedback


def test_get_security_level_thresholds():
    scorer = HybridRiskScorer()

    assert scorer.get_security_level(10) == "Çok Zayıf"
    assert scorer.get_security_level(30) == "Zayıf"
    assert scorer.get_security_level(50) == "Orta"
    assert scorer.get_security_level(70) == "Güçlü"
    assert scorer.get_security_level(95) == "Çok Güçlü"


def test_calculate_hybrid_score_returns_dict():
    result = calculate_hybrid_score("Test1234!", lstm_score=80)

    assert isinstance(result, dict)
    assert result["password"] == "Test1234!"
    assert result["lstm_score"] == 80
    assert "final_score" in result
    assert "security_level" in result
    assert "feedback" in result


def test_calculate_hybrid_score_without_lstm_score():
    result = calculate_hybrid_score("Test1234!")

    assert isinstance(result, dict)
    assert result["password"] == "Test1234!"
    assert result["lstm_score"] is None
    assert "final_score" in result
    assert 0 <= result["final_score"] <= 100


def test_invalid_weight_initialization_raises():
    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=-1, lstm_weight=0.5)

    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=0, lstm_weight=0)