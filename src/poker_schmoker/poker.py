"""Deterministic Hold'em ranking and mathematical primitives."""

from collections import Counter
from decimal import Decimal
from itertools import combinations
from typing import Sequence

from .model import Card


def _straight_high(ranks: list[int]) -> int | None:
    values = set(ranks)
    if values == {14, 2, 3, 4, 5}:
        return 5
    if len(values) == 5 and max(values) - min(values) == 4:
        return max(values)
    return None


def hand_rank(cards: Sequence[Card]) -> tuple[int, ...]:
    """Return a comparable (category, tie-breakers...) tuple for five cards."""
    if len(cards) != 5 or len(set(cards)) != 5:
        raise ValueError("A five-card hand must contain exactly five distinct cards")

    ranks = [card.rank for card in cards]
    counts = Counter(ranks)
    groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)
    flush = len({card.suit for card in cards}) == 1
    straight = _straight_high(ranks)

    if flush and straight is not None:
        return (8, straight)
    if groups[0][0] == 4:
        return (7, groups[0][1], groups[1][1])
    if [group[0] for group in groups] == [3, 2]:
        return (6, groups[0][1], groups[1][1])
    if flush:
        return (5, *sorted(ranks, reverse=True))
    if straight is not None:
        return (4, straight)
    if groups[0][0] == 3:
        kickers = sorted((rank for rank, count in counts.items() if count == 1), reverse=True)
        return (3, groups[0][1], *kickers)
    if [group[0] for group in groups[:2]] == [2, 2]:
        pairs = sorted((rank for rank, count in counts.items() if count == 2), reverse=True)
        kicker = next(rank for rank, count in counts.items() if count == 1)
        return (2, *pairs, kicker)
    if groups[0][0] == 2:
        kickers = sorted((rank for rank, count in counts.items() if count == 1), reverse=True)
        return (1, groups[0][1], *kickers)
    return (0, *sorted(ranks, reverse=True))


def best_hand_rank(cards: Sequence[Card]) -> tuple[int, ...]:
    """Evaluate the best five-card hand from five, six or seven cards."""
    if not 5 <= len(cards) <= 7 or len(set(cards)) != len(cards):
        raise ValueError("Expected five to seven distinct cards")
    return max(hand_rank(combo) for combo in combinations(cards, 5))


def pot_odds(call_amount: Decimal, pot_before_call: Decimal) -> Decimal:
    """Required showdown equity when calling an existing bet.

    `pot_before_call` includes all chips currently in the middle, but not
    the new hero call. For example calling 2 into a pot of 6 needs 25%.
    """
    if not call_amount.is_finite() or not pot_before_call.is_finite():
        raise ValueError("Amounts must be finite")
    if call_amount <= 0 or pot_before_call < 0:
        raise ValueError("Call must be positive and current pot nonnegative")
    return call_amount / (pot_before_call + call_amount)
