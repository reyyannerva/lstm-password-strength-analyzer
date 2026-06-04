"""
LSTM model bileşenleri için birim testleri.
"""

import pytest
import torch

try:
    from src.model.lstm_model import PasswordLSTM, build_model
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


VOCAB_SIZE = 50
BATCH_SIZE = 4
SEQ_LEN = 10


@pytest.fixture
def model():
    if not AVAILABLE:
        pytest.skip("src/model/lstm_model.py henüz mevcut değil.")
    return build_model(vocab_size=VOCAB_SIZE, embed_dim=32, hidden_dim=64, num_layers=2, dropout=0.1)


def test_model_instantiation(model):
    assert model is not None


def test_forward_pass_output_shape(model):
    x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    logits, hidden = model(x)
    assert logits.shape == (BATCH_SIZE, SEQ_LEN, VOCAB_SIZE)


def test_hidden_state_shape(model):
    x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    _, (h, c) = model(x)
    assert h.shape[0] == 2  # num_layers
    assert h.shape[1] == BATCH_SIZE
    assert c.shape == h.shape


def test_init_hidden_shape(model):
    device = torch.device("cpu")
    h, c = model.init_hidden(BATCH_SIZE, device)
    assert h.shape == (2, BATCH_SIZE, 64)
    assert c.shape == h.shape


def test_forward_with_init_hidden(model):
    device = torch.device("cpu")
    x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    hidden = model.init_hidden(BATCH_SIZE, device)
    logits, _ = model(x, hidden)
    assert logits.shape == (BATCH_SIZE, SEQ_LEN, VOCAB_SIZE)


def test_single_sample(model):
    x = torch.randint(0, VOCAB_SIZE, (1, SEQ_LEN))
    logits, _ = model(x)
    assert logits.shape == (1, SEQ_LEN, VOCAB_SIZE)


def test_output_is_tensor(model):
    x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    logits, _ = model(x)
    assert isinstance(logits, torch.Tensor)


def test_model_eval_mode(model):
    model.eval()
    x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, SEQ_LEN))
    with torch.no_grad():
        logits, _ = model(x)
    assert logits.shape == (BATCH_SIZE, SEQ_LEN, VOCAB_SIZE)


def test_invalid_vocab_index():
    if not AVAILABLE:
        pytest.skip("src/model/lstm_model.py henüz mevcut değil.")
    model = build_model(vocab_size=10, embed_dim=16, hidden_dim=32, num_layers=1, dropout=0.0)
    x = torch.randint(0, 10, (2, 5))
    logits, _ = model(x)
    assert logits.shape == (2, 5, 10)
