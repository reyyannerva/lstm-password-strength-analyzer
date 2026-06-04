"""
Hybrid risk skorlayıcısının testleri.
"""

import pytest

from src.security.risk_scorer import HybridRiskScorer, calculate_hybrid_score


def test_score_returns_dict_with_expected_fields():
    result = calculate_hybrid_score("Str0ng!Passw0rd2026")
    assert result["password"] == "Str0ng!Passw0rd2026"
    assert result["rule_score"] == 100.0
    assert result["final_score"] == 100.0
    assert result["security_level"] == "Çok Güçlü"
    assert result["feedback"] == []


def test_score_uses_lstm_score_when_provided():
    result = calculate_hybrid_score("Str0ngPa!", lstm_score=20, rule_weight=0.5, lstm_weight=0.5)
    assert result["lstm_score"] == 20.0
    assert result["final_score"] == 52.5
    assert result["security_level"] == "Orta"


def test_score_clamps_lstm_score_above_100():
    result = calculate_hybrid_score("Str0ngPa!", lstm_score=200, rule_weight=0.5, lstm_weight=0.5)
    assert result["lstm_score"] == 100.0
    assert result["final_score"] == 92.5


def test_negative_weights_raise_value_error():
    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=-0.1)


def test_zero_total_weights_raise_value_error():
    with pytest.raises(ValueError):
        HybridRiskScorer(rule_weight=0.0, lstm_weight=0.0)
