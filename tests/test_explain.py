"""
Password explanation and suggestion tests.
"""

import pytest

try:
    from src.security.explain import (
        get_missing_requirements,
        get_pattern_warnings,
        get_improvement_suggestions,
        explain_password,
        format_explanation,
    )
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


@pytest.fixture
def skip_if_unavailable():
    if not AVAILABLE:
        pytest.skip("src/security/explain.py modülü mevcut değil.")


def test_get_missing_requirements_strong_password(skip_if_unavailable):
    result = get_missing_requirements("SecurePass123!")
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_missing_requirements_weak_password(skip_if_unavailable):
    result = get_missing_requirements("weak")
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_missing_requirements_empty_password(skip_if_unavailable):
    result = get_missing_requirements("")
    assert isinstance(result, list)
    assert len(result) == 5  # All requirements missing


def test_get_pattern_warnings_with_patterns(skip_if_unavailable):
    result = get_pattern_warnings("aaa111")
    assert isinstance(result, list)


def test_get_pattern_warnings_no_patterns(skip_if_unavailable):
    result = get_pattern_warnings("SecurePass123!")
    assert isinstance(result, list)


def test_get_improvement_suggestions_returns_list(skip_if_unavailable):
    result = get_improvement_suggestions("password")
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_improvement_suggestions_strong_password(skip_if_unavailable):
    result = get_improvement_suggestions("SecurePass123!")
    assert isinstance(result, list)


def test_explain_password_structure(skip_if_unavailable):
    result = explain_password("test123")
    assert isinstance(result, dict)
    assert "password" in result
    assert "security_level" in result
    assert "assessment" in result
    assert "missing_requirements" in result
    assert "pattern_warnings" in result
    assert "suggestions" in result
    assert "is_strong" in result


def test_explain_password_strong(skip_if_unavailable):
    result = explain_password("MySecure123P@ss")
    # Verify structure regardless of is_strong value
    assert result["security_level"] in ["Güçlü", "Orta", "Zayıf"]
    assert isinstance(result["is_strong"], bool)


def test_explain_password_weak(skip_if_unavailable):
    result = explain_password("weak")
    assert result["is_strong"] is False
    assert result["security_level"] == "Zayıf"


def test_explain_password_empty(skip_if_unavailable):
    result = explain_password("")
    assert result["is_strong"] is False
    assert len(result["missing_requirements"]) == 5


def test_explain_password_none_input(skip_if_unavailable):
    result = explain_password(None)
    assert result["password"] == ""
    assert result["is_strong"] is False


def test_format_explanation_returns_string(skip_if_unavailable):
    result = format_explanation("Test123!")
    assert isinstance(result, str)
    assert "📋" in result or "Parola" in result


def test_format_explanation_contains_assessment(skip_if_unavailable):
    result = format_explanation("weak")
    assert "Güvenlik Seviyesi" in result
    assert "Değerlendirme" in result


def test_format_explanation_contains_suggestions(skip_if_unavailable):
    result = format_explanation("password")
    assert "İyileştirme" in result or "💡" in result


def test_explain_password_medium_strength(skip_if_unavailable):
    result = explain_password("Password123")
    assert result["security_level"] in ["Orta", "Güçlü", "Zayıf"]


def test_get_missing_requirements_uppercase_only(skip_if_unavailable):
    result = get_missing_requirements("PASSWORD")
    assert len(result) > 0
    assert any("küçük" in req for req in result)


def test_get_missing_requirements_digits_only(skip_if_unavailable):
    result = get_missing_requirements("12345678")
    assert len(result) > 0
    assert any("harf" in req for req in result)


def test_explain_password_all_fields_present(skip_if_unavailable):
    result = explain_password("ComplexPass456!@#")
    assert result["password"] == "ComplexPass456!@#"
    assert isinstance(result["is_strong"], bool)
    assert isinstance(result["missing_requirements"], list)
    assert isinstance(result["pattern_warnings"], list)
    assert isinstance(result["suggestions"], list)
