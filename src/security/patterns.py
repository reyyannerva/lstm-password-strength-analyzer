"""
Weak password pattern detection module.

This module detects risky but context-aware password patterns.
It is intentionally calibrated so that a strong password containing
a small pattern such as "123" is penalized mildly, not completely rejected.
"""

import re
from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class PatternFinding:
    code: str
    message: str
    severity: str
    penalty: int

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


COMMON_WORDS = [
    "password", "parola", "qwerty", "letmein", "welcome",
    "admin", "login", "iloveyou", "monkey", "dragon",
    "master", "sunshine", "princess",
]
COMMON_NAMES = [
    "ahmet", "mehmet", "ali", "ayse", "ayşe", "fatma",
    "john", "michael", "mike", "admin",
]
COMMON_YEARS = [str(year) for year in range(1950, 2031)]

KEYBOARD_PATTERNS = [
    "qwerty", "asdf", "zxcv", "qaz", "wsx", "123456",
    "abcdef", "abcd",
]


def _is_embedded_in_strong_password(password: str) -> bool:
    return (
        len(password) >= 10
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^a-zA-Z0-9]", password))
    )


def detect_repeated_chars(password: str) -> PatternFinding | None:
    if re.search(r"(.)\1{2,}", password):
        return PatternFinding(
            code="repeated_chars",
            message="Tekrarlayan karakterler içeriyor.",
            severity="medium",
            penalty=10,
        )
    return None


def detect_sequential_chars(password: str) -> PatternFinding | None:
    lowered = password.lower()

    if len(password) <= 6 and re.fullmatch(r"(123456|12345|1234|123|abcdef|abcd|abc)", lowered):
        return PatternFinding(
            code="simple_sequence",
            message="Parola büyük ölçüde ardışık karakterlerden oluşuyor.",
            severity="high",
            penalty=35,
        )

    for i in range(len(lowered) - 2):
        trio = lowered[i:i + 3]
        if len(set(trio)) == 3:
            if (
                ord(trio[1]) - ord(trio[0]) == 1
                and ord(trio[2]) - ord(trio[1]) == 1
            ):
                return PatternFinding(
                    code="embedded_sequence",
                    message="Kısa bir ardışık karakter deseni içeriyor.",
                    severity="low" if _is_embedded_in_strong_password(password) else "medium",
                    penalty=5 if _is_embedded_in_strong_password(password) else 12,
                )

    return None


def detect_keyboard_pattern(password: str) -> PatternFinding | None:
    lowered = password.lower()

    for pattern in KEYBOARD_PATTERNS:
        if pattern in lowered:
            if lowered == pattern or len(password) <= len(pattern) + 2:
                return PatternFinding(
                    code="keyboard_pattern",
                    message=f"Klavye deseni içeriyor: {pattern}",
                    severity="high",
                    penalty=30,
                )

            return PatternFinding(
                code="embedded_keyboard_pattern",
                message=f"Klavye deseni içeriyor: {pattern}",
                severity="medium",
                penalty=12,
            )

    return None


def detect_common_year(password: str) -> PatternFinding | None:
    for year in COMMON_YEARS:
        if year in password:
            return PatternFinding(
                code="common_year",
                message=f"Yaygın yıl ifadesi içeriyor: {year}",
                severity="low",
                penalty=5,
            )
    return None
def detect_date_pattern(password: str) -> PatternFinding | None:
    if re.search(r"(?<!\d)\d{8}(?!\d)", password):
        return PatternFinding(
            code="date_pattern",
            message="Tarih benzeri sayı deseni içeriyor.",
            severity="medium",
            penalty=18,
        )
    return None


def detect_phone_pattern(password: str) -> PatternFinding | None:
    if re.search(r"(?<!\d)5\d{9}(?!\d)", password):
        return PatternFinding(
            code="phone_pattern",
            message="Telefon numarası benzeri yapı içeriyor.",
            severity="medium",
            penalty=20,
        )
    return None

def detect_common_name(password: str) -> PatternFinding | None:
    lowered = password.lower()

    for name in COMMON_NAMES:
        if name in lowered:
            return PatternFinding(
                code="common_name",
                message=f"Yaygın isim içeriyor: {name}",
                severity="medium",
                penalty=15,
            )

    return None

def detect_common_word(password: str) -> PatternFinding | None:
    lowered = password.lower()

    for word in COMMON_WORDS:
        if word in lowered:
            if lowered == word or lowered in {f"{word}123", f"{word}1234", f"{word}!"}:
                return PatternFinding(
                    code="common_word",
                    message=f"Yaygın parola kelimesi içeriyor: {word}",
                    severity="high",
                    penalty=35,
                )

            return PatternFinding(
                code="embedded_common_word",
                message=f"Yaygın kelime içeriyor: {word}",
                severity="medium",
                penalty=15,
            )

    return None


def detect_only_digits(password: str) -> PatternFinding | None:
    if password.isdigit():
        return PatternFinding(
            code="only_digits",
            message="Parola yalnızca rakamlardan oluşuyor.",
            severity="high",
            penalty=35,
        )
    return None


def detect_only_letters(password: str) -> PatternFinding | None:
    if password.isalpha():
        return PatternFinding(
            code="only_letters",
            message="Parola yalnızca harflerden oluşuyor.",
            severity="medium",
            penalty=18,
        )
    return None


_DETECTORS = [
    detect_only_digits,
    detect_only_letters,
    detect_common_word,
    detect_common_name,
    detect_keyboard_pattern,
    detect_sequential_chars,
    detect_repeated_chars,
    detect_common_year,
    detect_date_pattern,
    detect_phone_pattern,
]


def detect_pattern_details(password: str) -> List[Dict[str, object]]:
    findings = []

    if password is None:
        password = ""

    password = str(password)

    for detector in _DETECTORS:
        result = detector(password)
        if result:
            findings.append(result.to_dict())

    return findings


def detect_patterns(password: str) -> List[str]:
    """
    Backward-compatible helper.
    Returns only pattern messages.
    """
    return [item["message"] for item in detect_pattern_details(password)]