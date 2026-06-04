"""Comprehensive tests for hybrid password risk scoring module."""

import pytest

from src.security.risk_scorer import HybridRiskScorer, calculate_hybrid_score


VALID_LEVELS = ["Çok Zayıf", "Zayıf", "Orta", "Güçlü", "Çok Güçlü"]


def test_empty_password_returns_zero_and_very_weak():
    result = calculate_hybrid_score("")

    assert result["password"] == ""
    assert result["rule_score"] == 0.0
    assert result["final_score"] == 0
    assert result["security_level"] == "Çok Zayıf"
    assert "Parola boş olamaz." in result["feedback"]


def test_very_short_letters_only_password_is_very_weak():
    result = calculate_hybrid_score("weak")

    assert result["final_score"] <= 20
    assert result["security_level"] in ["Çok Zayıf", "Zayıf"]
    assert "Parola en az 8 karakter olmalı." in result["feedback"]
    assert any("yalnızca harflerden" in item for item in result["feedback"])


def test_digits_only_sequence_is_very_weak():
    result = calculate_hybrid_score("123456")

    assert result["final_score"] <= 20
    assert result["security_level"] == "Çok Zayıf"
    assert any("yalnızca rakamlardan" in item for item in result["feedback"])
    assert any("Klavye deseni" in item for item in result["feedback"])
    assert any("ardışık" in item for item in result["feedback"])


def test_common_password_word_with_sequence_is_penalized_heavily():
    result = calculate_hybrid_score("password123")

    assert result["final_score"] < 40
    assert result["security_level"] in ["Çok Zayıf", "Zayıf"]
    assert any("Yaygın parola kelimesi" in item for item in result["feedback"])
    assert any("ardışık" in item for item in result["feedback"])


def test_password123_with_capital_letter_is_still_not_strong():
    result = calculate_hybrid_score("Password123")

    assert 20 <= result["final_score"] < 60
    assert result["security_level"] in ["Zayıf", "Orta"]
    assert "Özel karakter ekleyin." in result["feedback"]
    assert any("Yaygın parola kelimesi" in item for item in result["feedback"])


def test_strong_password_with_small_123_suffix_is_not_over_penalized():
    result = calculate_hybrid_score("Str0ng!Pass123")

    assert result["final_score"] >= 75
    assert result["security_level"] in ["Güçlü", "Çok Güçlü"]
    assert any("Kısa bir ardışık karakter deseni" in item for item in result["feedback"])


def test_generated_style_password_is_very_strong():
    result = calculate_hybrid_score("A9!xK2#mQ7")

    assert result["final_score"] >= 80
    assert result["security_level"] == "Çok Güçlü"
    assert result["feedback"] == ["Parola güçlü görünüyor."]


def test_score_method_returns_dataclass_result():
    scorer = HybridRiskScorer()
    result = scorer.score("Str0ng!Pass123")

    assert result.password == "Str0ng!Pass123"
    assert result.final_score >= 75
    assert result.security_level in ["Güçlü", "Çok Güçlü"]
    assert isinstance(result.feedback, list)


def test_calculate_hybrid_score_returns_api_friendly_dict():
    output = calculate_hybrid_score("Test123!", lstm_score=75)

    assert isinstance(output, dict)
    assert output["password"] == "Test123!"
    assert output["lstm_score"] == 75.0
    assert output["security_level"] in VALID_LEVELS
    assert 0 <= output["rule_score"] <= 100
    assert 0 <= output["final_score"] <= 100
    assert isinstance(output["feedback"], list)


def test_lstm_score_is_used_when_provided():
    scorer = HybridRiskScorer(rule_weight=0.5, lstm_weight=0.5)

    without_lstm = scorer.score("WeakPass1!")
    with_lstm = scorer.score("WeakPass1!", lstm_score=90)

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


def test_custom_weights_are_normalized_and_supported():
    result = calculate_hybrid_score(
        "Str0ng!Pass123",
        lstm_score=60,
        rule_weight=7,
        lstm_weight=3,
    )

    assert result["lstm_score"] == 60.0
    assert 0 <= result["final_score"] <= 100
    assert result["security_level"] in VALID_LEVELS


def test_negative_rule_weight_raises_value_error():
    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=-0.1, lstm_weight=0.5)


def test_negative_lstm_weight_raises_value_error():
    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=0.5, lstm_weight=-0.1)


def test_zero_total_weights_raise_value_error():
    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=0.0, lstm_weight=0.0)


def test_rule_score_feedback_contains_missing_digit_message():
    scorer = HybridRiskScorer()
    score, feedback = scorer.calculate_rule_score("NoDigits!")

    assert score < 100
    assert "Rakam ekleyin." in feedback


def test_rule_score_feedback_contains_missing_special_character_message():
    scorer = HybridRiskScorer()
    score, feedback = scorer.calculate_rule_score("NoSpecial123")

    assert score < 100
    assert "Özel karakter ekleyin." in feedback


def test_security_level_boundaries():
    scorer = HybridRiskScorer()

    assert scorer.get_security_level(0) == "Çok Zayıf"
    assert scorer.get_security_level(19.99) == "Çok Zayıf"
    assert scorer.get_security_level(20) == "Zayıf"
    assert scorer.get_security_level(39.99) == "Zayıf"
    assert scorer.get_security_level(40) == "Orta"
    assert scorer.get_security_level(59.99) == "Orta"
    assert scorer.get_security_level(60) == "Güçlü"
    assert scorer.get_security_level(79.99) == "Güçlü"
    assert scorer.get_security_level(80) == "Çok Güçlü"
    assert scorer.get_security_level(100) == "Çok Güçlü"