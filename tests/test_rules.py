"""
Security rule and hybrid risk scorer tests.

This test module validates:
- Rule-based password analysis functions from src.security.rules
- Hybrid risk scoring functions from src.security.risk_scorer
"""

import pytest

from src.security.rules import (
    analyze_rules,
    check_digits,
    check_length,
    check_lowercase,
    check_special_chars,
    check_uppercase,
)

from src.security.risk_scorer import (
    HybridRiskScorer,
    calculate_hybrid_score,
)


@pytest.fixture
def scorer():
    return HybridRiskScorer()


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


def test_calculate_rule_score_empty_password(scorer):
    score, feedback = scorer.calculate_rule_score("")

    assert score == 0.0
    assert feedback == ["Parola boş olamaz."]


def test_calculate_rule_score_very_weak_password(scorer):
    score, feedback = scorer.calculate_rule_score("123")

    assert score < 30
    assert "Parola en az 8 karakter olmalı." in feedback
    assert "Büyük harf ekleyin." in feedback
    assert "Küçük harf ekleyin." in feedback
    assert "Özel karakter ekleyin." in feedback


def test_calculate_rule_score_short_letters_only_password(scorer):
    score, feedback = scorer.calculate_rule_score("weak")

    assert score <= 20
    assert "Parola en az 8 karakter olmalı." in feedback
    assert "Büyük harf ekleyin." in feedback
    assert "Rakam ekleyin." in feedback
    assert "Özel karakter ekleyin." in feedback
    assert any("yalnızca harflerden" in item for item in feedback)


def test_calculate_rule_score_password123_is_penalized(scorer):
    score, feedback = scorer.calculate_rule_score("password123")

    assert score < 40
    assert "Büyük harf ekleyin." in feedback
    assert "Özel karakter ekleyin." in feedback
    assert any("Yaygın parola kelimesi" in item for item in feedback)
    assert any("ardışık" in item for item in feedback)


def test_calculate_rule_score_password123_with_capital_is_not_strong(scorer):
    score, feedback = scorer.calculate_rule_score("Password123")

    assert 20 <= score < 60
    assert "Özel karakter ekleyin." in feedback
    assert any("Yaygın parola kelimesi" in item for item in feedback)


def test_calculate_rule_score_strong_password_with_short_sequence(scorer):
    score, feedback = scorer.calculate_rule_score("Str0ng!Pass123")

    assert score >= 75
    assert any("Kısa bir ardışık karakter deseni" in item for item in feedback)


def test_calculate_rule_score_generated_style_password(scorer):
    score, feedback = scorer.calculate_rule_score("A9!xK2#mQ7")

    assert score >= 80
    assert feedback == ["Parola güçlü görünüyor."]


@pytest.mark.parametrize(
    "score, expected_level",
    [
        (0, "Çok Zayıf"),
        (19.99, "Çok Zayıf"),
        (20, "Zayıf"),
        (39.99, "Zayıf"),
        (40, "Orta"),
        (59.99, "Orta"),
        (60, "Güçlü"),
        (79.99, "Güçlü"),
        (80, "Çok Güçlü"),
        (100, "Çok Güçlü"),
    ],
)
def test_get_security_level_boundaries(scorer, score, expected_level):
    assert scorer.get_security_level(score) == expected_level


def test_calculate_hybrid_score_returns_dict():
    result = calculate_hybrid_score("Test1234!", lstm_score=80)

    assert isinstance(result, dict)
    assert result["password"] == "Test1234!"
    assert result["lstm_score"] == 80.0
    assert "rule_score" in result
    assert "final_score" in result
    assert "security_level" in result
    assert "feedback" in result
    assert 0 <= result["final_score"] <= 100


def test_calculate_hybrid_score_without_lstm_score():
    result = calculate_hybrid_score("Test1234!")

    assert isinstance(result, dict)
    assert result["password"] == "Test1234!"
    assert result["lstm_score"] is None
    assert "final_score" in result
    assert 0 <= result["final_score"] <= 100


def test_lstm_score_can_increase_final_score(scorer):
    weighted_scorer = HybridRiskScorer(rule_weight=0.5, lstm_weight=0.5)

    without_lstm = weighted_scorer.score("WeakPass1!")
    with_lstm = weighted_scorer.score("WeakPass1!", lstm_score=90)

    assert with_lstm.lstm_score == 90.0
    assert with_lstm.final_score >= without_lstm.final_score


def test_lstm_score_is_clamped_above_100():
    result = calculate_hybrid_score(
        "Str0ngPa!",
        lstm_score=200,
        rule_weight=0.5,
        lstm_weight=0.5,
    )

    assert result["lstm_score"] == 100.0
    assert result["final_score"] <= 100


def test_lstm_score_is_clamped_below_zero():
    result = calculate_hybrid_score(
        "Str0ngPa!",
        lstm_score=-50,
        rule_weight=0.5,
        lstm_weight=0.5,
    )

    assert result["lstm_score"] == 0


def test_invalid_weight_initialization_raises():
    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=-1, lstm_weight=0.5)

    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=0, lstm_weight=0)