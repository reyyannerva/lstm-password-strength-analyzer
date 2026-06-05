from pathlib import Path
import re

# -------------------------
# 1) src/model/dataset.py fix
# -------------------------
dataset_path = Path("src/model/dataset.py")
text = dataset_path.read_text(encoding="utf-8")

# Yanlış PowerShell patch kalıntısını düzelt
text = text.replace("self.seq_len = max_length if max_length is not $null else seq_len",
                    "self.seq_len = max_length if max_length is not None else seq_len")

# __init__ max_length kabul etmiyorsa ekle
text = re.sub(
    r"def __init__\((self,\s*passwords,\s*tokenizer,\s*seq_len\s*=\s*[^,\)\n]+)\):",
    r"def __init__(\1, max_length=None):",
    text
)

# Eğer signature farklıysa daha genel yedek düzeltme
text = re.sub(
    r"def __init__\((self,\s*passwords,\s*tokenizer,\s*seq_len\s*:\s*int\s*=\s*[^,\)\n]+)\):",
    r"def __init__(\1, max_length=None):",
    text
)

# self.seq_len = seq_len satırını alias uyumlu yap
text = re.sub(
    r"self\.seq_len\s*=\s*seq_len",
    "self.seq_len = max_length if max_length is not None else seq_len",
    text
)

dataset_path.write_text(text, encoding="utf-8")


# -------------------------
# 2) src/security/patterns.py fix
# -------------------------
patterns_path = Path("src/security/patterns.py")
patterns_path.write_text(r'''"""
Weak password pattern detection module.
"""

import re
from typing import Dict, List


KEYBOARD_ROWS = [
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1234567890",
    "abcdefghijklmnopqrstuvwxyz",
]

COMMON_WORDS = [
    "password",
    "parola",
    "admin",
    "qwerty",
    "login",
    "user",
    "welcome",
    "test",
    "pass",
    "root",
    "letmein",
    "iloveyou",
]


def _safe_password(password) -> str:
    if password is None:
        return ""
    return str(password)


def detect_repeated_chars(password):
    password = _safe_password(password)
    if re.search(r"(.)\1{2,}", password):
        return "tekrarlı karakter tespit edildi"
    return None


def detect_sequential_chars(password):
    password = _safe_password(password).lower()
    for i in range(len(password) - 2):
        trio = password[i:i + 3]
        if len(trio) == 3 and ord(trio[1]) - ord(trio[0]) == 1 and ord(trio[2]) - ord(trio[1]) == 1:
            return "ardışık karakter tespit edildi"
    return None


def detect_keyboard_pattern(password):
    password = _safe_password(password).lower()
    for row in KEYBOARD_ROWS:
        for i in range(len(row) - 2):
            chunk = row[i:i + 3]
            if chunk in password:
                return "klavye deseni tespit edildi"
    return None


def detect_common_year(password):
    password = _safe_password(password)
    if re.search(r"(19|20)\d{2}", password):
        return "yaygın yıl tespit edildi"
    return None


def detect_common_word(password):
    password = _safe_password(password).lower()
    for word in COMMON_WORDS:
        if word in password:
            return "yaygın kelime tespit edildi"
    return None


def detect_only_digits(password):
    password = _safe_password(password)
    if password and password.isdigit():
        return "yalnızca rakamlardan oluşuyor"
    return None


def detect_only_letters(password):
    password = _safe_password(password)
    if password and password.isalpha():
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


def detect_patterns(password) -> List[str]:
    password = _safe_password(password)
    found = []
    for detector in _DETECTORS:
        result = detector(password)
        if result:
            found.append(result)
    return found


def detect_pattern_details(password) -> List[Dict[str, str]]:
    details = []
    for pattern in detect_patterns(password):
        severity = "medium"
        if (
            "yalnızca" in pattern
            or "yaygın kelime" in pattern
            or "klavye deseni" in pattern
        ):
            severity = "high"

        details.append({
            "pattern": pattern,
            "message": pattern,
            "severity": severity,
        })

    return details
''', encoding="utf-8")


# -------------------------
# 3) src/security/rules.py empty password fix
# -------------------------
rules_path = Path("src/security/rules.py")
text = rules_path.read_text(encoding="utf-8")

# analyze_rules fonksiyonunun başına boş parola guard ekle
if "def analyze_rules" in text and "FINAL_EMPTY_PASSWORD_GUARD" not in text:
    text = re.sub(
        r"(def analyze_rules\([^\)]*\):\n)",
        r'''\1    # FINAL_EMPTY_PASSWORD_GUARD
    if password is None:
        password = ""
    if password == "":
        return {
            "password": "",
            "rules": [],
            "passed_count": 0,
            "failed_count": 0,
            "total_count": 0,
        }

''',
        text,
        count=1
    )

rules_path.write_text(text, encoding="utf-8")


# -------------------------
# 4) frontend/script.js /explain garanti
# -------------------------
script_path = Path("frontend/script.js")
if script_path.exists():
    text = script_path.read_text(encoding="utf-8")
    if "/explain" not in text:
        text += r'''

async function explainPassword(password) {
  const response = await fetch(`${API_BASE}/explain`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ password })
  });

  if (!response.ok) {
    throw new Error("Explain API request failed");
  }

  return await response.json();
}
'''
        script_path.write_text(text, encoding="utf-8")

print("Patch tamamlandı.")
