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

def test_fit_returns_self_for_chaining():
    tokenizer = CharTokenizer()

    result = tokenizer.fit(["abc", "123"])

    assert result is tokenizer


def test_encode_supports_max_length():
    tokenizer = CharTokenizer()
    tokenizer.fit(["abcdef"])

    encoded = tokenizer.encode("abcdef", max_length=4)

    assert len(encoded) == 4
    assert encoded[0] == tokenizer.sos_idx
    assert encoded[-1] == tokenizer.eos_idx


def test_encode_without_special_tokens():
    tokenizer = CharTokenizer()
    tokenizer.fit(["abc"])

    encoded = tokenizer.encode("abc", add_special_tokens=False)

    assert tokenizer.sos_idx not in encoded
    assert tokenizer.eos_idx not in encoded
    assert len(encoded) == 3


def test_analyze_coverage_reports_unknown_ratio():
    tokenizer = CharTokenizer()
    tokenizer.fit(["abc"])

    coverage = tokenizer.analyze_coverage(["abcx"])

    assert coverage["total_characters"] == 4
    assert coverage["unknown_characters"] == 1
    assert coverage["coverage_ratio"] == 0.75
    assert coverage["unknown_ratio"] == 0.25

