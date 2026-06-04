"""Rule-based security tests."""

from src.security.risk_scorer import HybridRiskScorer, calculate_hybrid_score


def test_calculate_rule_score_strong_password():
    scorer = HybridRiskScorer()
    score, feedback = scorer.calculate_rule_score("Str0ng!Pass123")

    assert score > 60
    assert feedback == [] or all(isinstance(item, str) for item in feedback)


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


def test_invalid_weight_initialization_raises():
    try:
        HybridRiskScorer(rule_weight=-1, lstm_weight=0.5)
        assert False, "Negative rule_weight should raise ValueError"
    except ValueError:
        pass

    try:
        HybridRiskScorer(rule_weight=0, lstm_weight=0)
        assert False, "Zero total weight should raise ValueError"
    except ValueError:
        pass
