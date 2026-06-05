"""
Character-level tokenizer for password strings.

Implements CharTokenizer with:
- special tokens
- encode/decode
- optional max_length support
- optional special token control
- vocabulary coverage analysis
"""

from typing import Iterable, List, Dict


class CharTokenizer:
    def __init__(self) -> None:
        self.pad_token = "<pad>"
        self.sos_token = "<sos>"
        self.eos_token = "<eos>"
        self.unk_token = "<unk>"

        self.pad_idx = 0
        self.sos_idx = 1
        self.eos_idx = 2
        self.unk_idx = 3

        self._char2id: Dict[str, int] = {}
        self._id2char: Dict[int, str] = {}

        self._id2char[self.pad_idx] = self.pad_token
        self._id2char[self.sos_idx] = self.sos_token
        self._id2char[self.eos_idx] = self.eos_token
        self._id2char[self.unk_idx] = self.unk_token

        self._char2id[self.pad_token] = self.pad_idx
        self._char2id[self.sos_token] = self.sos_idx
        self._char2id[self.eos_token] = self.eos_idx
        self._char2id[self.unk_token] = self.unk_idx

        self._next_id = 4

    def fit(self, passwords: Iterable[str]) -> "CharTokenizer":
        """Build vocabulary from password strings and return self."""
        for password in passwords:
            if password is None:
                continue

            for ch in str(password):
                if ch in (
                    self.pad_token,
                    self.sos_token,
                    self.eos_token,
                    self.unk_token,
                ):
                    continue

                if ch not in self._char2id:
                    self._char2id[ch] = self._next_id
                    self._id2char[self._next_id] = ch
                    self._next_id += 1

        return self

    def encode(
        self,
        password: str,
        max_length: int | None = None,
        add_special_tokens: bool = True,
    ) -> List[int]:
        """
        Encode a password string to token ids.

        Default output:
        [<sos>, id(c1), id(c2), ..., <eos>]
        """
        if password is None:
            password = ""

        ids: List[int] = []

        if add_special_tokens:
            ids.append(self.sos_idx)

        for ch in str(password):
            ids.append(self._char2id.get(ch, self.unk_idx))

        if add_special_tokens:
            ids.append(self.eos_idx)

        if max_length is not None:
            if max_length < 1:
                raise ValueError("max_length must be at least 1")

            ids = ids[:max_length]

            if add_special_tokens and ids and ids[-1] != self.eos_idx:
                ids[-1] = self.eos_idx

        return ids

    def decode(self, ids: Iterable[int]) -> str:
        """Decode token ids back to a password string."""
        chars: List[str] = []

        for idx in ids:
            if idx in (self.sos_idx, self.eos_idx, self.pad_idx):
                continue

            if idx == self.unk_idx:
                continue

            ch = self._id2char.get(idx)
            if ch is not None:
                chars.append(ch)

        return "".join(chars)

    def analyze_coverage(self, passwords: Iterable[str]) -> Dict[str, float | int]:
        """
        Analyze tokenizer vocabulary coverage on password data.
        """
        total_characters = 0
        unknown_characters = 0

        for password in passwords:
            if password is None:
                continue

            for ch in str(password):
                total_characters += 1
                if ch not in self._char2id:
                    unknown_characters += 1

        if total_characters == 0:
            return {
                "total_characters": 0,
                "unknown_characters": 0,
                "coverage_ratio": 1.0,
                "unknown_ratio": 0.0,
            }

        unknown_ratio = unknown_characters / total_characters

        return {
            "total_characters": total_characters,
            "unknown_characters": unknown_characters,
            "coverage_ratio": 1.0 - unknown_ratio,
            "unknown_ratio": unknown_ratio,
        }

    @property
    def vocab(self) -> Dict[str, int]:
        """Expose character-to-id mapping."""
        return dict(self._char2id)

    @property
    def vocab_size(self) -> int:
        return self._next_id