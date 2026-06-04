"""
Güvenli parola üretici modülü.
"""

import secrets
import string

from src.security.patterns import detect_patterns

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SPECIAL = "!@#$%^&*()-_=+[]{}|;:,.<>?"

MAX_ATTEMPTS = 100


def _meets_criteria(password):
    has_upper = any(c in UPPERCASE for c in password)
    has_lower = any(c in LOWERCASE for c in password)
    has_digit = any(c in DIGITS for c in password)
    has_special = any(c in SPECIAL for c in password)
    no_weak_patterns = len(detect_patterns(password)) == 0
    return has_upper and has_lower and has_digit and has_special and no_weak_patterns


def _generate_candidate(length):
    required = [
        secrets.choice(UPPERCASE),
        secrets.choice(LOWERCASE),
        secrets.choice(DIGITS),
        secrets.choice(SPECIAL),
    ]
    alphabet = UPPERCASE + LOWERCASE + DIGITS + SPECIAL
    rest = [secrets.choice(alphabet) for _ in range(length - 4)]
    chars = required + rest
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def generate_password(length=16):
    """
    Minimum güvenlik kriterlerini karşılayan parola üretir.
    Döndürür: {"password": str, "length": int, "weak_patterns": list}
    """
    if length < 8:
        length = 8

    for _ in range(MAX_ATTEMPTS):
        candidate = _generate_candidate(length)
        if _meets_criteria(candidate):
            return {
                "password": candidate,
                "length": len(candidate),
                "weak_patterns": [],
            }

    # Kriterleri tam karşılayan bulunamazsa son adayı döndür
    candidate = _generate_candidate(length)
    return {
        "password": candidate,
        "length": len(candidate),
        "weak_patterns": detect_patterns(candidate),
    }
