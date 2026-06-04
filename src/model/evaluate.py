"""
Eğitilmiş LSTM modelinin validation değerlendirmesi ve perplexity hesabı.
"""

import math
import torch
import torch.nn as nn


def evaluate(model, data_loader, device):
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=0)
    total_loss = 0.0
    total_tokens = 0

    with torch.no_grad():
        for inputs, targets in data_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            batch_size = inputs.size(0)
            hidden = model.init_hidden(batch_size, device)
            logits, _ = model(inputs, hidden)

            logits = logits.view(-1, logits.size(-1))
            targets = targets.view(-1)

            loss = criterion(logits, targets)
            non_pad = (targets != 0).sum().item()
            total_loss += loss.item() * non_pad
            total_tokens += non_pad

    avg_loss = total_loss / total_tokens if total_tokens > 0 else float("inf")
    perplexity = math.exp(avg_loss)
    return {"loss": avg_loss, "perplexity": perplexity}
