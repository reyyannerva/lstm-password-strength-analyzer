"""
Eğitilmiş LSTM modelinin validation değerlendirmesi.

Hesaplanan metrikler:
- loss
- perplexity
- token-level accuracy
"""

import math

import torch
import torch.nn as nn


def evaluate(model, data_loader, device, pad_token_id: int = 0):
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

            flat_logits = logits.view(-1, vocab_size)
            flat_targets = targets.view(-1)

            loss = criterion(flat_logits, flat_targets)

            non_pad_mask = flat_targets != pad_token_id
            non_pad_count = non_pad_mask.sum().item()

            if non_pad_count == 0:
                continue

            predictions = flat_logits.argmax(dim=-1)
            correct_tokens += (
                predictions[non_pad_mask] == flat_targets[non_pad_mask]
            ).sum().item()

            total_loss += loss.item() * non_pad_count
            total_tokens += non_pad_count

    avg_loss = total_loss / total_tokens if total_tokens > 0 else float("inf")
    perplexity = math.exp(avg_loss) if avg_loss != float("inf") else float("inf")
    accuracy = correct_tokens / total_tokens if total_tokens > 0 else 0.0

    return {
        "loss": avg_loss,
        "perplexity": perplexity,
        "accuracy": accuracy,
    }