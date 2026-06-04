"""
Rule-based password analysis module.

Each rule function operates independently and returns a result dictionary.
The analyze_rules function combines all results into a comprehensive report.

Output format: JSON-compatible dictionary with rule checks and scoring.
"""

import re
import string
from typing import Dict, Any


# Character sets
UPPERCASE_CHARS = set(string.ascii_uppercase)
LOWERCASE_CHARS = set(string.ascii_lowercase)
DIGIT_CHARS = set(string.digits)
SPECIAL_CHARS = set("!@#$%^&*()-_=+[]{}|;:,.<>?~`")


def check_length(password: str, min_length: int = 8, max_length: int = 128) -> Dict[str, Any]:
    """
    Check password length against minimum and maximum constraints.

    Args:
        password: Password to check.
        min_length: Minimum required length (default: 8).
        max_length: Maximum allowed length (default: 128).

    Returns:
        Dictionary with 'passed' (bool) and 'details' (str) keys.
    """
    length = len(password) if password else 0
    passed = min_length <= length <= max_length

    if not passed:
        if length < min_length:
            details = f"Uzunluk yetersiz: {length} karakter (minimum {min_length} gerekli)"
        else:
            details = f"Uzunluk aşıldı: {length} karakter (maksimum {max_length})"
    else:
        details = f"Uzunluk uygun: {length} karakter"

    return {"passed": passed, "details": details}


def check_uppercase(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one uppercase letter.

    Args:
        password: Password to check.

    Returns:
        Dictionary with 'passed' (bool) and 'details' (str) keys.
    """
    if not password:
        return {"passed": False, "details": "Parola boş"}

    passed = any(c in UPPERCASE_CHARS for c in password)
    details = (
        "Büyük harf bulunuyor"
        if passed
        else "Büyük harf yok (en az 1 tane gerekli)"
    )

    return {"passed": passed, "details": details}


def check_lowercase(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one lowercase letter.

    Args:
        password: Password to check.

    Returns:
        Dictionary with 'passed' (bool) and 'details' (str) keys.
    """
    if not password:
        return {"passed": False, "details": "Parola boş"}

    passed = any(c in LOWERCASE_CHARS for c in password)
    details = (
        "Küçük harf bulunuyor"
        if passed
        else "Küçük harf yok (en az 1 tane gerekli)"
    )

    return {"passed": passed, "details": details}


def check_digits(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one digit.

    Args:
        password: Password to check.

    Returns:
        Dictionary with 'passed' (bool) and 'details' (str) keys.
    """
    if not password:
        return {"passed": False, "details": "Parola boş"}

    passed = any(c in DIGIT_CHARS for c in password)
    details = (
        "Rakam bulunuyor"
        if passed
        else "Rakam yok (en az 1 tane gerekli)"
    )

    return {"passed": passed, "details": details}


def check_special_chars(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one special character.

    Args:
        password: Password to check.

    Returns:
        Dictionary with 'passed' (bool) and 'details' (str) keys.
    """
    if not password:
        return {"passed": False, "details": "Parola boş"}

    passed = any(c in SPECIAL_CHARS for c in password)
    special_string = "!@#$%^&*()-_=+[]{}|;:,.<>?~`"
    details = (
        "Özel karakter bulunuyor"
        if passed
        else f"Özel karakter yok (en az 1 tane gerekli: {special_string})"
    )

    return {"passed": passed, "details": details}


def analyze_rules(
    password: str,
    min_length: int = 8,
    max_length: int = 128,
) -> Dict[str, Any]:
    """
    Analyze password against all rules and return comprehensive report.

    Args:
        password: Password to analyze.
        min_length: Minimum required length (default: 8).
        max_length: Maximum allowed length (default: 128).

    Returns:
        JSON-compatible dictionary with all rule checks, passed count, and score.
    """
    password = str(password) if password is not None else ""

    checks = {
        "length": check_length(password, min_length, max_length),
        "uppercase": check_uppercase(password),
        "lowercase": check_lowercase(password),
        "digits": check_digits(password),
        "special_chars": check_special_chars(password),
    }

    passed_count = sum(1 for check in checks.values() if check["passed"])
    total_checks = len(checks)
    score = (passed_count / total_checks) * 100 if total_checks > 0 else 0.0

    return {
        "password": password,
        "checks": checks,
        "passed_count": passed_count,
        "total_checks": total_checks,
        "score": round(score, 2),
    }
