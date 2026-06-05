"""
Weak password pattern detection module.

This module detects predictable password patterns such as:
- repeated characters
- sequential characters
- keyboard patterns
- common years
- common weak words
- common names
- date-like numeric patterns
- phone-like numeric patterns
- digit-only passwords
- letter-only passwords

Public API:
- detect_patterns(password) -> list[str]
- detect_pattern_details(password) -> list[dict]

The string outputs are intentionally Turkish because tests, API feedback,
risk scoring, and frontend messages rely on these phrases.
"""

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PatternFinding:
    code: str
    message: str
    severity: str
    penalty: int

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["pattern"] = self.message
        return data


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

COMMON_NAMES = [
    "ahmet",
    "mehmet",
    "ali",
    "ayse",
    "ayşe",
    "fatma",
    "john",
    "michael",
    "mike",
]

COMMON_YEARS = [str(year) for year in range(1950, 2031)]

COMMON_YEARS_PATTERN = re.compile(r"(19|20)\d{2}")
REPEATED_CHARS_PATTERN = re.compile(r"(.)\1{2,}")


def _safe_password(password: Optional[str]) -> str:
    if password is None:
        return ""
    return str(password)


def _is_strong_context(password: str) -> bool:
    password = _safe_password(password)

    return (
        len(password) >= 10
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^a-zA-Z0-9]", password))
    )


def _is_short_or_simple(password: str) -> bool:
    password = _safe_password(password)

    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^a-zA-Z0-9]", password))
    variety_count = sum([has_lower, has_upper, has_digit, has_special])

    return len(password) < 10 or variety_count <= 2


def detect_repeated_chars(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    match = REPEATED_CHARS_PATTERN.search(password)
    if not match:
        return None

    return PatternFinding(
        code="repeated_characters",
        message="tekrarlı karakter tespit edildi",
        severity="medium",
        penalty=20 if len(password) <= 10 else 10,
    )


def detect_sequential_chars(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password).lower()

    for i in range(len(password) - 2):
        trio = password[i:i + 3]

        if not trio.isalnum():
            continue

        ascending = (
            ord(trio[1]) - ord(trio[0]) == 1
            and ord(trio[2]) - ord(trio[1]) == 1
        )
        descending = (
            ord(trio[0]) - ord(trio[1]) == 1
            and ord(trio[1]) - ord(trio[2]) == 1
        )

        if ascending or descending:
            if _is_strong_context(password):
                penalty = 8
            elif len(password) <= 8:
                penalty = 30
            else:
                penalty = 14

            return PatternFinding(
                code="sequential_characters",
                message="ardışık karakter tespit edildi",
                severity="medium",
                penalty=penalty,
            )

    return None


def detect_keyboard_pattern(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password).lower()

    for row in KEYBOARD_ROWS:
        for size in range(4, 2, -1):
            for i in range(len(row) - size + 1):
                chunk = row[i:i + size]
                reverse_chunk = chunk[::-1]

                if chunk in password or reverse_chunk in password:
                    return PatternFinding(
                        code="keyboard_pattern",
                        message="klavye deseni tespit edildi",
                        severity="high",
                        penalty=35 if len(password) <= 10 else 18,
                    )

    return None


def detect_common_year(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    match = COMMON_YEARS_PATTERN.search(password)
    if not match:
        return None

    year = match.group(0)

    return PatternFinding(
        code="common_year",
        message="yaygın yıl tespit edildi",
        severity="medium",
        penalty=8 if _is_strong_context(password) else 14,
    )


def detect_date_pattern(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    if re.search(r"(?<!\d)\d{8}(?!\d)", password):
        return PatternFinding(
            code="date_pattern",
            message="tarih benzeri sayı deseni tespit edildi",
            severity="medium",
            penalty=18,
        )

    return None


def detect_phone_pattern(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    if re.search(r"(?<!\d)5\d{9}(?!\d)", password):
        return PatternFinding(
            code="phone_pattern",
            message="telefon numarası benzeri yapı tespit edildi",
            severity="medium",
            penalty=20,
        )

    return None


def detect_common_name(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password).lower()

    for name in COMMON_NAMES:
        if name in password:
            return PatternFinding(
                code="common_name",
                message="yaygın isim tespit edildi",
                severity="medium",
                penalty=15,
            )

    return None


def detect_common_word(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password).lower()

    for word in COMMON_WORDS:
        if word in password:
            return PatternFinding(
                code="common_word",
                message="yaygın kelime tespit edildi",
                severity="high",
                penalty=35 if len(password) <= 10 else 18,
            )

    return None


def detect_only_digits(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    if password and password.isdigit():
        return PatternFinding(
            code="only_digits",
            message="yalnızca rakamlardan oluşuyor",
            severity="high",
            penalty=45 if len(password) <= 8 else 30,
        )

    return None


def detect_only_letters(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    if password and password.isalpha():
        return PatternFinding(
            code="only_letters",
            message="yalnızca harflerden oluşuyor",
            severity="high",
            penalty=35 if len(password) <= 10 else 25,
        )

    return None


_DETECTORS = [
    detect_repeated_chars,
    detect_sequential_chars,
    detect_keyboard_pattern,
    detect_common_year,
    detect_common_word,
    detect_common_name,
    detect_date_pattern,
    detect_phone_pattern,
    detect_only_digits,
    detect_only_letters,
]


def _normalize_finding(result: Optional[object]) -> Optional[PatternFinding]:
    if result is None:
        return None

    if isinstance(result, PatternFinding):
        return result

    if isinstance(result, str):
        return PatternFinding(
            code="generic_pattern",
            message=result,
            severity=_severity_for_pattern(result),
            penalty=_penalty_for_pattern(result, ""),
        )

    return None


def _deduplicate_findings(findings: List[PatternFinding]) -> List[PatternFinding]:
    seen_messages = set()
    unique_findings: List[PatternFinding] = []

    for finding in findings:
        if finding.message in seen_messages:
            continue

        seen_messages.add(finding.message)
        unique_findings.append(finding)

    return unique_findings


def detect_patterns(password: Optional[str]) -> List[str]:
    password = _safe_password(password)
    findings: List[PatternFinding] = []

    for detector in _DETECTORS:
        finding = _normalize_finding(detector(password))
        if finding is not None:
            findings.append(finding)

    return [finding.message for finding in _deduplicate_findings(findings)]


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
        or "yaygın isim" in pattern
        or "tarih" in pattern
        or "telefon" in pattern
    ):
        return "medium"

    return "low"


def _penalty_for_pattern(pattern: str, password: str) -> int:
    pattern_lower = pattern.lower()
    password = _safe_password(password)
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

    if "yaygın isim" in pattern_lower:
        return 15

    if "tarih" in pattern_lower:
        return 18

    if "telefon" in pattern_lower:
        return 20

    return 10


def detect_pattern_details(password: Optional[str]) -> List[Dict[str, Any]]:
    password = _safe_password(password)
    findings: List[PatternFinding] = []

    for detector in _DETECTORS:
        finding = _normalize_finding(detector(password))
        if finding is not None:
            findings.append(finding)

    unique_findings = _deduplicate_findings(findings)

    return [
        {
            "code": finding.code,
            "pattern": finding.message,
            "message": finding.message,
            "severity": finding.severity,
            "penalty": int(finding.penalty),
        }
        for finding in unique_findings
    ]