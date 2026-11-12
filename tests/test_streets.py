import unittest

from poker_schmoker.cards import CardObservation
from poker_schmoker.model import Card
from poker_schmoker.streets import StreetTracker


def observed(board: list[str], hero: tuple[str, str] = ("Ts", "5c"), complete: bool = True):
    street = {0: "preflop", 3: "flop", 4: "turn", 5: "river"}.get(len(board), "unknown")
    return CardObservation(
        tuple(Card.parse(code) for code in hero),
        tuple(Card.parse(code) for code in board),
        street,
        complete,
    )


FLOP = ["9c", "6h", "Ac"]
TURN = FLOP + ["2s"]
RIVER = TURN + ["4c"]


class StreetTrackerTests(unittest.TestCase):
    def test_flop_turn_river_progression(self):
        tracker = StreetTracker()
        self.assertIsNone(tracker.push(observed([])))
        self.assertEqual(tracker.push(observed(FLOP)), "flop")
        self.assertEqual(tracker.push(observed(TURN)), "turn")
        self.assertEqual(tracker.push(observed(RIVER)), "river")

    def test_repeated_frame_does_not_emit_duplicate_street(self):
        tracker = StreetTracker()
        tracker.push(observed(FLOP))
        self.assertIsNone(tracker.push(observed(FLOP)))

    def test_unknown_frame_resets_transition_claim(self):
        tracker = StreetTracker()
        tracker.push(observed(FLOP))
        self.assertIsNone(tracker.push(observed(TURN, complete=False)))
        self.assertIsNone(tracker.push(observed(TURN)))

    def test_hero_change_prevents_cross_hand_transition(self):
        tracker = StreetTracker()
        tracker.push(observed(FLOP))
        self.assertIsNone(tracker.push(observed(TURN, hero=("Ah", "9d"))))

    def test_changed_board_prefix_prevents_transition(self):
        tracker = StreetTracker()
        tracker.push(observed(FLOP))
        self.assertIsNone(tracker.push(observed(["9c", "7h", "Ac", "2s"])))

    def test_reverse_street_resets(self):
        tracker = StreetTracker()
        tracker.push(observed(RIVER))
        self.assertIsNone(tracker.push(observed(FLOP)))


if __name__ == "__main__":
    unittest.main()
