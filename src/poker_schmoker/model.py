"""Immutable poker card values."""

from dataclasses import dataclass


_RANK_VALUES = {rank: value for value, rank in enumerate("23456789TJQKA", start=2)}


@dataclass(frozen=True, order=True)
class Card:
    rank: int
    suit: str

    def __post_init__(self) -> None:
        if self.rank not in _RANK_VALUES.values() or self.suit not in "cdhs":
            raise ValueError("Invalid poker card")

    @classmethod
    def parse(cls, code: str) -> "Card":
        if not isinstance(code, str) or len(code) != 2:
            raise ValueError(f"Invalid card code: {code!r}")
        value = _RANK_VALUES.get(code[0].upper())
        suit = code[1].lower()
        if value is None or suit not in "cdhs":
            raise ValueError(f"Invalid card code: {code!r}")
        return cls(value, suit)
