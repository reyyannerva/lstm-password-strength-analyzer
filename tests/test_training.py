"""
Training pipeline tests for LSTM password model.
"""

import pytest
import torch

try:
    from src.model.lstm_model import build_model
    from src.model.dataset import PasswordDataset, create_dataloader
    from src.model.train import train, train_epoch
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


class DummyTokenizer:
    def encode(self, password):
        # Basic encoding that produces a sequence of integer ids.
        if not password:
            return [1, 2]
        return [1] + [ord(c) % 10 + 4 for c in password] + [2]


@pytest.fixture
def sample_data_loader():
    if not AVAILABLE:
        pytest.skip("Model training pipeline modülleri mevcut değil.")

    passwords = ["abc", "defg", "xyz", "test"]
    tokenizer = DummyTokenizer()
    dataset = PasswordDataset(passwords, tokenizer, max_length=6)
    return create_dataloader(dataset.passwords, tokenizer, batch_size=2, max_length=6, shuffle=False)


def test_train_epoch_runs(sample_data_loader):
    model = build_model(vocab_size=16, embed_dim=16, hidden_dim=32, num_layers=1, dropout=0.0)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = torch.nn.CrossEntropyLoss(ignore_index=0)
    device = torch.device("cpu")

    loss = train_epoch(model, sample_data_loader, optimizer, criterion, device)
    assert isinstance(loss, float)
    assert loss >= 0.0


def test_train_history(sample_data_loader):
    model = build_model(vocab_size=16, embed_dim=16, hidden_dim=32, num_layers=1, dropout=0.0)
    history = train(model, sample_data_loader, val_loader=sample_data_loader, epochs=2, device=torch.device("cpu"))

    assert history["train_loss"] is not None
    assert len(history["train_loss"]) == 2
    assert len(history["val_loss"]) == 2
    assert len(history["val_perplexity"]) == 2
    assert all(isinstance(loss, float) for loss in history["train_loss"])
    assert all(isinstance(perp, float) for perp in history["val_perplexity"])


def test_train_uses_default_optimizer_and_criterion(sample_data_loader):
    model = build_model(vocab_size=16, embed_dim=16, hidden_dim=32, num_layers=1, dropout=0.0)
    history = train(model, sample_data_loader, epochs=1, device=torch.device("cpu"))

    assert isinstance(history, dict)
    assert history["train_loss"][0] >= 0.0


def test_train_writes_checkpoint_and_log(sample_data_loader, tmp_path):
    model = build_model(vocab_size=16, embed_dim=16, hidden_dim=32, num_layers=1, dropout=0.0)
    checkpoint_path = tmp_path / "checkpoints" / "model_epoch.pt"
    log_path = tmp_path / "logs" / "training.json"

    history = train(
        model,
        sample_data_loader,
        epochs=1,
        device=torch.device("cpu"),
        checkpoint_path=str(checkpoint_path),
        log_path=str(log_path),
    )

    assert checkpoint_path.exists()
    assert log_path.exists()
    assert history["train_loss"][0] >= 0.0

    import json

    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "train_loss" in data
    assert len(data["train_loss"]) == 1
