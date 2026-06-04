"""
Hybrid password risk scoring module.

This module combines:
- Rule-based password analysis
- Optional LSTM-based predictability score

Final score range:
0   -> very risky / very weak
100 -> very safe / very strong
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import re


@dataclass
class RiskScoreResult:
    password: str
    rule_score: float
    lstm_score: Optional[float]
    final_score: float
    security_level: str
    feedback: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HybridRiskScorer:
    """
    Hybrid password security scorer.

    Args:
        rule_weight: Weight of rule-based score.
        lstm_weight: Weight of LSTM-based score.
    """

    def __init__(self, rule_weight: float = 0.6, lstm_weight: float = 0.4) -> None:
        if rule_weight < 0 or lstm_weight < 0:
            raise ValueError("Weights cannot be negative.")

        total_weight = rule_weight + lstm_weight
        if total_weight == 0:
            raise ValueError("At least one weight must be greater than zero.")

        self.rule_weight = rule_weight / total_weight
        self.lstm_weight = lstm_weight / total_weight

    def score(
        self,
        password: str,
        lstm_score: Optional[float] = None,
    ) -> RiskScoreResult:
        """
        Calculate final hybrid password security score.

        Args:
            password: Password text to analyze.
            lstm_score: Optional LSTM security score between 0 and 100.
                        Higher means safer, lower means more predictable.

        Returns:
            RiskScoreResult object.
        """

        if password is None:
            password = ""

        password = str(password)

        rule_score, feedback = self.calculate_rule_score(password)

        normalized_lstm_score = None
        if lstm_score is not None:
            normalized_lstm_score = self._clamp(float(lstm_score), 0, 100)

        if normalized_lstm_score is None:
            final_score = rule_score
        else:
            final_score = (
                self.rule_weight * rule_score
                + self.lstm_weight * normalized_lstm_score
            )

        final_score = round(self._clamp(final_score, 0, 100), 2)
        security_level = self.get_security_level(final_score)

        return RiskScoreResult(
            password=password,
            rule_score=round(rule_score, 2),
            lstm_score=normalized_lstm_score,
            final_score=final_score,
            security_level=security_level,
            feedback=feedback,
        )

    def calculate_rule_score(self, password: str) -> tuple[float, list[str]]:
        """
        Calculate rule-based password score between 0 and 100.
        """

        score = 0.0
        feedback = []

        length = len(password)

        if length == 0:
            return 0.0, ["Parola boş olamaz."]

        if length >= 8:
            score += 15
        else:
            feedback.append("Parola en az 8 karakter olmalı.")

        if length >= 12:
            score += 15
        else:
            feedback.append("Daha güçlü bir parola için en az 12 karakter önerilir.")

        if length >= 16:
            score += 10

        if re.search(r"[a-z]", password):
            score += 10
        else:
            feedback.append("Küçük harf ekleyin.")

        if re.search(r"[A-Z]", password):
            score += 10
        else:
            feedback.append("Büyük harf ekleyin.")

        if re.search(r"\d", password):
            score += 10
        else:
            feedback.append("Rakam ekleyin.")

        if re.search(r"[^a-zA-Z0-9]", password):
            score += 15
        else:
            feedback.append("Özel karakter ekleyin.")

        if not self._has_repeated_chars(password):
            score += 10
        else:
            feedback.append("Tekrarlayan karakterleri azaltın.")

        if not self._has_common_pattern(password):
            score += 15
        else:
            feedback.append("123, abc, qwerty gibi tahmin edilebilir desenlerden kaçının.")

        return self._clamp(score, 0, 100), feedback

    def get_security_level(self, score: float) -> str:
        """
        Convert numeric score to Turkish security level.
        """

        score = self._clamp(score, 0, 100)

        if score < 20:
            return "Çok Zayıf"
        if score < 40:
            return "Zayıf"
        if score < 60:
            return "Orta"
        if score < 80:
            return "Güçlü"
        return "Çok Güçlü"

    def _has_repeated_chars(self, password: str) -> bool:
        return bool(re.search(r"(.)\1{2,}", password))

    def _has_common_pattern(self, password: str) -> bool:
        lowered = password.lower()

        common_patterns = [
            "123",
            "1234",
            "12345",
            "abc",
            "abcd",
            "qwerty",
            "password",
            "admin",
            "letmein",
            "111",
            "000",
        ]

        return any(pattern in lowered for pattern in common_patterns)

    def _clamp(self, value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(value, maximum))


def calculate_hybrid_score(
    password: str,
    lstm_score: Optional[float] = None,
    rule_weight: float = 0.6,
    lstm_weight: float = 0.4,
) -> Dict[str, Any]:
    """
    API-friendly helper function.

    Returns a dictionary that can be directly used in API responses.
    """

    scorer = HybridRiskScorer(
        rule_weight=rule_weight,
        lstm_weight=lstm_weight,
    )

    return scorer.score(
        password=password,
        lstm_score=lstm_score,
    ).to_dict()