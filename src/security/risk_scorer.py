"""
Hybrid password risk scoring module.

Combines:
- Rule-based password quality analysis
- Pattern-based penalties
- Optional LSTM score

Score range:
0   -> very weak
100 -> very strong
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import re

try:
    from src.security.patterns import detect_pattern_details
except ImportError:
    from patterns import detect_pattern_details


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
    def __init__(self, rule_weight: float = 0.7, lstm_weight: float = 0.3) -> None:
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

        return RiskScoreResult(
            password=password,
            rule_score=round(rule_score, 2),
            lstm_score=normalized_lstm_score,
            final_score=final_score,
            security_level=self.get_security_level(final_score),
            feedback=feedback,
        )

    def calculate_rule_score(self, password: str) -> tuple[float, list[str]]:
        if not password:
            return 0.0, ["Parola boş olamaz."]

        score = 0.0
        feedback = []
        length = len(password)

        if length >= 16:
            score += 30
        elif length >= 12:
            score += 25
        elif length >= 8:
            score += 18
        elif length >= 6:
            score += 8
        else:
            feedback.append("Parola en az 8 karakter olmalı.")

        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[^a-zA-Z0-9]", password))

        if has_lower:
            score += 12
        else:
            feedback.append("Küçük harf ekleyin.")

        if has_upper:
            score += 12
        else:
            feedback.append("Büyük harf ekleyin.")

        if has_digit:
            score += 12
        else:
            feedback.append("Rakam ekleyin.")

        if has_special:
            score += 14
        else:
            feedback.append("Özel karakter ekleyin.")

        variety_count = sum([has_lower, has_upper, has_digit, has_special])
        if variety_count == 4:
            score += 15
        elif variety_count == 3:
            score += 8
        elif variety_count <= 1:
            score -= 10

        if length >= 12 and variety_count >= 3:
            score += 8

        pattern_findings = detect_pattern_details(password)
        total_penalty = sum(int(item["penalty"]) for item in pattern_findings)

        if self._is_strong_context(password):
            total_penalty = min(total_penalty, 12)
        elif length <= 8:
            total_penalty = min(total_penalty, 45)
        else:
            total_penalty = min(total_penalty, 30)

        score -= total_penalty

        for item in pattern_findings:
            feedback.append(str(item["message"]))

        if score >= 80 and not feedback:
            feedback.append("Parola güçlü görünüyor.")

        return self._clamp(score, 0, 100), feedback

    def get_security_level(self, score: float) -> str:
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

    def _is_strong_context(self, password: str) -> bool:
        return (
            len(password) >= 10
            and bool(re.search(r"[a-z]", password))
            and bool(re.search(r"[A-Z]", password))
            and bool(re.search(r"\d", password))
            and bool(re.search(r"[^a-zA-Z0-9]", password))
        )

    def _clamp(self, value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(value, maximum))


def calculate_hybrid_score(
    password: str,
    lstm_score: Optional[float] = None,
    rule_weight: float = 0.7,
    lstm_weight: float = 0.3,
) -> Dict[str, Any]:
    scorer = HybridRiskScorer(
        rule_weight=rule_weight,
        lstm_weight=lstm_weight,
    )

    return scorer.score(
        password=password,
        lstm_score=lstm_score,
    ).to_dict()