"""
Character-level tokenizer for password strings.

Implements a minimal `CharTokenizer` with the interface used by tests
and dataset code: `fit(passwords)`, `encode(password)`, `decode(ids)`.

Special token ids:
  <pad> = 0
  <sos> = 1
  <eos> = 2
  <unk> = 3

The encoder wraps sequences with <sos>...<eos> and returns a list of ints.
"""

from typing import Iterable, List, Dict


class CharTokenizer:
    def __init__(self) -> None:
        # Special tokens
        self.pad_token = "<pad>"
        self.sos_token = "<sos>"
        self.eos_token = "<eos>"
        self.unk_token = "<unk>"

        # Fixed ids for special tokens
        self.pad_idx = 0
        self.sos_idx = 1
        self.eos_idx = 2
        self.unk_idx = 3

        # Vocab mappings (char -> id) and inverse
        # Start assigning ids after the special tokens (start at 4)
        self._char2id: Dict[str, int] = {}
        self._id2char: Dict[int, str] = {}

        # initialize special tokens in mappings for completeness
        self._id2char[self.pad_idx] = self.pad_token
        self._id2char[self.sos_idx] = self.sos_token
        self._id2char[self.eos_idx] = self.eos_token
        self._id2char[self.unk_idx] = self.unk_token

        # reverse mapping for specials
        self._char2id[self.pad_token] = self.pad_idx
        self._char2id[self.sos_token] = self.sos_idx
        self._char2id[self.eos_token] = self.eos_idx
        self._char2id[self.unk_token] = self.unk_idx

        self._next_id = 4

    def fit(self, passwords: Iterable[str]) -> None:
        """Build vocabulary from an iterable of password strings."""
        for pw in passwords:
            if pw is None:
                continue
            for ch in str(pw):
                if ch not in self._char2id:
                    # skip if ch is one of the special token strings
                    if ch in (self.pad_token, self.sos_token, self.eos_token, self.unk_token):
                        continue
                    self._char2id[ch] = self._next_id
                    self._id2char[self._next_id] = ch
                    self._next_id += 1

    def encode(self, password: str) -> List[int]:
        """Encode a password string to a list of token ids.

        Output format: [<sos>, id(c1), id(c2), ..., <eos>]
        Unknown characters map to `<unk>` id. Always returns a list.
        """
        if password is None:
            password = ""

        ids: List[int] = [self.sos_idx]

        for ch in str(password):
            ids.append(self._char2id.get(ch, self.unk_idx))

        ids.append(self.eos_idx)
        return ids

    def decode(self, ids: Iterable[int]) -> str:
        """Decode a sequence of ids back to a string.

        Strips leading `<sos>` and trailing `<eos>` tokens if present.
        Special tokens are ignored in the output string.
        """
        chars: List[str] = []
        for idx in ids:
            if idx == self.sos_idx or idx == self.eos_idx or idx == self.pad_idx:
                continue
            if idx == self.unk_idx:
                # For unknown tokens, we cannot recover original char; skip or
                # optionally place a placeholder. Tests expect exact roundtrip
                # for known characters, so leaving unknowns out is acceptable.
                continue
            ch = self._id2char.get(idx)
            if ch is not None:
                chars.append(ch)

        return "".join(chars)

    @property
    def vocab(self) -> Dict[str, int]:
        """Expose the character->id mapping (including specials)."""
        return dict(self._char2id)

    @property
    def vocab_size(self) -> int:
        return self._next_id
