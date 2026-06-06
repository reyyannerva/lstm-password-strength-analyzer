"""
Parola tahmin edilebilirlik skoru üretici.
Düşük perplexity → tahmin edilmesi kolay → yüksek risk skoru.
"""

import math
import torch
import torch.nn.functional as F


# Perplexity eşik değerleri (deneysel)
VERY_WEAK_PPX = 5.0
STRONG_PPX = 200.0


def _password_perplexity(model, tokenizer, password, device):
    model.eval()
    if not password or not password.strip():
        return 1.0
    ids = tokenizer.encode(password)
    if len(ids) < 2:
        return 1.0

    inputs = torch.tensor([ids[:-1]], dtype=torch.long).to(device)
    targets = torch.tensor([ids[1:]], dtype=torch.long).to(device)

    with torch.no_grad():
        hidden = model.init_hidden(1, device)
        logits, _ = model(inputs, hidden)
        logits = logits.view(-1, logits.size(-1))
        targets = targets.view(-1)
        log_probs = F.log_softmax(logits, dim=-1)
        token_log_probs = log_probs[range(len(targets)), targets]
        avg_neg_log_prob = -token_log_probs.mean().item()

    return math.exp(avg_neg_log_prob)


def score_password(model, tokenizer, password, device="cpu"):
    """
    0-100 arası risk skoru döner.
    100 → çok zayıf (kolay tahmin edilir), 0 → çok güçlü.
    """
    ppx = _password_perplexity(model, tokenizer, password, device)

    ppx_clamped = max(VERY_WEAK_PPX, min(ppx, STRONG_PPX))
    normalized = (ppx_clamped - VERY_WEAK_PPX) / (STRONG_PPX - VERY_WEAK_PPX)
    risk_score = round((1.0 - normalized) * 100, 2)

    return {
        "password": password,
        "perplexity": round(ppx, 4),
        "risk_score": risk_score,
    }
