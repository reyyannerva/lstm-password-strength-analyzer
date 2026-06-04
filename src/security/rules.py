"""
Rule-based password security analyzer module.

Analyzes passwords against predefined security rules.
Returns comprehensive rule-based scoring and assessment.
"""

import string
import re
from typing import Dict, List, Any


def check_length(password: str, min_length: int = 8, max_length: int = 128) -> Dict[str, Any]:
    """
    Check password length requirements.
    
    Args:
        password: Password to check.
        min_length: Minimum required length.
        max_length: Maximum allowed length.
    
    Returns:
        {"passed": bool, "details": str}
    """
    password = str(password) if password else ""
    length = len(password)
    
    if length < min_length:
        return {
            "passed": False,
            "details": f"Parola en az {min_length} karakter olmalı (mevcut: {length})"
        }
    
    if length > max_length:
        return {
            "passed": False,
            "details": f"Parola en fazla {max_length} karakter olmalı (mevcut: {length})"
        }
    
    return {
        "passed": True,
        "details": f"Parola uzunluğu uygun ({length} karakter)"
    }


def check_uppercase(password: str) -> Dict[str, Any]:
    """
    Check if password contains uppercase letters.
    
    Returns:
        {"passed": bool, "details": str}
    """
    password = str(password) if password else ""
    
    if not re.search(r"[A-Z]", password):
        return {
            "passed": False,
            "details": "Parola en az bir büyük harf (A-Z) içermelidir"
        }
    
    return {
        "passed": True,
        "details": "Parola büyük harf içeriyor"
    }


def check_lowercase(password: str) -> Dict[str, Any]:
    """
    Check if password contains lowercase letters.
    
    Returns:
        {"passed": bool, "details": str}
    """
    password = str(password) if password else ""
    
    if not re.search(r"[a-z]", password):
        return {
            "passed": False,
            "details": "Parola en az bir küçük harf (a-z) içermelidir"
        }
    
    return {
        "passed": True,
        "details": "Parola küçük harf içeriyor"
    }


def check_digits(password: str) -> Dict[str, Any]:
    """
    Check if password contains digits.
    
    Returns:
        {"passed": bool, "details": str}
    """
    password = str(password) if password else ""
    
    if not re.search(r"\d", password):
        return {
            "passed": False,
            "details": "Parola en az bir rakam (0-9) içermelidir"
        }
    
    return {
        "passed": True,
        "details": "Parola rakam içeriyor"
    }


def check_special_chars(password: str) -> Dict[str, Any]:
    """
    Check if password contains special characters.
    
    Allowed special characters: !@#$%^&*()-_=+[]{}|;:,.<>?~`
    
    Returns:
        {"passed": bool, "details": str}
    """
    password = str(password) if password else ""
    special_chars = r"[!@#$%^&*()\-_=+\[\]{}|;:,.<>?~`]"
    
    if not re.search(special_chars, password):
        return {
            "passed": False,
            "details": "Parola en az bir özel karakter içermelidir (!@#$%^&* vb.)"
        }
    
    return {
        "passed": True,
        "details": "Parola özel karakter içeriyor"
    }


def analyze_rules(password: str) -> Dict[str, Any]:
    """
    Comprehensive rule-based password analysis.
    
    Combines all rule checks and produces detailed report.
    
    Args:
        password: Password to analyze.
    
    Returns:
        Dictionary with:
        - password: Input password
        - checks: Dict of all check results
        - passed_count: Number of passed checks
        - total_checks: Total number of checks
        - score: Percentage score (0-100)
        - all_passed: Boolean indicating if all checks passed
        - details: List of check details
    """
    password = str(password) if password is not None else ""
    
    checks = {
        "length": check_length(password),
        "uppercase": check_uppercase(password),
        "lowercase": check_lowercase(password),
        "digits": check_digits(password),
        "special_chars": check_special_chars(password),
    }
    
    passed_checks = sum(1 for check in checks.values() if check["passed"])
    total_checks = len(checks)
    score = (passed_checks / total_checks) * 100
    
    details = [
        f"✓ {check['details']}" if check["passed"] else f"✗ {check['details']}"
        for check in checks.values()
    ]
    
    return {
        "password": password,
        "checks": checks,
        "passed_count": passed_checks,
        "total_checks": total_checks,
        "score": round(score, 2),
        "all_passed": passed_checks == total_checks,
        "details": details,
    }
