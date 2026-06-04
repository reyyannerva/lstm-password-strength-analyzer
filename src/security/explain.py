"""
Password explanation and improvement suggestion module.

Provides user-friendly explanations for why a password is weak or strong,
identifies missing security requirements, warns about weak patterns,
and suggests improvements in Turkish.
"""

import string
from typing import Any, Dict, List

from src.security.patterns import detect_patterns


UPPERCASE_CHARS = set(string.ascii_uppercase)
LOWERCASE_CHARS = set(string.ascii_lowercase)
DIGIT_CHARS = set(string.digits)
SPECIAL_CHARS = set("!@#$%^&*()-_=+[]{}|;:,.<>?~`")


def get_missing_requirements(password: str) -> List[str]:
    password = str(password or "")
    missing: List[str] = []

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
    warnings: List[str] = []
    patterns = detect_patterns(password)

    for pattern in patterns:
        lower = pattern.lower()
        if "tekrarlı karakter" in lower:
            warnings.append("Aynı karakterin tekrar etmesi parolayı güçsüzleştirir.")
        elif "ardışık karakter" in lower:
            warnings.append("Ardışık karakter dizileri tahmin edilebilir şifreler üretir.")
        elif "klavye deseni" in lower:
            warnings.append("Klavye dizileri (qwerty, asdf) güvenli değildir.")
        elif "yaygın yıl" in lower:
            warnings.append("Yaygın yıl kullanımı parolayı kolay tahmin edilebilir yapar.")
        elif "yaygın kelime" in lower:
            warnings.append("Yaygın kelime kullanımı parolayı zayıflatır.")
        elif "yalnızca rakamlardan" in lower:
            warnings.append("Sadece rakamlardan oluşan parola çok zayıftır.")
        elif "yalnızca harflerden" in lower:
            warnings.append("Sadece harflerden oluşan parola yeterince güvenli değildir.")
        else:
            warnings.append(pattern)

    return warnings


def get_improvement_suggestions(password: str) -> List[str]:
    suggestions: List[str] = []
    missing = get_missing_requirements(password)
    warnings = get_pattern_warnings(password)

    if missing:
        suggestions.append("Parolayı güçlendirmek için şu eksikleri tamamlayın:")
        for item in missing:
            suggestions.append(f"- {item}")

    if warnings:
        suggestions.append("Zayıf şifre desenlerini düzeltmek için şu adımları izleyin:")
        for item in warnings:
            suggestions.append(f"- {item}")

    if len(password) < 12:
        suggestions.append("Daha uzun bir parola seçerek güvenliği artırın (12+ karakter önerilir).")

    if not any(c in SPECIAL_CHARS for c in password):
        suggestions.append("Özel karakter ekleyin: !@#$%^&*()-_=+[]{}|;:,.<>?~`")

    if password == password.lower() or password == password.upper():
        suggestions.append("Büyük ve küçük harfleri karıştırarak parola çeşitliliğini artırın.")

    if not any(c.isdigit() for c in password):
        suggestions.append("Parolaya rakam ekleyin.")

    return suggestions


def explain_password(password: str) -> Dict[str, Any]:
    password = str(password or "")
    missing_requirements = get_missing_requirements(password)
    pattern_warnings = get_pattern_warnings(password)
    suggestions = get_improvement_suggestions(password)

    if not password:
        security_level = "Zayıf"
        assessment = "Parola boş olamaz. Lütfen geçerli bir parola girin."
    elif not missing_requirements and not pattern_warnings:
        security_level = "Güçlü"
        assessment = "Parola yeterli görünüyor. Güçlü bir parola seçmişsiniz."
    elif len(missing_requirements) <= 2 and not pattern_warnings:
        security_level = "Orta"
        assessment = "Parola bazı temel gereksinimleri karşılıyor, ancak iyileştirilebilir."
    else:
        security_level = "Zayıf"
        assessment = "Parola güvenli değil. Aşağıdaki önerileri takip edin."

    return {
        "password": password,
        "security_level": security_level,
        "assessment": assessment,
        "missing_requirements": missing_requirements,
        "pattern_warnings": pattern_warnings,
        "suggestions": suggestions,
        "is_strong": not missing_requirements and not pattern_warnings,
    }
