"""
Güvenli parola üretici modülünün testleri.
"""

import re

from src.security.generator import _meets_criteria, generate_password
from src.security.patterns import detect_patterns


def test_meets_criteria_returns_false_for_weak_password():
    assert not _meets_criteria("password")
    assert not _meets_criteria("12345678")


def test_meets_criteria_returns_true_for_strong_password():
    assert _meets_criteria("Ab1!fHr9")


def test_generate_password_default_length_and_structure():
    result = generate_password()
    assert result["length"] == 16
    assert len(result["password"]) == 16
    assert re.search(r"[A-Z]", result["password"])
    assert re.search(r"[a-z]", result["password"])
    assert re.search(r"\d", result["password"])
    assert re.search(r"[^a-zA-Z0-9]", result["password"])
    assert detect_patterns(result["password"]) == []
    assert result["weak_patterns"] == []


def test_generate_password_minimum_length_enforced():
    result = generate_password(length=4)
    assert result["length"] == 8
    assert len(result["password"]) == 8
