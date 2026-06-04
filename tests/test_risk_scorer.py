"""Risk scorer tests for password scoring module."""

from src.security.risk_scorer import HybridRiskScorer, calculate_hybrid_score


def test_score_strong_password():
    scorer = HybridRiskScorer()
    result = scorer.score("Str0ng!Pass123")

    assert result.final_score > 60
    assert result.security_level in ["Orta", "Güçlü", "Çok Güçlü"]
    assert result.password == "Str0ng!Pass123"


def test_score_weak_password():
    scorer = HybridRiskScorer()
    result = scorer.score("weak")

    assert result.final_score < 40
    assert result.security_level in ["Çok Zayıf", "Zayıf"]
    assert "Parola en az 8 karakter olmalı." in result.feedback


def test_score_with_lstm_increases_score():
    scorer = HybridRiskScorer(rule_weight=0.5, lstm_weight=0.5)
    no_lstm = scorer.score("WeakPass1!")
    with_lstm = scorer.score("WeakPass1!", lstm_score=90)

    assert with_lstm.final_score >= no_lstm.final_score
    assert with_lstm.lstm_score == 90


def test_calculate_hybrid_score_dict_output():
    output = calculate_hybrid_score("Test123!", lstm_score=75)

    assert isinstance(output, dict)
    assert output["password"] == "Test123!"
    assert output["lstm_score"] == 75
    assert output["final_score"] == output["final_score"]
    assert output["security_level"] in ["Çok Zayıf", "Zayıf", "Orta", "Güçlü", "Çok Güçlü"]


def test_calculate_rule_score_feedback_contains_missing_rules():
    scorer = HybridRiskScorer()
    score, feedback = scorer.calculate_rule_score("NoDigits!")

    assert score < 100
    assert "Rakam ekleyin." in feedback
