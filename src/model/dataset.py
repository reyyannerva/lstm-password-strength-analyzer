"""
Password dataset and DataLoader utilities.

This module prepares password sequences for LSTM language-model training.

For each password, it creates:

input_ids  = token ids except the last token
target_ids = token ids except the first token

Example:
password: "abc"
encoded : [<sos>, a, b, c, <eos>]
input   : [<sos>, a, b, c]
target  : [a, b, c, <eos>]
"""

from typing import List, Sequence, Tuple

import torch
from torch.utils.data import DataLoader, Dataset


class PasswordDataset(Dataset):
    """
    PyTorch Dataset for password language modeling.

    This class is intentionally backward compatible with both parameter names:

    - seq_len
    - max_length

    If max_length is provided, it takes priority over seq_len.

    Args:
        passwords: Password strings.
        tokenizer: Tokenizer object with an encode(password) method.
        seq_len: Maximum encoded sequence length.
        max_length: Backward-compatible alias for seq_len.
        pad_token_id: Token id used for padding.
    """

    def __init__(
        self,
        passwords: Sequence[str],
        tokenizer,
        seq_len: int = 64,
        max_length: int | None = None,
        pad_token_id: int = 0,
    ) -> None:
        if passwords is None:
            raise ValueError("passwords cannot be None")

        if tokenizer is None:
            raise ValueError("tokenizer cannot be None")

        if not hasattr(tokenizer, "encode"):
            raise TypeError("tokenizer must have an encode(password) method")

        effective_seq_len = max_length if max_length is not None else seq_len

        if effective_seq_len < 2:
            raise ValueError("seq_len/max_length must be at least 2")

        self.passwords = [
            str(password).strip()
            for password in passwords
            if str(password).strip()
        ]

        self.tokenizer = tokenizer
        self.seq_len = int(effective_seq_len)
        self.max_length = int(effective_seq_len)
        self.pad_token_id = int(pad_token_id)

    def __len__(self) -> int:
        return len(self.passwords)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        password = self.passwords[index]

        token_ids = self.tokenizer.encode(password)

        if not isinstance(token_ids, list):
            token_ids = list(token_ids)

        token_ids = [int(token_id) for token_id in token_ids]
        token_ids = token_ids[: self.seq_len]

        if len(token_ids) < 2:
            token_ids = token_ids + [self.pad_token_id] * (2 - len(token_ids))

        input_ids = token_ids[:-1]
        target_ids = token_ids[1:]

        input_ids = self._pad(input_ids, self.seq_len - 1)
        target_ids = self._pad(target_ids, self.seq_len - 1)

        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(target_ids, dtype=torch.long),
        )

    def _pad(self, token_ids: List[int], target_length: int) -> List[int]:
        if len(token_ids) >= target_length:
            return token_ids[:target_length]

        padding_size = target_length - len(token_ids)
        return token_ids + [self.pad_token_id] * padding_size


def create_dataloader(
    passwords: Sequence[str],
    tokenizer,
    batch_size: int = 32,
    seq_len: int = 64,
    max_length: int | None = None,
    pad_token_id: int = 0,
    shuffle: bool = True,
    num_workers: int = 0,
) -> DataLoader:
    """
    Create a PyTorch DataLoader for password training.

    This helper supports both seq_len and max_length for compatibility.

    Args:
        passwords: Password strings.
        tokenizer: Tokenizer object with an encode(password) method.
        batch_size: Number of samples per batch.
        seq_len: Maximum encoded sequence length.
        max_length: Optional alias for seq_len. Takes priority when provided.
        pad_token_id: Padding token id.
        shuffle: Whether to shuffle the dataset.
        num_workers: DataLoader worker count.

    Returns:
        DataLoader that yields input and target batches.
    """

    effective_seq_len = max_length if max_length is not None else seq_len

    dataset = PasswordDataset(
        passwords=passwords,
        tokenizer=tokenizer,
        seq_len=effective_seq_len,
        pad_token_id=pad_token_id,
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
    )