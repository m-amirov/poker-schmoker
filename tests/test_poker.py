import unittest
from decimal import Decimal

from poker_schmoker.model import Card
from poker_schmoker.poker import best_hand_rank, hand_rank, pot_odds


def cards(*codes: str) -> list[Card]:
    return [Card.parse(code) for code in codes]


class PokerMathTests(unittest.TestCase):
    def test_wheel_straight_has_five_high(self):
        self.assertEqual(hand_rank(cards("As", "2d", "3h", "4c", "5s")), (4, 5))

    def test_flush_beats_straight(self):
        flush = hand_rank(cards("As", "Qs", "9s", "7s", "3s"))
        straight = hand_rank(cards("9s", "8d", "7h", "6c", "5s"))
        self.assertGreater(flush, straight)

    def test_two_pair_kicker_breaks_ties(self):
        queen_kicker = hand_rank(cards("As", "Ad", "Kh", "Kc", "Qd"))
        jack_kicker = hand_rank(cards("As", "Ad", "Kh", "Kc", "Jd"))
        self.assertGreater(queen_kicker, jack_kicker)

    def test_best_seven_prefers_royal_flush(self):
        result = best_hand_rank(cards("As", "Ks", "Qs", "Js", "Ts", "2d", "3h"))
        self.assertEqual(result, (8, 14))

    def test_duplicate_card_is_rejected(self):
        with self.assertRaises(ValueError):
            best_hand_rank(cards("As", "As", "Qs", "Js", "Ts", "2d", "3h"))

    def test_invalid_card_code_is_rejected(self):
        for code in ("1s", "10s", "Ax", "ZZ", ""):
            with self.subTest(code=code), self.assertRaises(ValueError):
                Card.parse(code)

    def test_pot_odds(self):
        self.assertEqual(pot_odds(Decimal("2"), Decimal("6")), Decimal("0.25"))

    def test_pot_odds_rejects_non_positive_call(self):
        for amount in (Decimal("0"), Decimal("-2")):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                pot_odds(amount, Decimal("6"))

    def test_pot_odds_rejects_invalid_existing_pot(self):
        with self.assertRaises(ValueError):
            pot_odds(Decimal("2"), Decimal("-1"))


if __name__ == "__main__":
    unittest.main()
