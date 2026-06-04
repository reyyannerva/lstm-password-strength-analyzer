"""
Hybrid rule tabanlı parola güvenlik skorlayıcısının testleri.
"""

import pytest

from src.security.risk_scorer import HybridRiskScorer


@pytest.fixture
def scorer():
    return HybridRiskScorer()


def test_calculate_rule_score_strong_password(scorer):
    score, feedback = scorer.calculate_rule_score("Str0ng!Passw0rd2026")
    assert score == 100.0
    assert feedback == []


def test_calculate_rule_score_weak_password(scorer):
    score, feedback = scorer.calculate_rule_score("123")
    assert score == 20.0
    assert "Parola en az 8 karakter olmalı." in feedback
    assert "Büyük harf ekleyin." in feedback
    assert "Küçük harf ekleyin." in feedback
    assert "Özel karakter ekleyin." in feedback


def test_calculate_rule_score_empty_password(scorer):
    score, feedback = scorer.calculate_rule_score("")
    assert score == 0.0
    assert feedback == ["Parola boş olamaz."]


@pytest.mark.parametrize(
    "score,expected_level",
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
