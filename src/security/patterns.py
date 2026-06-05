"""
Weak password pattern detection module.

This module detects predictable password patterns such as:
- repeated characters
- sequential characters
- keyboard patterns
- common years
- common weak words
- digit-only passwords
- letter-only passwords

Public API:
- detect_patterns(password) -> list[str]
- detect_pattern_details(password) -> list[dict]

The string outputs are intentionally Turkish because tests, API feedback,
and frontend messages rely on these phrases.
"""

import re
from typing import Any, Dict, List, Optional


KEYBOARD_ROWS = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1234567890",
]

COMMON_WORDS = [
    "password",
    "parola",
    "admin",
    "qwerty",
    "login",
    "welcome",
    "letmein",
    "iloveyou",
    "root",
]

COMMON_YEARS_PATTERN = re.compile(r"(19|20)\d{2}")
REPEATED_CHARS_PATTERN = re.compile(r"(.)\1{2,}")


def _safe_password(password: Optional[str]) -> str:
    if password is None:
        return ""
    return str(password)


def _is_strong_context(password: str) -> bool:
    return (
        len(password) >= 10
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^a-zA-Z0-9]", password))
    )


def detect_repeated_chars(password: Optional[str]) -> Optional[str]:
    password = _safe_password(password)

    if REPEATED_CHARS_PATTERN.search(password):
        return "tekrarlı karakter tespit edildi"

    return None


def detect_sequential_chars(password: Optional[str]) -> Optional[str]:
    password = _safe_password(password).lower()

    for i in range(len(password) - 2):
        trio = password[i:i + 3]

        if not trio.isalnum():
            continue

        if (
            ord(trio[1]) - ord(trio[0]) == 1
            and ord(trio[2]) - ord(trio[1]) == 1
        ):
            return "ardışık karakter tespit edildi"

        if (
            ord(trio[0]) - ord(trio[1]) == 1
            and ord(trio[1]) - ord(trio[2]) == 1
        ):
            return "ardışık karakter tespit edildi"

    return None


def detect_keyboard_pattern(password: Optional[str]) -> Optional[str]:
    password = _safe_password(password).lower()

    for row in KEYBOARD_ROWS:
        for size in range(4, 2, -1):
            for i in range(len(row) - size + 1):
                chunk = row[i:i + size]
                reverse_chunk = chunk[::-1]

                if chunk in password or reverse_chunk in password:
                    return "klavye deseni tespit edildi"

    return None


def detect_common_year(password: Optional[str]) -> Optional[str]:
    password = _safe_password(password)

    if COMMON_YEARS_PATTERN.search(password):
        return "yaygın yıl tespit edildi"

    return None


def detect_common_word(password: Optional[str]) -> Optional[str]:
    password = _safe_password(password).lower()

    for word in COMMON_WORDS:
        if word in password:
            return "yaygın kelime tespit edildi"

    return None


def detect_only_digits(password: Optional[str]) -> Optional[str]:
    password = _safe_password(password)

    if password and password.isdigit():
        return "yalnızca rakamlardan oluşuyor"

    return None


def detect_only_letters(password: Optional[str]) -> Optional[str]:
    password = _safe_password(password)

    if password and password.isalpha():
        return "yalnızca harflerden oluşuyor"

    return None


_DETECTORS = [
    detect_repeated_chars,
    detect_sequential_chars,
    detect_keyboard_pattern,
    detect_common_year,
    detect_common_word,
    detect_only_digits,
    detect_only_letters,
]


def detect_patterns(password: Optional[str]) -> List[str]:
    password = _safe_password(password)
    found: List[str] = []

    for detector in _DETECTORS:
        result = detector(password)
        if result and result not in found:
            found.append(result)

    return found


def _severity_for_pattern(pattern: str) -> str:
    pattern = pattern.lower()

    if (
        "yalnızca" in pattern
        or "yaygın kelime" in pattern
        or "klavye deseni" in pattern
    ):
        return "high"

    if (
        "ardışık" in pattern
        or "tekrarlı" in pattern
        or "yaygın yıl" in pattern
    ):
        return "medium"

    return "low"


def _penalty_for_pattern(pattern: str, password: str) -> int:
    pattern_lower = pattern.lower()
    length = len(password)
    strong_context = _is_strong_context(password)

    if "yalnızca rakamlardan" in pattern_lower:
        return 45 if length <= 8 else 30

    if "yalnızca harflerden" in pattern_lower:
        return 35 if length <= 10 else 25

    if "yaygın kelime" in pattern_lower:
        return 35 if length <= 10 else 18

    if "klavye deseni" in pattern_lower:
        return 35 if length <= 10 else 18

    if "ardışık" in pattern_lower:
        if strong_context:
            return 8
        return 30 if length <= 8 else 14

    if "tekrarlı" in pattern_lower:
        return 20 if length <= 10 else 10

    if "yaygın yıl" in pattern_lower:
        return 8 if strong_context else 14

    return 10


def detect_pattern_details(password: Optional[str]) -> List[Dict[str, Any]]:
    password = _safe_password(password)
    details: List[Dict[str, Any]] = []

    for pattern in detect_patterns(password):
        details.append(
            {
                "pattern": pattern,
                "message": pattern,
                "severity": _severity_for_pattern(pattern),
                "penalty": _penalty_for_pattern(pattern, password),
            }
        )

    return details