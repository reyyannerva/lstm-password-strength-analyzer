"""
Rule-based password analysis module.

This module analyzes a password using independent security rules and combines
the results into a JSON-compatible report.

The goal is to provide:
- Clear rule-level results
- Human-readable Turkish feedback
- A 0-100 rule-based score
- Details that can be used by API endpoints and frontend components
"""

import re
import string
from typing import Any, Dict, List


UPPERCASE_CHARS = set(string.ascii_uppercase)
LOWERCASE_CHARS = set(string.ascii_lowercase)
DIGIT_CHARS = set(string.digits)
SPECIAL_CHARS = set("!@#$%^&*()-_=+[]{}|;:,.<>?~`")


def _normalize_password(password: str) -> str:
    """
    Convert password input into a safe string value.
    """

    return str(password) if password is not None else ""


def check_length(
    password: str,
    min_length: int = 8,
    max_length: int = 128,
) -> Dict[str, Any]:
    """
    Check password length requirements.
    """

    password = _normalize_password(password)
    length = len(password)

    if length < min_length:
        return {
            "passed": False,
            "details": f"Parola en az {min_length} karakter olmalı (mevcut: {length})",
            "current_length": length,
            "min_length": min_length,
            "max_length": max_length,
        }

    if length > max_length:
        return {
            "passed": False,
            "details": f"Parola en fazla {max_length} karakter olmalı (mevcut: {length})",
            "current_length": length,
            "min_length": min_length,
            "max_length": max_length,
        }

    return {
        "passed": True,
        "details": f"Parola uzunluğu uygun ({length} karakter)",
        "current_length": length,
        "min_length": min_length,
        "max_length": max_length,
    }


def check_uppercase(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one uppercase letter.
    """

    password = _normalize_password(password)
    count = sum(1 for char in password if char in UPPERCASE_CHARS)
    passed = count > 0

    return {
        "passed": passed,
        "details": (
            f"Parola büyük harf içeriyor ({count} adet)"
            if passed
            else "Parola en az bir büyük harf (A-Z) içermelidir"
        ),
        "count": count,
    }


def check_lowercase(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one lowercase letter.
    """

    password = _normalize_password(password)
    count = sum(1 for char in password if char in LOWERCASE_CHARS)
    passed = count > 0

    return {
        "passed": passed,
        "details": (
            f"Parola küçük harf içeriyor ({count} adet)"
            if passed
            else "Parola en az bir küçük harf (a-z) içermelidir"
        ),
        "count": count,
    }


def check_digits(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one digit.
    """

    password = _normalize_password(password)
    count = sum(1 for char in password if char in DIGIT_CHARS)
    passed = count > 0

    return {
        "passed": passed,
        "details": (
            f"Parola rakam içeriyor ({count} adet)"
            if passed
            else "Parola en az bir rakam (0-9) içermelidir"
        ),
        "count": count,
    }


def check_special_chars(password: str) -> Dict[str, Any]:
    """
    Check if password contains at least one special character.
    """

    password = _normalize_password(password)
    count = sum(1 for char in password if char in SPECIAL_CHARS)
    passed = count > 0

    return {
        "passed": passed,
        "details": (
            f"Parola özel karakter içeriyor ({count} adet)"
            if passed
            else "Parola en az bir özel karakter içermelidir (!@#$%^&* vb.)"
        ),
        "count": count,
        "allowed_special_chars": "".join(sorted(SPECIAL_CHARS)),
    }


def check_repeated_characters(password: str) -> Dict[str, Any]:
    """
    Check whether the password contains repeated characters such as aaa or 111.
    """

    password = _normalize_password(password)
    matched = re.search(r"(.)\1{2,}", password)
    passed = matched is None

    return {
        "passed": passed,
        "details": (
            "Parola tekrarlı karakter deseni içermiyor"
            if passed
            else f"Tekrarlı karakter deseni bulundu: '{matched.group(0)}'"
        ),
        "matched_pattern": None if passed else matched.group(0),
    }


def check_sequential_patterns(password: str) -> Dict[str, Any]:
    """
    Check common sequential patterns such as abc, 123, qwerty.
    """

    password = _normalize_password(password).lower()

    sequential_patterns = [
        "abc",
        "abcd",
        "abcde",
        "123",
        "1234",
        "12345",
        "234",
        "345",
        "456",
        "567",
        "678",
        "789",
        "987",
        "876",
        "765",
        "654",
        "543",
        "432",
        "321",
        "qwerty",
        "asdf",
        "zxcv",
    ]

    matched_patterns = [
        pattern for pattern in sequential_patterns if pattern in password
    ]

    passed = len(matched_patterns) == 0

    return {
        "passed": passed,
        "details": (
            "Parola yaygın ardışık desen içermiyor"
            if passed
            else f"Yaygın ardışık desen bulundu: {', '.join(matched_patterns)}"
        ),
        "matched_patterns": matched_patterns,
    }


def check_common_words(password: str) -> Dict[str, Any]:
    """
    Check common weak password words.
    """

    password = _normalize_password(password).lower()

    common_words = [
        "password",
        "parola",
        "sifre",
        "şifre",
        "admin",
        "login",
        "welcome",
        "qwerty",
        "letmein",
        "monkey",
        "dragon",
        "master",
        "princess",
        "sunshine",
        "iloveyou",
        "abc123",
        "123456",
    ]

    matched_words = [word for word in common_words if word in password]
    passed = len(matched_words) == 0

    return {
        "passed": passed,
        "details": (
            "Parola yaygın zayıf kelime içermiyor"
            if passed
            else f"Yaygın zayıf kelime bulundu: {', '.join(matched_words)}"
        ),
        "matched_words": matched_words,
    }


def check_character_diversity(password: str) -> Dict[str, Any]:
    """
    Calculate how many character groups are used in the password.
    """

    password = _normalize_password(password)

    groups = {
        "uppercase": any(char in UPPERCASE_CHARS for char in password),
        "lowercase": any(char in LOWERCASE_CHARS for char in password),
        "digits": any(char in DIGIT_CHARS for char in password),
        "special_chars": any(char in SPECIAL_CHARS for char in password),
    }

    used_group_count = sum(1 for used in groups.values() if used)
    passed = used_group_count >= 3

    return {
        "passed": passed,
        "details": (
            f"Karakter çeşitliliği yeterli ({used_group_count}/4 grup kullanılmış)"
            if passed
            else f"Karakter çeşitliliği düşük ({used_group_count}/4 grup kullanılmış)"
        ),
        "used_group_count": used_group_count,
        "groups": groups,
    }


def check_only_letters_or_digits(password: str) -> Dict[str, Any]:
    """
    Check whether password consists only of letters or only of digits.
    """

    password = _normalize_password(password)

    if not password:
        return {
            "passed": False,
            "details": "Parola boş",
            "only_letters": False,
            "only_digits": False,
        }

    only_letters = password.isalpha()
    only_digits = password.isdigit()
    passed = not only_letters and not only_digits

    return {
        "passed": passed,
        "details": (
            "Parola yalnızca harflerden veya yalnızca rakamlardan oluşmuyor"
            if passed
            else "Parola yalnızca harflerden veya yalnızca rakamlardan oluşmamalı"
        ),
        "only_letters": only_letters,
        "only_digits": only_digits,
    }


def _security_level_from_score(score: float) -> str:
    """
    Convert rule-based score to a security level.
    """

    if score < 20:
        return "Çok Zayıf"
    if score < 40:
        return "Zayıf"
    if score < 60:
        return "Orta"
    if score < 80:
        return "Güçlü"
    return "Çok Güçlü"


def _build_recommendations(checks: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Build user-friendly recommendations from failed checks.
    """

    recommendations = []

    if not checks["length"]["passed"]:
        recommendations.append("Parolayı en az 8, tercihen 12 veya daha fazla karakter yapın.")

    if not checks["uppercase"]["passed"]:
        recommendations.append("En az bir büyük harf ekleyin.")

    if not checks["lowercase"]["passed"]:
        recommendations.append("En az bir küçük harf ekleyin.")

    if not checks["digits"]["passed"]:
        recommendations.append("En az bir rakam ekleyin.")

    if not checks["special_chars"]["passed"]:
        recommendations.append("En az bir özel karakter ekleyin.")

    if not checks["repeated_characters"]["passed"]:
        recommendations.append("Aynı karakteri üç veya daha fazla kez tekrar etmekten kaçının.")

    if not checks["sequential_patterns"]["passed"]:
        recommendations.append("123, abc, qwerty gibi tahmin edilebilir dizilerden kaçının.")

    if not checks["common_words"]["passed"]:
        recommendations.append("password, admin, parola gibi yaygın kelimeleri kullanmayın.")

    if not checks["character_diversity"]["passed"]:
        recommendations.append(
            "Büyük harf, küçük harf, rakam ve özel karakter gruplarını birlikte kullanın."
        )

    if not checks["only_letters_or_digits"]["passed"]:
        recommendations.append(
            "Parolayı yalnızca harflerden veya yalnızca rakamlardan oluşturmayın."
        )

    if not recommendations:
        recommendations.append(
            "Parola temel kural tabanlı güvenlik kontrollerini başarıyla karşılıyor."
        )

    return recommendations


def analyze_rules(
    password: str,
    min_length: int = 8,
    max_length: int = 128,
) -> Dict[str, Any]:
    """
    Comprehensive rule-based password analysis.

    Returns:
        JSON-compatible dictionary with:
        - password
        - checks
        - passed_count
        - total_checks
        - total_count
        - score
        - security_level
        - all_passed
        - details
        - recommendations
    """

    password = _normalize_password(password)
    if not password:
        checks = {
            "length": check_length(password, min_length, max_length),
            "uppercase": check_uppercase(password),
            "lowercase": check_lowercase(password),
            "digits": check_digits(password),
            "special_chars": check_special_chars(password),
            "repeated_characters": {
                "passed": False,
                "details": "Parola boş olduğu için tekrarlı karakter kontrolü yapılamadı",
                "matched_pattern": None,
            },
            "sequential_patterns": {
                "passed": False,
                "details": "Parola boş olduğu için ardışık desen kontrolü yapılamadı",
                "matched_patterns": [],
            },
            "common_words": {
                "passed": False,
                "details": "Parola boş olduğu için yaygın kelime kontrolü yapılamadı",
                "matched_words": [],
            },
            "character_diversity": check_character_diversity(password),
            "only_letters_or_digits": check_only_letters_or_digits(password),
        }

        return {
            "password": password,
            "checks": checks,
            "passed_count": 0,
            "total_checks": len(checks),
            "score": 0,
            "security_level": "Çok Zayıf",
            "all_passed": False,
            "details": [
                f"✗ {check['details']}"
                for check in checks.values()
            ],
            "recommendations": _build_recommendations(checks),
        }

    if password == "":
        return {
            "password": "",
            "checks": {},
            "passed_count": 0,
            "total_checks": 0,
            "total_count": 0,
            "score": 0.0,
            "security_level": "Çok Zayıf",
            "all_passed": False,
            "details": ["Parola boş olamaz."],
            "recommendations": ["Parola boş olamaz."],
        }

    checks = {
        "length": check_length(password, min_length, max_length),
        "uppercase": check_uppercase(password),
        "lowercase": check_lowercase(password),
        "digits": check_digits(password),
        "special_chars": check_special_chars(password),
        "repeated_characters": check_repeated_characters(password),
        "sequential_patterns": check_sequential_patterns(password),
        "common_words": check_common_words(password),
        "character_diversity": check_character_diversity(password),
        "only_letters_or_digits": check_only_letters_or_digits(password),
    }

    passed_count = sum(1 for check in checks.values() if check["passed"])
    total_checks = len(checks)
    score = (passed_count / total_checks) * 100 if total_checks else 0.0
    score = round(score, 2)

    details = [
        f"✓ {check['details']}" if check["passed"] else f"✗ {check['details']}"
        for check in checks.values()
    ]

    return {
        "password": password,
        "checks": checks,
        "passed_count": passed_count,
        "total_checks": total_checks,
        "total_count": total_checks,
        "score": score,
        "security_level": _security_level_from_score(score),
        "all_passed": passed_count == total_checks,
        "details": details,
        "recommendations": _build_recommendations(checks),
    }