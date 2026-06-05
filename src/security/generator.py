"""
Güvenli parola üretici modülü — geliştirilmiş sürüm.
"""

import secrets
import string

from src.security.patterns import detect_patterns

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SPECIAL = "!@#$%^&*()-_=+[]{}|;:,.<>?"

MAX_ATTEMPTS = 200
DEFAULT_LENGTH = 16
MIN_LENGTH = 8
DEFAULT_COUNT = 3


def _balanced_candidate(length):
    """Her karakter grubundan dengeli sayıda karakter üretir."""
    quarter = max(1, length // 4)
    remainder = length - quarter * 4

    chars = (
        [secrets.choice(UPPERCASE) for _ in range(quarter)]
        + [secrets.choice(LOWERCASE) for _ in range(quarter)]
        + [secrets.choice(DIGITS) for _ in range(quarter)]
        + [secrets.choice(SPECIAL) for _ in range(quarter + remainder)]
    )
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _has_sequential(password, n=3):
    pw = password.lower()
    for i in range(len(pw) - n + 1):
        chunk = pw[i:i+n]
        if all(ord(chunk[j+1]) - ord(chunk[j]) == 1 for j in range(n-1)):
            return True
    return False


def _has_repeated(password, n=3):
    for i in range(len(password) - n + 1):
        if len(set(password[i:i+n])) == 1:
            return True
    return False


_KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]


def _has_keyboard_pattern(password, n=3):
    pw = password.lower()
    for row in _KEYBOARD_ROWS:
        for i in range(len(row) - n + 1):
            if row[i:i+n] in pw:
                return True
    return False


def _is_strong(password):
    if len(password) < MIN_LENGTH:
        return False
    has_upper = any(c in UPPERCASE for c in password)
    has_lower = any(c in LOWERCASE for c in password)
    has_digit = any(c in DIGITS for c in password)
    has_special = any(c in SPECIAL for c in password)
    no_sequential = not _has_sequential(password)
    no_repeated = not _has_repeated(password)
    no_keyboard = not _has_keyboard_pattern(password)
    no_weak_patterns = len(detect_patterns(password)) == 0
    return all([has_upper, has_lower, has_digit, has_special,
                no_sequential, no_repeated, no_keyboard, no_weak_patterns])


def _generate_one(length):
    for _ in range(MAX_ATTEMPTS):
        candidate = _balanced_candidate(length)
        if _is_strong(candidate):
            return candidate
    # Garantili minimum: tekrar dene, desen kontrolü olmadan
    return _balanced_candidate(length)


def generate_password(length=DEFAULT_LENGTH):
    """
    Tek güvenli parola üretir.
    Döndürür: {"password": str, "length": int, "weak_patterns": list, "is_strong": bool}
    """
    length = max(MIN_LENGTH, length)
    password = _generate_one(length)
    patterns = detect_patterns(password)
    return {
        "password": password,
        "length": len(password),
        "weak_patterns": patterns,
        "is_strong": _is_strong(password),
    }


def generate_multiple(length=DEFAULT_LENGTH, count=DEFAULT_COUNT):
    """
    Birden fazla güvenli parola seçeneği üretir.
    Döndürür: [{"password": str, "length": int, "weak_patterns": list, "is_strong": bool}, ...]
    """
    length = max(MIN_LENGTH, length)
    results = []
    seen = set()
    attempts = 0

    while len(results) < count and attempts < MAX_ATTEMPTS * count:
        pw = _generate_one(length)
        attempts += 1
        if pw not in seen:
            seen.add(pw)
            patterns = detect_patterns(pw)
            results.append({
                "password": pw,
                "length": len(pw),
                "weak_patterns": patterns,
                "is_strong": _is_strong(pw),
            })

    return results
