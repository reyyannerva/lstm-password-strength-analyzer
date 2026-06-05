"""
Password explanation and improvement suggestion module.

This module provides user-friendly Turkish explanations for password strength.
It identifies missing security requirements, detects weak password patterns,
creates actionable improvement suggestions, and formats the result for API or
frontend usage.
"""

import string
from typing import Any, Dict, List

from src.security.patterns import detect_patterns


UPPERCASE_CHARS = set(string.ascii_uppercase)
LOWERCASE_CHARS = set(string.ascii_lowercase)
DIGIT_CHARS = set(string.digits)
SPECIAL_CHARS = set("!@#$%^&*()-_=+[]{}|;:,.<>?~`")


def _normalize_password(password: str) -> str:
    """
    Convert password input into a safe string value.
    """

    return str(password) if password is not None else ""


def get_missing_requirements(password: str) -> List[str]:
    """
    Identify missing security requirements in the password.
    """

    password = _normalize_password(password)
    missing: List[str] = []

    if len(password) < 8:
        missing.append("Parola en az 8 karakter olmalı")

    if not any(char in UPPERCASE_CHARS for char in password):
        missing.append("En az bir büyük harf (A-Z) bulunmalı")

    if not any(char in LOWERCASE_CHARS for char in password):
        missing.append("En az bir küçük harf (a-z) bulunmalı")

    if not any(char in DIGIT_CHARS for char in password):
        missing.append("En az bir rakam (0-9) bulunmalı")

    if not any(char in SPECIAL_CHARS for char in password):
        missing.append("En az bir özel karakter (!@#$%^&* vb.) bulunmalı")

    return missing


def get_pattern_warnings(password: str) -> List[str]:
    """
    Detect weak password patterns and return user-friendly warnings.
    """

    password = _normalize_password(password)
    detected_patterns = detect_patterns(password)
    warnings: List[str] = []

    pattern_to_message = {
        "tekrarlı karakter": "⚠️ Aynı karakterin ardı ardına tekrar etmesi parolayı zayıflatır.",
        "ardışık karakter": "⚠️ Ardışık karakterler parolayı tahmin edilebilir yapar.",
        "klavye deseni": "⚠️ Klavye dizileri (qwerty, asdf gibi) güvenli değildir.",
        "yaygın yıl": "⚠️ Yıl bilgisi içeren parolalar daha kolay tahmin edilebilir.",
        "yaygın kelime": "⚠️ Yaygın kelimeler parolayı zayıflatır.",
        "yalnızca rakamlardan": "⚠️ Yalnızca rakamlardan oluşan parola çok zayıftır.",
        "yalnızca harflerden": "⚠️ Yalnızca harflerden oluşan parola yeterince güvenli değildir.",
    }

    for pattern in detected_patterns:
        pattern_text = str(pattern).lower()
        matched = False

        for key, message in pattern_to_message.items():
            if key in pattern_text:
                warnings.append(message)
                matched = True
                break

        if not matched:
            warnings.append(f"⚠️ Zayıf parola deseni tespit edildi: {pattern}")

    return warnings


def get_improvement_suggestions(password: str) -> List[str]:
    """
    Generate actionable Turkish improvement suggestions.
    """

    password = _normalize_password(password)
    suggestions: List[str] = []

    missing_requirements = get_missing_requirements(password)
    pattern_warnings = get_pattern_warnings(password)

    if not password:
        return [
            "💡 Analiz için boş olmayan bir parola girin.",
            "💡 En az 8 karakterden oluşan, büyük harf, küçük harf, rakam ve özel karakter içeren bir parola kullanın.",
        ]

    if missing_requirements:
        suggestions.append("Eksik güvenlik kurallarını tamamlayın:")
        for requirement in missing_requirements:
            suggestions.append(f"  • {requirement}")

    if pattern_warnings:
        suggestions.append("Zayıf parola desenlerinden kaçının:")
        for warning in pattern_warnings:
            suggestions.append(f"  {warning}")

    if len(password) < 12:
        suggestions.append("💡 Daha güçlü bir parola için 12 veya daha fazla karakter kullanın.")

    if not any(char in SPECIAL_CHARS for char in password):
        suggestions.append("💡 Özel karakter eklemek parolanın güvenliğini artırır.")

    if password == password.lower() or password == password.upper():
        suggestions.append("💡 Büyük ve küçük harfleri birlikte kullanın.")

    if not any(char in DIGIT_CHARS for char in password):
        suggestions.append("💡 En az bir rakam ekleyin.")

    if not suggestions:
        suggestions.append("✅ Parola temel güvenlik gereksinimlerini karşılıyor.")

    return suggestions


def explain_password(password: str) -> Dict[str, Any]:
    """
    Generate comprehensive password explanation.

    Returns:
        JSON-compatible dictionary for API and frontend usage.
    """

    password = _normalize_password(password)

    missing_requirements = get_missing_requirements(password)
    pattern_warnings = get_pattern_warnings(password)
    suggestions = get_improvement_suggestions(password)

    if not password:
        security_level = "Zayıf"
        assessment = "Parola boş olamaz. Lütfen geçerli bir parola girin."
    elif len(missing_requirements) == 0 and len(pattern_warnings) == 0:
        security_level = "Güçlü"
        assessment = (
            "Bu parola iyi bir güvenlik düzeyine sahip. "
            "Temel güvenlik gereksinimlerini karşılıyor ve belirgin zayıf desen içermiyor."
        )
    elif len(missing_requirements) <= 2 and len(pattern_warnings) == 0:
        security_level = "Orta"
        assessment = (
            "Parola kullanılabilir seviyede, ancak bazı güvenlik kuralları eksik. "
            "Aşağıdaki öneriler uygulanarak güçlendirilebilir."
        )
    else:
        security_level = "Zayıf"
        assessment = (
            "Bu parola yeterince güvenli değil. "
            "Eksik kurallar veya zayıf desenler nedeniyle tahmin edilmesi kolay olabilir."
        )

    is_strong = (
        bool(password)
        and len(missing_requirements) == 0
        and len(pattern_warnings) == 0
    )

    return {
        "password": password,
        "security_level": security_level,
        "assessment": assessment,
        "missing_requirements": missing_requirements,
        "pattern_warnings": pattern_warnings,
        "suggestions": suggestions,
        "is_strong": is_strong,
        "summary": {
            "password_length": len(password),
            "missing_requirement_count": len(missing_requirements),
            "pattern_warning_count": len(pattern_warnings),
            "suggestion_count": len(suggestions),
        },
    }


def format_explanation(password: str) -> str:
    """
    Format password explanation as readable Turkish text.
    """

    explanation = explain_password(password)

    lines = [
        "📋 Parola Analiz Raporu",
        "=" * 40,
        f"🔐 Parola: {explanation['password']}",
        f"📊 Güvenlik Seviyesi: {explanation['security_level']}",
        "",
        "💬 Değerlendirme:",
        explanation["assessment"],
    ]

    if explanation["missing_requirements"]:
        lines.append("")
        lines.append("❌ Eksik Güvenlik Kuralları:")
        for requirement in explanation["missing_requirements"]:
            lines.append(f"  • {requirement}")

    if explanation["pattern_warnings"]:
        lines.append("")
        lines.append("⚠️ Zayıf Parola Desenleri:")
        for warning in explanation["pattern_warnings"]:
            lines.append(f"  {warning}")

    if explanation["suggestions"]:
        lines.append("")
        lines.append("✅ İyileştirme Önerileri:")
        for suggestion in explanation["suggestions"]:
            lines.append(f"  {suggestion}")

    return "\n".join(lines)