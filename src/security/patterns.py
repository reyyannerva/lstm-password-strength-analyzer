"""
Weak password pattern detection module.

This module detects predictable password patterns such as:
- repeated characters
- sequential characters
- keyboard patterns
- common years
- common weak words
- embedded common words
- common names
- date-like numeric patterns
- phone-like numeric patterns
- digit-only passwords
- letter-only passwords

Public API:
- detect_patterns(password) -> list[str]
- detect_pattern_details(password) -> list[dict]
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
    # Parola kelimeleri
    "password", "passwd", "pass", "parola", "sifre",
    # Sistem/yetkili
    "admin", "administrator", "root", "user", "guest", "test",
    # Yaygın giriş
    "login", "logon", "welcome", "access", "enter",
    "letmein", "letme", "secure", "security",
    # Duygusal / yaygın
    "iloveyou", "love", "monkey", "dragon", "master", "shadow",
    "sunshine", "princess", "sunshine", "baseball", "football",
    "soccer", "hockey", "ninja", "batman", "superman", "spider",
    # İngilizce yaygın
    "abc", "qwerty", "trustno", "hello", "changeme",
    "secret", "default", "temp", "demo", "sample",
    # Türkçe yaygın
    "merhaba", "sifrem", "turkiye", "istanbul", "ankara",
]

COMMON_NAMES = [
    # Türkçe
    "ahmet", "mehmet", "ali", "ayse", "ayşe", "fatma",
    "zeynep", "burak", "emre", "selin", "deniz", "mert",
    "cansu", "yusuf", "omer", "ömer", "hasan", "huseyin",
    # İngilizce
    "john", "michael", "mike", "emma", "olivia", "liam",
    "noah", "james", "david", "sarah", "jessica", "daniel",
]

COMMON_YEARS = [str(year) for year in range(1950, 2031)]
REPEATED_CHARS_PATTERN = re.compile(r"(.)\1{2,}")


def _safe_password(password: Optional[str]) -> str:
    return "" if password is None else str(password)


def _is_strong_context(password: Optional[str]) -> bool:
    password = _safe_password(password)

    return (
        len(password) >= 10
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^a-zA-Z0-9]", password))
    )


def detect_repeated_chars(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    if REPEATED_CHARS_PATTERN.search(password):
        return PatternFinding(
            code="repeated_chars",
            message="Tekrarlayan karakter deseni tespit edildi (tekrarlı karakter)",
            severity="medium",
            penalty=20 if len(password) <= 10 else 10,
        )

    return None


def detect_sequential_chars(password: Optional[str]) -> Optional[PatternFinding]:
    raw_password = _safe_password(password)
    lowered_password = raw_password.lower()

    for i in range(len(lowered_password) - 2):
        trio = lowered_password[i:i + 3]

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

        if not ascending and not descending:
            continue

        simple = lowered_password.isdigit() or lowered_password.isalpha()
        strong_context = _is_strong_context(raw_password)

        if strong_context:
            return PatternFinding(
                code="embedded_sequence",
                message="Kısa bir ardışık karakter deseni tespit edildi",
                severity="low",
                penalty=5,
            )

        if simple:
            return PatternFinding(
                code="simple_sequence",
                message="ardışık karakter tespit edildi",
                severity="high",
                penalty=35,
            )

        return PatternFinding(
            code="embedded_sequence",
            message="ardışık karakter tespit edildi",
            severity="medium",
            penalty=20,
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
                        message="Klavye deseni tespit edildi (klavye deseni)",
                        severity="high",
                        penalty=35 if len(password) <= 10 else 18,
                    )

    return None


def detect_common_year(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    for year in COMMON_YEARS:
        if year in password:
            return PatternFinding(
                code="common_year",
                message=f"yaygın yıl tespit edildi: {year}",
                severity="low",
                penalty=8,
            )

    return None


def detect_date_pattern(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    if re.search(r"(?<!\d)\d{8}(?!\d)", password):
        return PatternFinding(
            code="date_pattern",
            message="Tarih benzeri sayı deseni tespit edildi",
            severity="medium",
            penalty=18,
        )

    return None


def detect_phone_pattern(password: Optional[str]) -> Optional[PatternFinding]:
    password = _safe_password(password)

    if re.search(r"(?<!\d)5\d{9}(?!\d)", password):
        return PatternFinding(
            code="phone_pattern",
            message="Telefon numarası benzeri yapı tespit edildi",
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
                message=f"Yaygın isim tespit edildi: {name}",
                severity="medium",
                penalty=15,
            )

    return None


def detect_common_word(password: Optional[str]) -> Optional[PatternFinding]:
    raw_password = _safe_password(password)
    password = raw_password.lower()

    for word in COMMON_WORDS:
        if word not in password:
            continue

        direct_word = password == word
        word_with_digits = password.startswith(word) and password[len(word):].isdigit()

        if direct_word or word_with_digits:
            return PatternFinding(
                code="common_word",
                message=f"Yaygın parola kelimesi tespit edildi: {word} (yaygın kelime)",
                severity="high",
                penalty=35,
            )

        return PatternFinding(
            code="embedded_common_word",
            message=f"Yaygın parola kelimesi gömülü olarak tespit edildi: {word} (yaygın kelime)",
            severity="medium",
            penalty=18,
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
            severity="medium",
            penalty=25,
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


def _deduplicate_findings(findings: List[PatternFinding]) -> List[PatternFinding]:
    seen_codes = set()
    unique: List[PatternFinding] = []

    for finding in findings:
        if finding.code in seen_codes:
            continue

        seen_codes.add(finding.code)
        unique.append(finding)

    return unique


def _collect_findings(password: Optional[str]) -> List[PatternFinding]:
    password = _safe_password(password)
    findings: List[PatternFinding] = []

    for detector in _DETECTORS:
        result = detector(password)
        if result is not None:
            findings.append(result)

    return _deduplicate_findings(findings)


def detect_patterns(password: Optional[str]) -> List[str]:
    return [finding.message for finding in _collect_findings(password)]


def detect_pattern_details(password: Optional[str]) -> List[Dict[str, Any]]:
    return [
        {
            "code": finding.code,
            "pattern": finding.message,
            "message": finding.message,
            "severity": finding.severity,
            "penalty": int(finding.penalty),
        }
        for finding in _collect_findings(password)
    ]