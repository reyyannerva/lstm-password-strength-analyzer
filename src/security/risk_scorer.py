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

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple
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
    feedback: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HybridRiskScorer:
    """
    Hybrid password scorer.

    The rule score evaluates visible password quality:
    - length
    - lowercase letters
    - uppercase letters
    - digits
    - special characters
    - character variety
    - weak patterns

    If an LSTM score is supplied, the final score combines rule score and LSTM score.
    """

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
        password = "" if password is None else str(password)

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

    def calculate_rule_score(self, password: str) -> Tuple[float, List[str]]:
        password = "" if password is None else str(password)

        if password == "":
            return 0.0, ["Parola boş olamaz."]

        score = 0.0
        feedback: List[str] = []
        length = len(password)

        # Length score: max 30
        if length >= 16:
            score += 30
        elif length >= 12:
            score += 25
        elif length >= 8:
            score += 18
        elif length >= 6:
            score += 8
            feedback.append("Parola en az 8 karakter olmalı.")
        else:
            score += 0
            feedback.append("Parola en az 8 karakter olmalı.")

        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[^a-zA-Z0-9]", password))

        # Character group score: max 50
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

        # Variety bonus: max 15
        if variety_count == 4:
            score += 15
        elif variety_count == 3:
            score += 8
        elif variety_count <= 1:
            score -= 10

        # Long and diverse password bonus
        if length >= 12 and variety_count >= 3:
            score += 8

        # Pattern penalties
        pattern_findings = self._safe_pattern_details(password)
        total_penalty = sum(int(item.get("penalty", 0)) for item in pattern_findings)

        # Do not over-penalize long and diverse passwords for small suffixes like "123".
        if self._is_strong_context(password):
            total_penalty = min(total_penalty, 12)
        elif length <= 8:
            total_penalty = min(total_penalty, 45)
        else:
            total_penalty = min(total_penalty, 30)

        score -= total_penalty

        for item in pattern_findings:
            message = item.get("message") or item.get("pattern")
            if message:
                feedback.append(str(message))

        score = self._clamp(score, 0, 100)

        if score >= 80 and not feedback:
            feedback.append("Parola güçlü görünüyor.")

        return score, feedback

    def get_security_level(self, score: float) -> str:
        score = self._clamp(score, 0, 100)

        if score < 20:
            return "Çok Zayıf"
        if score < 40:
            return "Zayıf"
        if score < 60:
            return "Orta"
        if score < 90:
            return "Güçlü"
        return "Çok Güçlü"

    def _safe_pattern_details(self, password: str) -> List[Dict[str, Any]]:
        """
        Normalizes detect_pattern_details output.

        Expected item format:
        {
            "pattern": "...",
            "message": "...",
            "severity": "low|medium|high",
            "penalty": 0-100
        }

        This method keeps the scorer stable even if patterns.py omits penalty.
        """

        try:
            raw_findings = detect_pattern_details(password)
        except Exception:
            return []

        normalized: List[Dict[str, Any]] = []

        for item in raw_findings or []:
            if isinstance(item, str):
                message = item
                severity = self._infer_severity(message)
                penalty = self._penalty_from_message(message, password)
                normalized.append(
                    {
                        "pattern": message,
                        "message": message,
                        "severity": severity,
                        "penalty": penalty,
                    }
                )
                continue

            if isinstance(item, dict):
                message = str(item.get("message") or item.get("pattern") or "")
                severity = str(item.get("severity") or self._infer_severity(message))
                penalty = item.get("penalty")

                if penalty is None:
                    penalty = self._penalty_from_message(message, password)

                normalized.append(
                    {
                        "pattern": str(item.get("pattern") or message),
                        "message": message,
                        "severity": severity,
                        "penalty": int(penalty),
                    }
                )

        return normalized

    def _penalty_from_message(self, message: str, password: str) -> int:
        message_lower = message.lower()
        password = "" if password is None else str(password)
        length = len(password)

        strong_context = self._is_strong_context(password)

        if "yalnızca" in message_lower:
            return 35

        if "yaygın kelime" in message_lower:
            return 30 if length <= 10 else 18

        if "klavye deseni" in message_lower:
            return 28 if length <= 10 else 14

        if "ardışık" in message_lower:
            if strong_context:
                return 8
            return 28 if length <= 8 else 14

        if "tekrarlı" in message_lower or "tekrar" in message_lower:
            return 18 if length <= 10 else 10

        if "yaygın yıl" in message_lower:
            return 8 if strong_context else 14

        return 10

    def _infer_severity(self, message: str) -> str:
        message_lower = message.lower()

        if (
            "yalnızca" in message_lower
            or "yaygın kelime" in message_lower
            or "klavye deseni" in message_lower
        ):
            return "high"

        if (
            "ardışık" in message_lower
            or "tekrarlı" in message_lower
            or "yaygın yıl" in message_lower
        ):
            return "medium"

        return "low"

    def _is_strong_context(self, password: str) -> bool:
        password = "" if password is None else str(password)

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