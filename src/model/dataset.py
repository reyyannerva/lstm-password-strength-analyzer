"""
Password dataset and DataLoader utilities.

This module prepares password sequences for LSTM training.
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
from torch.utils.data import Dataset, DataLoader


class PasswordDataset(Dataset):
    """
    PyTorch Dataset for password language modeling.

    Args:
        passwords: List of password strings.
        tokenizer: Tokenizer object with an encode(password) method.
        max_length: Maximum sequence length after encoding.
        pad_token_id: Token id used for padding.
    """

    def __init__(
        self,
        passwords: Sequence[str],
        tokenizer,
        max_length: int = 64,
        pad_token_id: int = 0,
    ) -> None:
        if passwords is None:
            raise ValueError("passwords cannot be None")

        if tokenizer is None:
            raise ValueError("tokenizer cannot be None")

        if not hasattr(tokenizer, "encode"):
            raise TypeError("tokenizer must have an encode(password) method")

        if max_length < 2:
            raise ValueError("max_length must be at least 2")

        self.passwords = [str(password).strip() for password in passwords if str(password).strip()]
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.pad_token_id = pad_token_id

    def __len__(self) -> int:
        return len(self.passwords)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        password = self.passwords[index]

        token_ids = self.tokenizer.encode(password)

        if not isinstance(token_ids, list):
            token_ids = list(token_ids)

        token_ids = token_ids[: self.max_length]

        if len(token_ids) < 2:
            token_ids = token_ids + [self.pad_token_id] * (2 - len(token_ids))

        input_ids = token_ids[:-1]
        target_ids = token_ids[1:]

        input_ids = self._pad(input_ids, self.max_length - 1)
        target_ids = self._pad(target_ids, self.max_length - 1)

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
    max_length: int = 64,
    pad_token_id: int = 0,
    shuffle: bool = True,
    num_workers: int = 0,
) -> DataLoader:
    """
    Create a PyTorch DataLoader for password training.

    Args:
        passwords: List of password strings.
        tokenizer: Tokenizer object with an encode(password) method.
        batch_size: Number of samples per batch.
        max_length: Maximum encoded sequence length.
        pad_token_id: Padding token id.
        shuffle: Whether to shuffle the dataset.
        num_workers: DataLoader worker count.

    Returns:
        DataLoader that yields input and target batches.
    """

    dataset = PasswordDataset(
        passwords=passwords,
        tokenizer=tokenizer,
        max_length=max_length,
        pad_token_id=pad_token_id,
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
    )