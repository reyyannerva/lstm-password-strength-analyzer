"""Comprehensive tests for password weak pattern detection."""

from src.security.patterns import (
    detect_common_word,
    detect_common_year,
    detect_keyboard_pattern,
    detect_only_digits,
    detect_only_letters,
    detect_pattern_details,
    detect_patterns,
    detect_repeated_chars,
    detect_sequential_chars,
)


def test_detect_repeated_chars_returns_finding_for_three_or_more_repeats():
    finding = detect_repeated_chars("aaabbb")

    assert finding is not None
    assert finding.code == "repeated_chars"
    assert "Tekrarlayan" in finding.message
    assert finding.severity == "medium"
    assert finding.penalty > 0


def test_detect_repeated_chars_returns_none_for_normal_password():
    assert detect_repeated_chars("Ab1!safe") is None


def test_detect_sequential_chars_detects_simple_numeric_sequence():
    finding = detect_sequential_chars("123456")

    assert finding is not None
    assert finding.code == "simple_sequence"
    assert finding.severity == "high"
    assert finding.penalty >= 30


def test_detect_sequential_chars_detects_embedded_sequence():
    finding = detect_sequential_chars("Secure123!")

    assert finding is not None
    assert finding.code == "embedded_sequence"
    assert "ardışık" in finding.message
    assert finding.penalty > 0


def test_detect_sequential_chars_penalty_is_low_in_strong_context():
    weak_context = detect_sequential_chars("abcpass")
    strong_context = detect_sequential_chars("Str0ng!Pass123")

    assert weak_context is not None
    assert strong_context is not None
    assert strong_context.penalty < weak_context.penalty
    assert strong_context.severity == "low"


def test_detect_sequential_chars_returns_none_for_non_sequence():
    assert detect_sequential_chars("a1c3e5") is None


def test_detect_keyboard_pattern_detects_full_keyboard_pattern():
    finding = detect_keyboard_pattern("qwerty11")

    assert finding is not None
    assert finding.code == "keyboard_pattern"
    assert "Klavye deseni" in finding.message
    assert finding.severity == "high"


def test_detect_keyboard_pattern_detects_embedded_keyboard_pattern():
    finding = detect_keyboard_pattern("MyqwertyPass")

    assert finding is not None
    assert finding.code in {"keyboard_pattern", "embedded_keyboard_pattern"}
    assert finding.penalty > 0


def test_detect_keyboard_pattern_returns_none_for_safe_password():
    assert detect_keyboard_pattern("A9!xK2#mQ7") is None


def test_detect_common_year_detects_year_between_1950_and_2030():
    finding = detect_common_year("Secure2023!")

    assert finding is not None
    assert finding.code == "common_year"
    assert "2023" in finding.message
    assert finding.severity == "low"


def test_detect_common_year_returns_none_for_non_year_text():
    assert detect_common_year("Secure2040!") is None


def test_detect_common_word_detects_high_risk_common_password_word():
    finding = detect_common_word("password123")

    assert finding is not None
    assert finding.code == "common_word"
    assert finding.severity == "high"
    assert finding.penalty >= 30


def test_detect_common_word_detects_embedded_common_word():
    finding = detect_common_word("MyAdminPortal!9")

    assert finding is not None
    assert finding.code == "embedded_common_word"
    assert finding.severity == "medium"
    assert finding.penalty > 0


def test_detect_common_word_returns_none_for_non_common_word():
    assert detect_common_word("A9!xK2#mQ7") is None


def test_detect_only_digits_detects_numeric_password():
    finding = detect_only_digits("123456")

    assert finding is not None
    assert finding.code == "only_digits"
    assert finding.severity == "high"
    assert finding.penalty >= 30


def test_detect_only_digits_returns_none_for_mixed_password():
    assert detect_only_digits("abc123!") is None


def test_detect_only_letters_detects_letters_only_password():
    finding = detect_only_letters("abcdef")

    assert finding is not None
    assert finding.code == "only_letters"
    assert finding.severity == "medium"
    assert finding.penalty > 0


def test_detect_only_letters_returns_none_for_mixed_password():
    assert detect_only_letters("abc123!") is None


def test_detect_pattern_details_returns_structured_findings():
    findings = detect_pattern_details("password123")

    assert isinstance(findings, list)
    assert len(findings) >= 2

    codes = {item["code"] for item in findings}

    assert "common_word" in codes
    assert "embedded_sequence" in codes or "simple_sequence" in codes

    for item in findings:
        assert "code" in item
        assert "message" in item
        assert "severity" in item
        assert "penalty" in item
        assert isinstance(item["penalty"], int)


def test_detect_patterns_returns_only_messages_for_backward_compatibility():
    patterns = detect_patterns("password123")

    assert isinstance(patterns, list)
    assert all(isinstance(item, str) for item in patterns)
    assert any("Yaygın parola kelimesi" in item for item in patterns)


def test_detect_patterns_returns_multiple_weak_patterns_for_very_weak_password():
    patterns = detect_patterns("qwerty123456")

    assert len(patterns) > 0

    assert any(
        "Klavye deseni" in item
        or "ardışık" in item
        for item in patterns
    )

def test_detect_patterns_returns_empty_for_generated_style_strong_password():
    assert detect_patterns("A9!xK2#mQ7") == []


def test_detect_patterns_handles_none_as_empty_string_safely():
    assert detect_patterns(None) == []


def test_detect_pattern_details_handles_none_as_empty_string_safely():
    assert detect_pattern_details(None) == []


def test_short_sequence_in_strong_password_is_detected_but_not_over_penalized():
    findings = detect_pattern_details("Str0ng!Pass123")

    assert any(item["code"] == "embedded_sequence" for item in findings)

    sequence_findings = [
        item for item in findings if item["code"] == "embedded_sequence"
    ]

    assert sequence_findings[0]["penalty"] <= 5
    assert sequence_findings[0]["severity"] == "low"


def test_common_word_password123_is_more_risky_than_password_inside_complex_password():
    direct = detect_common_word("password123")
    embedded = detect_common_word("MyPassword!94Safe")

    assert direct is not None
    assert embedded is not None
    assert direct.penalty > embedded.penalty
    assert direct.severity == "high"
    assert embedded.severity == "medium"

def test_detects_date_like_pattern():
    patterns = detect_patterns("Ali01012024!")

    assert any("Tarih benzeri" in item for item in patterns)


def test_detects_phone_like_pattern():
    patterns = detect_patterns("Pass5551234567!")

    assert any("Telefon numarası" in item for item in patterns)


def test_detects_common_name_pattern():
    patterns = detect_patterns("Ahmet123!")

    assert any("Yaygın isim" in item for item in patterns)


def test_strong_password_with_short_sequence_is_not_over_penalized():
    details = detect_pattern_details("Str0ng!abcPass")

    sequence_findings = [
        item for item in details
        if item["code"] == "embedded_sequence"
    ]

    assert sequence_findings
    assert sequence_findings[0]["severity"] == "low"
    assert sequence_findings[0]["penalty"] <= 5


def test_multiple_new_patterns_can_be_detected_together():
    patterns = detect_patterns("mehmet15051999!")

    assert any("Yaygın isim" in item for item in patterns)
    assert any("Tarih benzeri" in item for item in patterns)

def test_pattern_detection_performance_on_batch():
    passwords = [
        "password123",
        "Qwerty123!",
        "Str0ng!Pass123",
        "mehmet15051999!",
        "Pass5551234567!",
    ] * 100

    for password in passwords:
        patterns = detect_patterns(password)

        assert isinstance(patterns, list)