"""
Password explanation and improvement suggestion module.

Provides user-friendly explanations for why a password is weak or strong,
identifies missing security requirements, warns about weak patterns,
and suggests improvements in plain Turkish.
"""

import string
from typing import Dict, Any, List

from src.security.patterns import detect_patterns


# Character sets
UPPERCASE_CHARS = set(string.ascii_uppercase)
LOWERCASE_CHARS = set(string.ascii_lowercase)
DIGIT_CHARS = set(string.digits)
SPECIAL_CHARS = set("!@#$%^&*()-_=+[]{}|;:,.<>?~`")


def get_missing_requirements(password: str) -> List[str]:
    """
    Identify which security requirements are missing from the password.

    Returns:
        List of human-friendly descriptions of missing requirements.
    """
    missing = []

    password = str(password) if password else ""

    if len(password) < 8:
        missing.append("Parola en az 8 karakter olmalı")

    if not any(c in UPPERCASE_CHARS for c in password):
        missing.append("En az bir büyük harf (A-Z) bulunmalı")

    if not any(c in LOWERCASE_CHARS for c in password):
        missing.append("En az bir küçük harf (a-z) bulunmalı")

    if not any(c in DIGIT_CHARS for c in password):
        missing.append("En az bir rakam (0-9) bulunmalı")

    if not any(c in SPECIAL_CHARS for c in password):
        missing.append("En az bir özel karakter (!@#$%^&* vb.) bulunmalı")

    return missing


def get_pattern_warnings(password: str) -> List[str]:
    """
    Detect weak patterns in password and return user-friendly warnings.

    Returns:
        List of warnings about detected weak patterns.
    """
    patterns = detect_patterns(password)
    warnings = []

    pattern_to_message = {
        "tekrarlı karakter": "⚠️ Aynı karakterin ardı ardına gelmesi parolayı zayıflatıyor (örn. 'aaa', '111')",
        "ardışık karakter": "⚠️ Ardışık karakterler (abc, 123 gibi) parolayı tahmin edilebilir yapıyor",
        "klavye deseni": "⚠️ Klavyede yan yana karakterler (qwerty, asdf gibi) güvenli değil",
        "yaygın yıl": "⚠️ Yıl bilgisi içerişi parolayı kolay kırılabilir yapıyor",
        "yaygın kelime": "⚠️ Bilinen kelimeler parolayı güvenli değil kılıyor",
        "yalnızca rakamlardan": "⚠️ Yalnızca rakamlardan oluşan parola çok zayıf",
        "yalnızca harflerden": "⚠️ Yalnızca harflerden oluşan parola yeterince güvenli değil",
    }

    for pattern in patterns:
        for key, message in pattern_to_message.items():
            if key in pattern.lower():
                warnings.append(message)
                break

    return warnings


def get_improvement_suggestions(password: str) -> List[str]:
    """
    Generate user-friendly improvement suggestions based on password analysis.

    Returns:
        List of actionable suggestions to strengthen the password.
    """
    suggestions = []
    missing = get_missing_requirements(password)

    if len(missing) > 0:
        suggestions.append("Eksik güvenlik kuralları:")
        for req in missing:
            suggestions.append(f"  • {req}")

    patterns = get_pattern_warnings(password)
    if patterns:
        suggestions.append("\nZayıf parola desenleri:")
        for warning in patterns:
            suggestions.append(f"  {warning}")

    if len(password) < 12:
        suggestions.append("\n💡 Daha uzun bir parola seçerseniz (12+ karakter) güvenliği artar")

    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?~`" for c in password):
        suggestions.append("💡 Özel karakterler eklemek parolayı daha güvenli hale getirir")

    if password == password.lower() or password == password.upper():
        suggestions.append("💡 Hem büyük hem küçük harfler karıştırarak parola güvenliğini artırın")

    if not any(c.isdigit() for c in password):
        suggestions.append("💡 Rakamlı içerik parolayı daha güvenli hale getirir")

    return suggestions


def explain_password(password: str) -> Dict[str, Any]:
    """
    Generate comprehensive explanation and suggestions for a password.

    Returns:
        JSON-compatible dictionary with explanation, missing requirements,
        pattern warnings, suggestions, and overall assessment.
    """
    password = str(password) if password is not None else ""

    missing_requirements = get_missing_requirements(password)
    pattern_warnings = get_pattern_warnings(password)
    suggestions = get_improvement_suggestions(password)

    # Calculate security level
    if len(missing_requirements) == 0 and len(pattern_warnings) == 0:
        security_level = "Güçlü"
        assessment = "Bu parola iyi bir güvenlik düzeyine sahip. Şu an için herhangi bir iyileştirme önerisi yok."
    elif len(missing_requirements) <= 2 and len(pattern_warnings) == 0:
        security_level = "Orta"
        assessment = "Parola kullanılabilir, ancak bazı güvenlik kuralları eksik. Aşağıdaki önerileri göz önünde bulundurun."
    else:
        security_level = "Zayıf"
        assessment = "Bu parola yeterince güvenli değil. Aşağıdaki önerileri uygulayarak parolayı güçlendirebilirsiniz."

    return {
        "password": password,
        "security_level": security_level,
        "assessment": assessment,
        "missing_requirements": missing_requirements,
        "pattern_warnings": pattern_warnings,
        "suggestions": suggestions,
        "is_strong": len(missing_requirements) == 0 and len(pattern_warnings) == 0,
    }


def format_explanation(password: str) -> str:
    """
    Format password explanation as readable Turkish text.

    Returns:
        Formatted explanation string with structure and emojis.
    """
    explanation = explain_password(password)
    
    lines = [
        f"📋 Parola Analiz Raporu",
        f"=" * 40,
        f"🔐 Parola: {explanation['password']}",
        f"📊 Güvenlik Seviyesi: {explanation['security_level']}",
        f"",
        f"💬 Değerlendirme:",
        f"{explanation['assessment']}",
    ]
    
    if explanation['missing_requirements']:
        lines.append("")
        lines.append("❌ Eksik Güvenlik Kuralları:")
        for req in explanation['missing_requirements']:
            lines.append(f"  • {req}")
    
    if explanation['pattern_warnings']:
        lines.append("")
        lines.append("⚠️ Zayıf Parola Desenleri:")
        for warning in explanation['pattern_warnings']:
            lines.append(f"  {warning}")
    
    if explanation['suggestions']:
        lines.append("")
        lines.append("✅ İyileştirme Önerileri:")
        for suggestion in explanation['suggestions']:
            lines.append(f"  {suggestion}")
    
    return "\n".join(lines)
