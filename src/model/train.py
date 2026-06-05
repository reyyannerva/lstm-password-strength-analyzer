"""
Training utilities for LSTM password modeling.

Provides a simple training pipeline that supports:
- single-epoch training
- optional validation evaluation
- loss tracking and perplexity reporting
- default optimizer and criterion configuration
"""

import json
import os
from typing import Dict, Optional

import torch
import torch.nn as nn
import math

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


def _save_checkpoint(model: nn.Module, optimizer: torch.optim.Optimizer, epoch: int, train_loss: float, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "train_loss": train_loss,
        },
        path,
    )


def _save_training_log(history: Dict[str, list], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def train(
    model: nn.Module,
    train_loader: torch.utils.data.DataLoader,
    val_loader: Optional[torch.utils.data.DataLoader] = None,
    epochs: int = 10,
    optimizer: Optional[torch.optim.Optimizer] = None,
    criterion: Optional[nn.Module] = None,
    device: Optional[torch.device] = None,
    grad_clip: Optional[float] = None,
    checkpoint_path: Optional[str] = None,
    log_path: Optional[str] = None,
    early_stopping_patience: Optional[int] = None,
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
        "train_perplexity": [],
        "val_loss": [],
        "val_perplexity": [],
        "val_accuracy": [],
        "best_val_loss": [],
        "best_epoch": [],
    }
    best_val_loss = float("inf")
    epochs_without_improvement = 0

    for epoch in range(1, epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device, grad_clip)
        history["train_loss"].append(train_loss)
        history["train_perplexity"].append(
            math.exp(train_loss) if train_loss != float("inf") else float("inf")
        )

        if val_loader is not None:
            metrics = evaluate(model, val_loader, device)
            history["val_loss"].append(metrics["loss"])
            history["val_perplexity"].append(metrics["perplexity"])
            history["val_accuracy"].append(metrics.get("accuracy", 0.0))

            if early_stopping_patience is not None:
                current_val_loss = metrics["loss"]

                if current_val_loss < best_val_loss:
                    best_val_loss = current_val_loss
                    epochs_without_improvement = 0
                else:
                    epochs_without_improvement += 1

                if epochs_without_improvement >= early_stopping_patience:
                    break
        else:
            history["val_loss"].append(None)
            history["val_perplexity"].append(None)
            history["val_accuracy"].append(None)
        
        valid_losses = [loss for loss in history["val_loss"] if loss is not None]

        if valid_losses:
            best_val_loss = min(valid_losses)
            best_epoch = history["val_loss"].index(best_val_loss) + 1
        else:
            best_val_loss = None
            best_epoch = None

        history["best_val_loss"].append(best_val_loss)
        history["best_epoch"].append(best_epoch)

        if checkpoint_path is not None:
            _save_checkpoint(model, optimizer, epoch, train_loss, checkpoint_path)

        if log_path is not None:
            _save_training_log(history, log_path)

    return history

def plot_training_history(history: Dict[str, list], output_dir: str = "experiments") -> Dict[str, str]:
    """
    Save training evaluation charts.

    Generated charts:
    - training_loss.png
    - training_perplexity.png
    - validation_accuracy.png
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("matplotlib is required to generate training charts.") from exc

    os.makedirs(output_dir, exist_ok=True)

    epochs = list(range(1, len(history.get("train_loss", [])) + 1))
    saved_paths: Dict[str, str] = {}

    def _save_line_chart(filename: str, title: str, ylabel: str, series: Dict[str, list]) -> None:
        plt.figure(figsize=(8, 5))

        for label, values in series.items():
            clean_values = [
                value if value is not None and value != float("inf") else None
                for value in values
            ]
            plt.plot(epochs, clean_values, marker="o", label=label)

        plt.title(title)
        plt.xlabel("Epoch")
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        path = os.path.join(output_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        saved_paths[filename] = path

    _save_line_chart(
        "training_loss.png",
        "Training and Validation Loss",
        "Loss",
        {
            "Train Loss": history.get("train_loss", []),
            "Validation Loss": history.get("val_loss", []),
        },
    )

    _save_line_chart(
        "training_perplexity.png",
        "Training and Validation Perplexity",
        "Perplexity",
        {
            "Train Perplexity": history.get("train_perplexity", []),
            "Validation Perplexity": history.get("val_perplexity", []),
        },
    )

    _save_line_chart(
        "validation_accuracy.png",
        "Validation Accuracy",
        "Accuracy",
        {
            "Validation Accuracy": history.get("val_accuracy", []),
        },
    )

    return saved_paths