"""
LSTM model değerlendirme modülü.

Hesaplanan metrikler:
- loss (cross-entropy)
- perplexity
- token-level accuracy
- password-level classification F1 / precision / recall (sınıflandırma değerlendirmesi için)
"""

import math
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn


# ── Dil modeli değerlendirmesi ────────────────────────────────────────────────

def evaluate(model, data_loader, device, pad_token_id: int = 0) -> Dict:
    """Token-level loss, perplexity ve accuracy hesaplar."""
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=pad_token_id)

    total_loss = 0.0
    total_tokens = 0
    correct_tokens = 0

    with torch.no_grad():
        for inputs, targets in data_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            batch_size = inputs.size(0)
            hidden = model.init_hidden(batch_size, device)
            logits, _ = model(inputs, hidden)

            vocab_size = logits.size(-1)
            flat_logits  = logits.view(-1, vocab_size)
            flat_targets = targets.view(-1)

            loss = criterion(flat_logits, flat_targets)

            non_pad_mask  = flat_targets != pad_token_id
            non_pad_count = non_pad_mask.sum().item()
            if non_pad_count == 0:
                continue

            predictions = flat_logits.argmax(dim=-1)
            correct_tokens += (
                predictions[non_pad_mask] == flat_targets[non_pad_mask]
            ).sum().item()

            total_loss   += loss.item() * non_pad_count
            total_tokens += non_pad_count

    avg_loss   = total_loss / total_tokens if total_tokens > 0 else float("inf")
    perplexity = math.exp(avg_loss) if avg_loss < 700 else float("inf")
    accuracy   = correct_tokens / total_tokens if total_tokens > 0 else 0.0

    return {"loss": avg_loss, "perplexity": perplexity, "accuracy": accuracy}


# ── Perplexity → Güvenlik seviyesi dönüşümü ──────────────────────────────────

PERPLEXITY_THRESHOLDS = [
    (5,   "Çok Zayıf"),   # < 5     → çok tahmin edilebilir
    (20,  "Zayıf"),       # 5–20    → yaygın desen
    (80,  "Orta"),        # 20–80   → orta güçlük
    (200, "Güçlü"),       # 80–200  → az yaygın
]
# >= 200 → Çok Güçlü


def perplexity_to_level(perplexity: float) -> str:
    for threshold, level in PERPLEXITY_THRESHOLDS:
        if perplexity < threshold:
            return level
    return "Çok Güçlü"


def perplexity_to_score(perplexity: float) -> float:
    """Perplexity değerini 0-100 arası LSTM skoruna dönüştürür (yüksek = güçlü)."""
    import math
    if perplexity <= 0:
        return 0.0
    # log-scale normalisation: ppl 1 → 0, ppl 500 → 100
    score = min(100.0, max(0.0, math.log(perplexity + 1) / math.log(501) * 100))
    return round(score, 2)


# ── Eşik değer kalibrasyonu ──────────────────────────────────────────────────

def calibrate_thresholds(
    model,
    tokenizer,
    cal_passwords: List[str],
    cal_labels: List[str],
    device,
    max_length: int = 64,
) -> List[Tuple[float, str]]:
    """
    Test etiketleri kullanarak perplexity → seviye eşiklerini kalibre eder.

    Her sınıfın gerçek dağılımına göre perplexity percentillerini bulur
    ve sınıf sınırlarını otomatik ayarlar.
    """
    import statistics

    ppls = [compute_perplexity(model, pw, tokenizer, device, max_length) for pw in cal_passwords]

    # Sonsuz değerleri çok büyük bir sayıyla değiştir
    ppls = [min(p, 1e6) for p in ppls]

    label_ppls: Dict[str, List[float]] = {lbl: [] for lbl in LABEL_ORDER}
    for pw, lbl, ppl in zip(cal_passwords, cal_labels, ppls):
        if lbl in label_ppls:
            label_ppls[lbl].append(ppl)

    # Her sınıfın median perplexity'sini hesapla
    medians: Dict[str, float] = {}
    for lbl in LABEL_ORDER:
        vals = label_ppls[lbl]
        if vals:
            medians[lbl] = statistics.median(vals)
        else:
            medians[lbl] = None

    # Ardışık sınıf çiftleri arasında eşik: iki median'ın geometrik ortalaması
    thresholds: List[Tuple[float, str]] = []
    for i in range(len(LABEL_ORDER) - 1):
        a_lbl = LABEL_ORDER[i]
        b_lbl = LABEL_ORDER[i + 1]
        a_med = medians.get(a_lbl)
        b_med = medians.get(b_lbl)
        if a_med is not None and b_med is not None:
            import math
            boundary = math.sqrt(a_med * b_med) if a_med > 0 and b_med > 0 else (a_med + b_med) / 2
        elif a_med is not None:
            boundary = a_med * 3
        elif b_med is not None:
            boundary = b_med / 3
        else:
            boundary = (i + 1) * 20.0
        thresholds.append((round(boundary, 2), a_lbl))

    return thresholds  # [(t1, "Çok Zayıf"), (t2, "Zayıf"), (t3, "Orta"), (t4, "Güçlü")]


# ── Parola perplexity hesabı ──────────────────────────────────────────────────

def compute_perplexity(model, password: str, tokenizer, device, max_length: int = 64) -> float:
    """Tek bir parola için perplexity hesaplar."""
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=0)

    ids = tokenizer.encode(password, max_length=max_length)
    if len(ids) < 2:
        return float("inf")

    input_ids  = torch.tensor([ids[:-1]], dtype=torch.long).to(device)
    target_ids = torch.tensor([ids[1:]],  dtype=torch.long).to(device)

    with torch.no_grad():
        hidden = model.init_hidden(1, device)
        logits, _ = model(input_ids, hidden)
        loss = criterion(logits.view(-1, logits.size(-1)), target_ids.view(-1))

    return math.exp(loss.item()) if loss.item() < 700 else float("inf")


# ── Sınıflandırma F1 değerlendirmesi ─────────────────────────────────────────

LABEL_ORDER = ["Çok Zayıf", "Zayıf", "Orta", "Güçlü", "Çok Güçlü"]


def evaluate_classification(
    model,
    tokenizer,
    test_passwords: List[str],
    true_labels: List[str],
    device,
    max_length: int = 64,
    thresholds: Optional[List[Tuple[float, str]]] = None,
) -> Dict:
    """
    Perplexity tabanlı sınıflandırma F1 hesaplar.

    Parametreler
    ------------
    model         : Eğitilmiş PasswordLSTM
    tokenizer     : CharTokenizer
    test_passwords: Parola listesi
    true_labels   : Her parola için gerçek güvenlik seviyesi etiketi
    device        : torch.device

    Döndürür
    --------
    {
        "f1_macro": float,
        "f1_weighted": float,
        "precision_macro": float,
        "recall_macro": float,
        "accuracy": float,
        "per_class": {...},
        "confusion_matrix": [...],
        "predictions": [...],
    }
    """
    try:
        from sklearn.metrics import (
            f1_score, precision_score, recall_score,
            accuracy_score, confusion_matrix, classification_report,
        )
    except ImportError:
        raise ImportError("scikit-learn gerekli: pip install scikit-learn")

    active_thresholds = thresholds if thresholds is not None else PERPLEXITY_THRESHOLDS

    def _level(ppl: float) -> str:
        for threshold, level in active_thresholds:
            if ppl < threshold:
                return level
        return "Çok Güçlü"

    predictions = []
    for pw in test_passwords:
        ppl = compute_perplexity(model, pw, tokenizer, device, max_length)
        predictions.append(_level(ppl))

    f1_macro     = f1_score(true_labels, predictions, labels=LABEL_ORDER, average="macro", zero_division=0)
    f1_weighted  = f1_score(true_labels, predictions, labels=LABEL_ORDER, average="weighted", zero_division=0)
    prec_macro   = precision_score(true_labels, predictions, labels=LABEL_ORDER, average="macro", zero_division=0)
    rec_macro    = recall_score(true_labels, predictions, labels=LABEL_ORDER, average="macro", zero_division=0)
    acc          = accuracy_score(true_labels, predictions)
    cm           = confusion_matrix(true_labels, predictions, labels=LABEL_ORDER).tolist()

    # Sınıf bazlı metrikler
    per_class: Dict = {}
    for label in LABEL_ORDER:
        tp = sum(1 for t, p in zip(true_labels, predictions) if t == label and p == label)
        fp = sum(1 for t, p in zip(true_labels, predictions) if t != label and p == label)
        fn = sum(1 for t, p in zip(true_labels, predictions) if t == label and p != label)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        per_class[label] = {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

    return {
        "f1_macro":        round(f1_macro, 4),
        "f1_weighted":     round(f1_weighted, 4),
        "precision_macro": round(prec_macro, 4),
        "recall_macro":    round(rec_macro, 4),
        "accuracy":        round(acc, 4),
        "per_class":       per_class,
        "confusion_matrix": cm,
        "confusion_labels": LABEL_ORDER,
        "predictions":     predictions,
    }


# ── Kural tabanlı sistem F1 değerlendirmesi (LSTM gerektirmez) ────────────────

def evaluate_rule_based_f1(
    test_passwords: List[str],
    true_labels: List[str],
) -> Dict:
    """
    Kural tabanlı HybridRiskScorer üzerinde F1 hesaplar.
    LSTM modeli olmadan, sadece rule_score kullanır.
    """
    try:
        from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, confusion_matrix
    except ImportError:
        raise ImportError("scikit-learn gerekli: pip install scikit-learn")

    try:
        from src.security.risk_scorer import HybridRiskScorer
    except ImportError:
        from security.risk_scorer import HybridRiskScorer

    scorer = HybridRiskScorer(rule_weight=1.0, lstm_weight=0.0)
    predictions = [scorer.score(pw).security_level for pw in test_passwords]

    f1_macro    = f1_score(true_labels, predictions, labels=LABEL_ORDER, average="macro", zero_division=0)
    f1_weighted = f1_score(true_labels, predictions, labels=LABEL_ORDER, average="weighted", zero_division=0)
    prec_macro  = precision_score(true_labels, predictions, labels=LABEL_ORDER, average="macro", zero_division=0)
    rec_macro   = recall_score(true_labels, predictions, labels=LABEL_ORDER, average="macro", zero_division=0)
    acc         = accuracy_score(true_labels, predictions)
    cm          = confusion_matrix(true_labels, predictions, labels=LABEL_ORDER).tolist()

    per_class: Dict = {}
    for label in LABEL_ORDER:
        tp = sum(1 for t, p in zip(true_labels, predictions) if t == label and p == label)
        fp = sum(1 for t, p in zip(true_labels, predictions) if t != label and p == label)
        fn = sum(1 for t, p in zip(true_labels, predictions) if t == label and p != label)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        per_class[label] = {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

    return {
        "f1_macro":        round(f1_macro, 4),
        "f1_weighted":     round(f1_weighted, 4),
        "precision_macro": round(prec_macro, 4),
        "recall_macro":    round(rec_macro, 4),
        "accuracy":        round(acc, 4),
        "per_class":       per_class,
        "confusion_matrix": cm,
        "confusion_labels": LABEL_ORDER,
        "predictions":     predictions,
    }
