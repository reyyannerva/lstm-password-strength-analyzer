"""
LSTM Parola Güvenlik Modeli — Eğitim ve F1 Değerlendirme Pipeline

Çalıştırmak için:
    python scripts/train_and_evaluate.py

Adımlar:
  1. Veri yükle  (data/processed/clean_passwords.txt)
  2. Tokenizer fit et
  3. LSTM dil modelini eğit
  4. Kural tabanlı F1 değerlendir
  5. LSTM perplexity tabanlı F1 değerlendir
  6. Eğitim grafiklerini kaydet (experiments/)
  7. Modeli kaydet (experiments/lstm_model.pt)
"""

import os
import sys
import csv
import json
import math
import random

# Proje kök dizini PYTHONPATH'a ekle
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import torch

from src.model.preprocess  import load_passwords, clean as clean_passwords
from src.model.tokenizer   import CharTokenizer
from src.model.dataset     import create_dataloader
from src.model.lstm_model  import build_model
from src.model.train       import train, plot_training_history
from src.model.evaluate    import (
    evaluate,
    evaluate_classification,
    evaluate_rule_based_f1,
    calibrate_thresholds,
)

# ── Konfigürasyon ─────────────────────────────────────────────────────────────

CFG = {
    "data_path":        "data/processed/clean_passwords.txt",
    "test_csv":         "data/processed/test_passwords.csv",
    "checkpoint_path":  "experiments/lstm_model.pt",
    "log_path":         "experiments/training_log.json",
    "output_dir":       "experiments",
    "embed_dim":        64,
    "hidden_dim":       256,
    "num_layers":       2,
    "dropout":          0.3,
    "batch_size":       128,
    "seq_len":          64,
    "epochs":           20,
    "lr":               1e-3,
    "weight_decay":     1e-5,
    "grad_clip":        5.0,
    "early_stop":       5,
    "val_split":        0.1,
    "seed":             42,
}

random.seed(CFG["seed"])
torch.manual_seed(CFG["seed"])


def _load_test_csv(path: str):
    passwords, labels = [], []
    if not os.path.exists(path):
        print(f"[UYARI] Test CSV bulunamadı: {path}")
        return passwords, labels
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # başlık satırını atla
        for row in reader:
            if len(row) >= 2:
                passwords.append(row[0])
                labels.append(row[1])
    return passwords, labels


def _print_f1_report(title: str, result: dict) -> None:
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")
    print(f"  Macro F1       : {result['f1_macro']:.4f}")
    print(f"  Weighted F1    : {result['f1_weighted']:.4f}")
    print(f"  Macro Precision: {result['precision_macro']:.4f}")
    print(f"  Macro Recall   : {result['recall_macro']:.4f}")
    print(f"  Accuracy       : {result['accuracy']:.4f}")
    print(f"\n  Sınıf bazlı metrikler:")
    print(f"  {'Sınıf':<14} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print(f"  {'-'*46}")
    for label, m in result["per_class"].items():
        print(f"  {label:<14} {m['precision']:>10.4f} {m['recall']:>10.4f} {m['f1']:>10.4f}")
    print(f"\n  Karışıklık Matrisi ({' | '.join(result['confusion_labels'])}):")
    for i, row in enumerate(result["confusion_matrix"]):
        label = result["confusion_labels"][i]
        print(f"  {label:<14}: {row}")
    print(f"{'='*55}")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Cihaz: {device}")

    # ── 1. Test seti F1 (kural tabanlı, LSTM eğitimi gerekmez) ───────────────
    test_passwords, test_labels = _load_test_csv(CFG["test_csv"])

    if test_passwords:
        print("\n[1/5] Kural tabanlı skor F1 hesaplanıyor...")
        rule_result = evaluate_rule_based_f1(test_passwords, test_labels)
        _print_f1_report("KURAL TABANLI SKOR — F1 RAPORU", rule_result)

        with open(os.path.join(CFG["output_dir"], "f1_rule_based.json"), "w") as f:
            json.dump(rule_result, f, ensure_ascii=False, indent=2)
    else:
        print("[UYARI] Test CSV yüklenemedi, kural tabanlı F1 atlandı.")

    # ── 2. Eğitim verisi yükle ────────────────────────────────────────────────
    if not os.path.exists(CFG["data_path"]):
        print(f"\n[HATA] Eğitim verisi bulunamadı: {CFG['data_path']}")
        print("  Önce şunu çalıştır: python scripts/generate_training_data.py")
        return

    print(f"\n[2/5] Eğitim verisi yükleniyor: {CFG['data_path']}")
    raw = load_passwords(CFG["data_path"])
    passwords = clean_passwords(raw)
    print(f"  {len(passwords)} parola yüklendi.")

    if len(passwords) < 100:
        print("[HATA] Yetersiz veri (min. 100 parola gerekli).")
        return

    # ── 3. Tokenizer ──────────────────────────────────────────────────────────
    print("\n[3/5] Tokenizer fit ediliyor...")
    tokenizer = CharTokenizer()
    tokenizer.fit(passwords)
    print(f"  Vocab boyutu: {tokenizer.vocab_size}")

    # ── 4. Train / Validation split ───────────────────────────────────────────
    random.shuffle(passwords)
    val_size  = max(1, int(len(passwords) * CFG["val_split"]))
    val_pw    = passwords[:val_size]
    train_pw  = passwords[val_size:]

    train_loader = create_dataloader(train_pw, tokenizer, CFG["batch_size"], CFG["seq_len"], shuffle=True)
    val_loader   = create_dataloader(val_pw,   tokenizer, CFG["batch_size"], CFG["seq_len"], shuffle=False)
    print(f"  Eğitim: {len(train_pw)} | Doğrulama: {len(val_pw)}")

    # ── 5. Model ──────────────────────────────────────────────────────────────
    model = build_model(
        vocab_size  = tokenizer.vocab_size,
        embed_dim   = CFG["embed_dim"],
        hidden_dim  = CFG["hidden_dim"],
        num_layers  = CFG["num_layers"],
        dropout     = CFG["dropout"],
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"\n  Model parametreleri: {total_params:,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=CFG["lr"], weight_decay=CFG["weight_decay"])

    # ── 6. Eğitim ─────────────────────────────────────────────────────────────
    print(f"\n[4/5] Eğitim başlıyor ({CFG['epochs']} epoch)...")
    history = train(
        model                  = model,
        train_loader           = train_loader,
        val_loader             = val_loader,
        epochs                 = CFG["epochs"],
        optimizer              = optimizer,
        device                 = device,
        grad_clip              = CFG["grad_clip"],
        checkpoint_path        = CFG["checkpoint_path"],
        log_path               = CFG["log_path"],
        early_stopping_patience= CFG["early_stop"],
    )

    completed_epochs = len(history["train_loss"])
    best_val = min((v for v in history["val_loss"] if v is not None), default=float("inf"))
    best_ppl  = math.exp(best_val) if best_val < 700 else float("inf")
    print(f"\n  Tamamlanan epoch: {completed_epochs}")
    print(f"  En iyi val loss : {best_val:.4f}  (perplexity: {best_ppl:.2f})")

    # ── 7. Grafikler ──────────────────────────────────────────────────────────
    plot_training_history(history, CFG["output_dir"])
    print(f"  Grafikler kaydedildi → {CFG['output_dir']}/")

    # ── 8. LSTM tabanlı F1 ────────────────────────────────────────────────────
    if test_passwords:
        print("\n[5/5] LSTM perplexity tabanlı F1 hesaplanıyor...")

        # Eşikleri test etiketlerinden kalibre et
        print("  Perplexity eşikleri kalibre ediliyor...")
        cal_thresholds = calibrate_thresholds(
            model          = model,
            tokenizer      = tokenizer,
            cal_passwords  = test_passwords,
            cal_labels     = test_labels,
            device         = device,
        )
        print("  Kalibre edilmiş eşikler:")
        for t, lbl in cal_thresholds:
            print(f"    < {t:.2f} → {lbl}")
        print(f"    >= {cal_thresholds[-1][0]:.2f} → Çok Güçlü")

        lstm_result = evaluate_classification(
            model          = model,
            tokenizer      = tokenizer,
            test_passwords = test_passwords,
            true_labels    = test_labels,
            device         = device,
            thresholds     = cal_thresholds,
        )
        _print_f1_report("LSTM PERPLEXITY TABANLI — F1 RAPORU", lstm_result)

        with open(os.path.join(CFG["output_dir"], "f1_lstm.json"), "w") as f:
            json.dump(lstm_result, f, ensure_ascii=False, indent=2)

        # Karşılaştırma özeti
        if test_passwords:
            print(f"\n{'='*55}")
            print("  KARŞILAŞTIRMA ÖZETİ")
            print(f"{'='*55}")
            print(f"  {'Metrik':<22} {'Kural Tabanlı':>14} {'LSTM':>10}")
            print(f"  {'-'*48}")
            for key in ("f1_macro", "f1_weighted", "accuracy"):
                r = rule_result[key]
                l = lstm_result[key]
                diff = l - r
                sign = "+" if diff >= 0 else ""
                print(f"  {key:<22} {r:>14.4f} {l:>10.4f}  ({sign}{diff:.4f})")
            print(f"{'='*55}")
    else:
        print("[UYARI] Test CSV bulunamadı, LSTM F1 atlandı.")

    print("\nPipeline tamamlandı.")


if __name__ == "__main__":
    main()
