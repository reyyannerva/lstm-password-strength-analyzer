"""
Training utilities for LSTM password modeling.

Provides a simple training pipeline that supports:
- single-epoch training
- optional validation evaluation
- loss tracking and perplexity reporting
- default optimizer and criterion configuration
"""

from typing import Dict, Optional

import torch
import torch.nn as nn

from src.model.evaluate import evaluate


def _default_criterion(pad_token_id: int = 0) -> nn.CrossEntropyLoss:
    return nn.CrossEntropyLoss(ignore_index=pad_token_id)


def _default_optimizer(model: nn.Module, lr: float = 1e-3, weight_decay: float = 0.0) -> torch.optim.Optimizer:
    return torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)


def train_epoch(
    model: nn.Module,
    data_loader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
    grad_clip: Optional[float] = None,
) -> float:
    model.train()
    total_loss = 0.0
    total_tokens = 0

    for inputs, targets in data_loader:
        inputs, targets = inputs.to(device), targets.to(device)

        optimizer.zero_grad()
        logits, _ = model(inputs)

        loss = criterion(logits.view(-1, logits.size(-1)), targets.view(-1))
        loss.backward()

        if grad_clip is not None:
            nn.utils.clip_grad_norm_(model.parameters(), grad_clip)

        optimizer.step()

        ignore_index = getattr(criterion, "ignore_index", None)
        if ignore_index is not None:
            non_pad = (targets != ignore_index).sum().item()
        else:
            non_pad = targets.numel()

        total_loss += loss.item() * non_pad
        total_tokens += non_pad

    return total_loss / total_tokens if total_tokens > 0 else float("inf")


def train(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    val_loader: Optional[torch.utils.data.DataLoader] = None,
    epochs: int = 10,
    optimizer: Optional[torch.optim.Optimizer] = None,
    criterion: Optional[nn.Module] = None,
    device: Optional[torch.device] = None,
    grad_clip: Optional[float] = None,
) -> Dict[str, list]:
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = model.to(device)

    if optimizer is None:
        optimizer = _default_optimizer(model)

    if criterion is None:
        criterion = _default_criterion()

    history: Dict[str, list] = {
        "train_loss": [],
        "val_loss": [],
        "val_perplexity": [],
    }

    for epoch in range(1, epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device, grad_clip)
        history["train_loss"].append(train_loss)

        if val_loader is not None:
            metrics = evaluate(model, val_loader, device)
            history["val_loss"].append(metrics["loss"])
            history["val_perplexity"].append(metrics["perplexity"])
        else:
            history["val_loss"].append(None)
            history["val_perplexity"].append(None)

    return history
