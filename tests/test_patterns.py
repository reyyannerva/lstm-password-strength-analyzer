"""Pattern detection tests for password weakness."""

from src.security.patterns import detect_patterns


def test_detect_patterns_no_weakness():
    assert detect_patterns("S3cure!Pass") == []


def test_detect_repeated_characters_detected():
    patterns = detect_patterns("aaa1234")
    assert any("tekrarlı karakter" in p for p in patterns)


def test_detect_sequential_characters_detected():
    patterns = detect_patterns("abc123")
    assert any("ardışık karakter" in p for p in patterns)


def test_detect_keyboard_pattern_detected():
    patterns = detect_patterns("qwerty11")
    assert any("klavye deseni" in p for p in patterns)


def test_detect_common_year_detected():
    patterns = detect_patterns("MyPass2023!")
    assert any("yaygın yıl" in p for p in patterns)


def test_detect_common_word_detected():
    patterns = detect_patterns("admin123")
    assert any("yaygın kelime" in p for p in patterns)


def test_detect_only_digits():
    patterns = detect_patterns("123456")
    assert any("yalnızca rakamlardan" in p for p in patterns)


def test_detect_only_letters():
    patterns = detect_patterns("abcdef")
    assert any("yalnızca harflerden" in p for p in patterns)
