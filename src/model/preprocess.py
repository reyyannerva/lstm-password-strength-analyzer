"""
Parola veri setini model eğitimine hazırlayan ön işleme modülü.
"""

import os
import sys


RAW_PATH = os.path.join("data", "raw")
PROCESSED_PATH = os.path.join("data", "processed", "clean_passwords.txt")
MIN_LEN = 4
MAX_LEN = 64


def find_raw_file():
    for fname in os.listdir(RAW_PATH):
        fpath = os.path.join(RAW_PATH, fname)
        if os.path.isfile(fpath):
            return fpath
    return None


def load_passwords(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()


def clean(lines):
    seen = set()
    result = []
    for line in lines:
        pw = line.strip()
        if not pw:
            continue
        if len(pw) < MIN_LEN or len(pw) > MAX_LEN:
            continue
        try:
            pw.encode("utf-8").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
        if pw in seen:
            continue
        seen.add(pw)
        result.append(pw)
    return result


def save(passwords, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(passwords))


def run():
    raw_file = find_raw_file()
    if raw_file is None:
        print(f"Hata: {RAW_PATH} klasöründe veri dosyası bulunamadı.")
        sys.exit(1)

    print(f"Kaynak dosya: {raw_file}")
    lines = load_passwords(raw_file)
    print(f"Toplam satır (ham): {len(lines)}")

    cleaned = clean(lines)
    print(f"Temizleme sonrası kayıt sayısı: {len(cleaned)}")
    print(f"Kaldırılan kayıt sayısı: {len(lines) - len(cleaned)}")

    save(cleaned, PROCESSED_PATH)
    print(f"Temizlenmiş veri kaydedildi: {PROCESSED_PATH}")


if __name__ == "__main__":
    run()

def analyze_dataset_quality(passwords):
    """
    Dataset quality statistics.
    """

    passwords = [str(p) for p in passwords if p]

    if not passwords:
        return {
            "count": 0,
            "avg_length": 0,
            "min_length": 0,
            "max_length": 0,
            "unique_ratio": 0,
        }

    unique_count = len(set(passwords))

    lengths = [len(p) for p in passwords]

    return {
        "count": len(passwords),
        "avg_length": sum(lengths) / len(lengths),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "unique_ratio": unique_count / len(passwords),
    }