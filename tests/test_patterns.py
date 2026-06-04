"""
Parola zayıf desen tespit modülünün testleri.
"""

from src.security.patterns import (
    detect_patterns,
    detect_repeated_chars,
    detect_sequential_chars,
    detect_keyboard_pattern,
    detect_common_year,
    detect_common_word,
    detect_only_digits,
    detect_only_letters,
)


def test_detect_repeated_chars():
    assert detect_repeated_chars("aaabbb") == "tekrarlı karakter (örn. 'aaa', '111')"
    assert detect_repeated_chars("abc") is None


def test_detect_sequential_chars():
    assert detect_sequential_chars("abcd") == "ardışık karakter (örn. 'abc', '123')"
    assert detect_sequential_chars("13579") is None


def test_detect_keyboard_pattern():
    assert detect_keyboard_pattern("qwe") == "klavye deseni (örn. 'qwe')"
    assert detect_keyboard_pattern("pass") is None


def test_detect_common_year():
    assert detect_common_year("2023Secure") == "yaygın yıl içeriyor (2023)"
    assert detect_common_year("1999") == "yaygın yıl içeriyor (1999)"
    assert detect_common_year("abcd") is None


def test_detect_common_word():
    assert detect_common_word("MyPassword123") == "yaygın kelime içeriyor ('password')"
    assert detect_common_word("SafePass") is None


def test_detect_only_digits_and_letters():
    assert detect_only_digits("123456") == "yalnızca rakamlardan oluşuyor"
    assert detect_only_digits("abc123") is None
    assert detect_only_letters("abcdef") == "yalnızca harflerden oluşuyor"
    assert detect_only_letters("abc123") is None


def test_detect_patterns_returns_multiple_weak_patterns():
    patterns = detect_patterns("qwerty123456")
    assert "klavye deseni (örn. 'qwe')" in patterns
    assert "ardışık karakter (örn. 'abc', '123')" in patterns


def test_detect_patterns_returns_empty_for_strong_password():
    assert detect_patterns("A!9rTg#5") == []
