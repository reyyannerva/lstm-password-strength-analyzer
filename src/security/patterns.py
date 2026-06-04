"""
Zayıf parola desen tespit modülü.
"""

import re

KEYBOARD_ROWS = [
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "qwerty", "asdfgh", "zxcvbn",
    "1234567890",
]

COMMON_WORDS = [
    "password", "parola", "123456", "qwerty", "letmein",
    "welcome", "admin", "login", "iloveyou", "monkey",
    "dragon", "master", "abc123", "sunshine", "princess",
]

COMMON_YEARS = [str(y) for y in range(1950, 2030)]


def detect_repeated_chars(password):
    if re.search(r"(.)\1{2,}", password):
        return "tekrarlı karakter (örn. 'aaa', '111')"
    return None


def detect_sequential_chars(password):
    pw = password.lower()
    for i in range(len(pw) - 2):
        trio = pw[i:i+3]
        if (
            ord(trio[1]) - ord(trio[0]) == 1 and
            ord(trio[2]) - ord(trio[1]) == 1
        ):
            return "ardışık karakter (örn. 'abc', '123')"
    return None


def detect_keyboard_pattern(password):
    pw = password.lower()
    for row in KEYBOARD_ROWS:
        for i in range(len(row) - 2):
            chunk = row[i:i+3]
            if chunk in pw:
                return f"klavye deseni (örn. '{chunk}')"
    return None


def detect_common_year(password):
    for year in COMMON_YEARS:
        if year in password:
            return f"yaygın yıl içeriyor ({year})"
    return None


def detect_common_word(password):
    pw = password.lower()
    for word in COMMON_WORDS:
        if word in pw:
            return f"yaygın kelime içeriyor ('{word}')"
    return None


def detect_only_digits(password):
    if password.isdigit():
        return "yalnızca rakamlardan oluşuyor"
    return None


def detect_only_letters(password):
    if password.isalpha():
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


def detect_patterns(password):
    """Tespit edilen zayıf desenlerin listesini döndürür."""
    found = []
    for fn in _DETECTORS:
        result = fn(password)
        if result:
            found.append(result)
    return found
