"""
Tokenizer modülü için birim testleri.
Beklenen arayüz: CharTokenizer sınıfı (src/model/tokenizer.py)
"""

import pytest

try:
    from src.model.tokenizer import CharTokenizer
except ImportError:
    CharTokenizer = None


@pytest.fixture
def tokenizer():
    if CharTokenizer is None:
        pytest.skip("src/model/tokenizer.py henüz mevcut değil.")
    passwords = ["abc123", "hello", "password", "xyz"]
    tok = CharTokenizer()
    tok.fit(passwords)
    return tok


def test_vocab_not_empty(tokenizer):
    assert len(tokenizer.vocab) > 0


def test_encode_returns_list(tokenizer):
    ids = tokenizer.encode("abc")
    assert isinstance(ids, list)
    assert len(ids) > 0


def test_encode_decode_roundtrip(tokenizer):
    original = "abc"
    ids = tokenizer.encode(original)
    recovered = tokenizer.decode(ids)
    assert recovered == original


def test_unknown_char_handled(tokenizer):
    ids = tokenizer.encode("§§§")
    assert isinstance(ids, list)


def test_empty_string(tokenizer):
    ids = tokenizer.encode("")
    assert isinstance(ids, list)


def test_special_chars(tokenizer):
    ids = tokenizer.encode("!@#")
    assert isinstance(ids, list)


def test_vocab_size_property(tokenizer):
    assert tokenizer.vocab_size > 0


def test_padding_index(tokenizer):
    assert hasattr(tokenizer, "pad_idx")
    assert isinstance(tokenizer.pad_idx, int)
