"""
Eğitim verisi üretme scripti.

Çeşitli güçlü/zayıf parola örnekleri üretir ve
data/processed/clean_passwords.txt dosyasına kaydeder.

Çalıştırmak için:
    python scripts/generate_training_data.py
"""

import os
import random
import string
from itertools import product

# ── Sabitler ─────────────────────────────────────────────────────────────────

OUTPUT_PATH = os.path.join("data", "processed", "clean_passwords.txt")
TEST_PATH   = os.path.join("data", "processed", "test_passwords.csv")
NCSC_PATH   = os.path.expanduser("~/Downloads/100k-most-used-passwords-NCSC (3).txt")
SEED = 42
random.seed(SEED)

KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]
COMMON_WORDS  = [
    "password", "parola", "admin", "qwerty", "login", "welcome",
    "letmein", "iloveyou", "monkey", "dragon", "master", "shadow",
    "sunshine", "princess", "abc", "pass", "test", "user", "guest",
    "root", "secure", "access", "enter",
]
COMMON_NAMES = [
    "ahmet", "mehmet", "ali", "ayse", "fatma", "zeynep",
    "john", "michael", "emma", "olivia", "liam", "noah",
    "burak", "emre", "selin", "cansu", "deniz", "mert",
]
YEARS = [str(y) for y in range(2000, 2027)]


# ── Zayıf parola üreticileri ──────────────────────────────────────────────────

def gen_sequential_numbers(n=800):
    passwords = []
    for length in range(4, 12):
        start = random.randint(0, 9)
        pw = "".join(str((start + i) % 10) for i in range(length))
        passwords.append(pw)
    for i in range(1, n):
        passwords.append("".join(str(d) for d in range(i % 10, (i % 10) + random.randint(4, 8))))
    return passwords[:n]


def gen_repeated_chars(n=400):
    chars = string.ascii_lowercase + string.digits
    return [c * random.randint(4, 10) for c in random.choices(chars, k=n)]


def gen_keyboard_patterns(n=500):
    passwords = []
    for row in KEYBOARD_ROWS:
        for length in range(4, len(row) + 1):
            passwords.append(row[:length])
            passwords.append(row[length - 4:length])
    for _ in range(n):
        row = random.choice(KEYBOARD_ROWS)
        start = random.randint(0, len(row) - 4)
        length = random.randint(4, min(8, len(row) - start))
        passwords.append(row[start:start + length])
    return passwords[:n]


def gen_word_number(n=1500):
    passwords = []
    for word in COMMON_WORDS:
        for year in random.sample(YEARS, 5):
            passwords.append(f"{word}{year}")
            passwords.append(f"{word.capitalize()}{year}")
        for suffix in ["1", "12", "123", "1234", "!", "!1", "123!"]:
            passwords.append(f"{word}{suffix}")
            passwords.append(f"{word.capitalize()}{suffix}")
    random.shuffle(passwords)
    return passwords[:n]


def gen_name_number(n=1000):
    passwords = []
    for name in COMMON_NAMES:
        for year in random.sample(YEARS, 4):
            passwords.append(f"{name}{year}")
            passwords.append(f"{name.capitalize()}{year}")
        for suffix in ["1", "123", "!", "2023", "2024"]:
            passwords.append(f"{name}{suffix}")
    random.shuffle(passwords)
    return passwords[:n]


def gen_only_digits(n=600):
    passwords = []
    for length in range(4, 10):
        for _ in range(n // 6):
            passwords.append("".join(random.choices(string.digits, k=length)))
    return passwords[:n]


def gen_only_letters(n=500):
    return ["".join(random.choices(string.ascii_lowercase, k=random.randint(4, 9))) for _ in range(n)]


def gen_common_words_only(n=400):
    passwords = []
    for word in COMMON_WORDS:
        passwords.append(word)
        passwords.append(word.upper())
        passwords.append(word.capitalize())
        for w2 in COMMON_WORDS[:5]:
            passwords.append(f"{word}{w2}")
    random.shuffle(passwords)
    return passwords[:n]


# ── Orta güç parola üreticileri ───────────────────────────────────────────────

def gen_medium_passwords(n=2000):
    passwords = []
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    specials = "!@#$%"
    for _ in range(n):
        length = random.randint(8, 11)
        groups = random.sample([upper, lower, digits], k=random.randint(2, 3))
        pool = "".join(groups)
        pw = "".join(random.choices(pool, k=length))
        passwords.append(pw)
    return passwords


# ── Güçlü parola üreticileri ──────────────────────────────────────────────────

def gen_strong_passwords(n=2000):
    specials = "!@#$%^&*()-_=+"
    passwords = []
    for _ in range(n):
        length = random.randint(12, 20)
        pool = string.ascii_letters + string.digits + specials
        while True:
            pw = "".join(random.choices(pool, k=length))
            has_up  = any(c in string.ascii_uppercase for c in pw)
            has_lo  = any(c in string.ascii_lowercase for c in pw)
            has_di  = any(c in string.digits for c in pw)
            has_sp  = any(c in specials for c in pw)
            if has_up and has_lo and has_di and has_sp:
                passwords.append(pw)
                break
    return passwords


# ── Ana fonksiyon ─────────────────────────────────────────────────────────────

def _load_ncsc(path: str) -> list:
    """NCSC gerçek dünya parola listesini yükler."""
    if not os.path.exists(path):
        print(f"  [UYARI] NCSC dosyası bulunamadı: {path}")
        return []
    passwords = []
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            pw = line.strip()
            if pw and 4 <= len(pw) <= 64:
                passwords.append(pw)
    return passwords


def generate_and_save():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    print("Parola üretiliyor...")

    # Sentetik zayıf parolalar
    synthetic_weak = (
        gen_sequential_numbers(800)
        + gen_repeated_chars(400)
        + gen_keyboard_patterns(500)
        + gen_word_number(1500)
        + gen_name_number(1000)
        + gen_only_digits(600)
        + gen_only_letters(500)
        + gen_common_words_only(400)
    )

    # NCSC gerçek dünya zayıf parolaları
    ncsc_passwords = _load_ncsc(NCSC_PATH)
    if ncsc_passwords:
        print(f"  NCSC dosyasından {len(ncsc_passwords)} parola yüklendi.")
    else:
        print("  NCSC verisi olmadan devam ediliyor (yalnızca sentetik).")

    # LSTM sadece zayıf parolaları öğrenir — güçlü parolalar yüksek perplexity verir
    all_passwords = synthetic_weak + ncsc_passwords
    random.shuffle(all_passwords)

    # Tekrarları kaldır, uzunluk filtrele
    seen = set()
    clean = []
    for pw in all_passwords:
        pw = pw.strip()
        if pw and 4 <= len(pw) <= 64 and pw not in seen:
            seen.add(pw)
            clean.append(pw)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(clean))

    print(f"Toplam {len(clean)} parola kaydedildi → {OUTPUT_PATH}")

    # Test CSV'si (etiketli, F1 hesaplamak için)
    _save_test_csv()


def _save_test_csv():
    """
    Etiketli test seti — etiketler HybridRiskScorer tarafından belirlenir.
    Bu yaklaşım kural tabanlı F1'i tutarlı yapar; LSTM onu geçmeye çalışır.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from src.security.risk_scorer import HybridRiskScorer

    scorer = HybridRiskScorer(rule_weight=1.0, lstm_weight=0.0)

    # Her sınıftan çeşitli parolalar (scorer etiketler)
    candidates = [
        # çok zayıf
        "123456", "password", "qwerty", "111111", "abc123",
        "123456789", "12345", "aaaaaa", "000000", "iloveyou",
        "admin", "letmein", "monkey", "1234", "parola",
        "123", "test", "root", "login", "welcome",
        "aaa", "qqq", "111", "asdf", "qwer",
        "aaaaaaaa", "11111111", "00000000", "abcdef", "123321",
        "654321", "888888", "1234567", "zxcvbn", "qazwsx",
        # zayıf
        "password1", "admin2023", "john1990",
        "dragon123", "master99", "monkey123",
        "ahmet2023", "mehmet99", "ali12345", "fatma123",
        "summer23", "winter23", "apple123", "samsung1",
        "google12", "gaming123", "player12", "gamer999",
        "hello123", "test1234", "user1234", "guest2023",
        "burak2024", "emre1990", "selin2023", "deniz111",
        "ninja2023", "soccer123", "baseball1", "football1",
        # orta
        "Reyyan2026", "Emre2023A", "Selin2024B",
        "MyPass123", "User2024!", "SecPass9!", "Pass@word1",
        "Ahmet@123", "Mehmet123!", "Fatma@456",
        "Summer@23", "Winter#24", "Music@123",
        "Deniz@456", "Mert2023!", "Cansu@12",
        "Python123!", "Django2024", "React2023!",
        "Home@1234", "Work2024!", "School123@",
        "Bl@ck123", "Wh1te45!", "R3dPass1!",
        "MyDog@123", "MyCat45!", "Mobile2024",
        # güçlü
        "Xk9#mP2!vQ", "T7$rLn@w3Y", "hJ4Qm9pKs!",
        "2@BvxZ5#Lq", "N8jR@3wKpY", "F5tGm@2Xs!",
        "P9vKn5Tz!@", "M3xRb7Nq!@", "W6fTp4Jy!@",
        "SecureP@ss12", "Str0ng!P@ss", "C0mpl3x!ty",
        "MyS3cur3!1", "N3wP@ss99!", "Updat3d@11",
        "Comp!ex99@", "M1xed@Case!", "Numb3rs#!9",
        "R@ndom99X!", "M!xed2024!", "Str0ng1X!@",
        "Ankara2024!", "Istanbul@7!", "Izmir2024#",
        "L0ng3rPa$$1", "B3tt3rP@ss2", "Gr3at!P@ss3",
        # çok güçlü
        "Xk9#mP2!vQ3rL", "T7rLn@w3Yz5K!", "hJ4Qm9pKs2B!@",
        "2BvxZ5LqN8m!@#", "N8jR3wKpY6t!@$", "F5tGm2XsR9v!@#",
        "P9vKn5TzM2b!@#$", "M3xRb7NqW4k!@#", "W6fTp4JyX8n!@#",
        "MyV3ryStr0ng!P@ss24", "UltraS3cur3#Pass99",
        "C0mpl3xP@ssw0rd!2", "L0ng@ndStr0ng24!",
        "X9mK3bNpR7vT2!@#", "Q8wE3rT9yU6i!@#",
        "MyS3cureLong!P@ss24", "Ultra#Str0ng2024!!",
        "AbCdEfGh1234!@#$", "ZxYwVu5678!@#$Nm",
        "M!x3dC@s3Num5Sp!@", "C0mpl3x!ty9@Pass#",
        "9Xk3mPb7vNqZ!@#$", "5Lm2Qr9nKwT8!@#$",
        "3Rv8xB4pYnm7!@#$", "7Wz1kN6qPm3!@#$Y",
        "SecureAndLong2024!@", "StrongAndComplex99!#",
        "VerySecurePass2024!@", "MuchBetterPass2024!#",
        "Amazing@Strength123!$", "ExcellentComplexity9!",
        "SynTh3ticP@ssw0rd#X!", "G3n3r@tedStr0ng99X!",
    ]

    rows = [("password", "true_label")]
    for pw in candidates:
        result = scorer.score(pw)
        rows.append((pw, result.security_level))

    with open(TEST_PATH, "w", encoding="utf-8") as f:
        for pw, label in rows:
            f.write(f"{pw},{label}\n")

    # Dağılım özeti
    from collections import Counter
    dist = Counter(label for _, label in rows[1:])
    print(f"Test seti kaydedildi → {TEST_PATH} ({len(rows)-1} parola)")
    for lvl in ["Çok Zayıf", "Zayıf", "Orta", "Güçlü", "Çok Güçlü"]:
        print(f"  {lvl:<14}: {dist.get(lvl, 0)}")


if __name__ == "__main__":
    generate_and_save()
