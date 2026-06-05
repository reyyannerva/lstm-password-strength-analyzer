"""
Dataset ve DataLoader yapısı için birim testleri.
Beklenen arayüz: PasswordDataset sınıfı (src/model/dataset.py)
"""

import pytest

try:
    from src.model.tokenizer import CharTokenizer
    from src.model.dataset import PasswordDataset
    from torch.utils.data import DataLoader
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


@pytest.fixture
def setup():
    if not AVAILABLE:
        pytest.skip("src/model/tokenizer.py veya src/model/dataset.py henüz mevcut değil.")
    passwords = ["abc123", "hello!", "xyz789", "test"]
    tok = CharTokenizer()
    tok.fit(passwords)
    ds = PasswordDataset(passwords, tok, seq_len=8)
    return ds, tok


def test_dataset_length(setup):
    ds, _ = setup
    assert len(ds) == 4


def test_item_shapes(setup):
    ds, _ = setup
    x, y = ds[0]
    assert x.shape == y.shape
    assert x.ndim == 1


def test_input_target_offset(setup):
    ds, _ = setup
    x, y = ds[0]
    assert x.shape[0] == y.shape[0]


def test_dataloader_batch(setup):
    ds, _ = setup
    loader = DataLoader(ds, batch_size=2, shuffle=False)
    inputs, targets = next(iter(loader))
    assert inputs.shape[0] == 2
    assert targets.shape[0] == 2


def test_empty_password_skipped():
    if not AVAILABLE:
        pytest.skip("Gerekli modüller mevcut değil.")
    passwords = ["", "abc", ""]
    tok = CharTokenizer()
    tok.fit(["abc"])
    ds = PasswordDataset(passwords, tok, seq_len=8)
    assert len(ds) <= 3


def test_tensor_dtype(setup):
    import torch
    ds, _ = setup
    x, y = ds[0]
    assert x.dtype == torch.long
    assert y.dtype == torch.long
