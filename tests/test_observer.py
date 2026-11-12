import unittest

from poker_schmoker.observer import TurnDebouncer
from poker_schmoker.vision import ActionPanelObservation


def observation(state: str) -> ActionPanelObservation:
    return ActionPanelObservation(state, .95 if state == "hero_turn" else .8, ())


class ObserverTests(unittest.TestCase):
    def test_single_frame_does_not_trigger_turn(self):
        detector = TurnDebouncer(required=2)
        self.assertFalse(detector.push(observation("hero_turn")))

    def test_two_consistent_frames_trigger_once(self):
        detector = TurnDebouncer(required=2)
        self.assertFalse(detector.push(observation("hero_turn")))
        self.assertTrue(detector.push(observation("hero_turn")))
        self.assertFalse(detector.push(observation("hero_turn")))

    def test_turn_can_trigger_again_after_another_player_acts(self):
        detector = TurnDebouncer(required=2)
        for state in ("hero_turn", "hero_turn", "not_hero_turn", "hero_turn"):
            detector.push(observation(state))
        self.assertTrue(detector.push(observation("hero_turn")))

    def test_unknown_frame_resets_pending_streak(self):
        detector = TurnDebouncer(required=2)
        for state in ("hero_turn", "unknown", "hero_turn"):
            self.assertFalse(detector.push(observation(state)))
        self.assertTrue(detector.push(observation("hero_turn")))

    def test_bad_required_frame_count_is_rejected(self):
        with self.assertRaises(ValueError):
            TurnDebouncer(required=0)


if __name__ == "__main__":
    unittest.main()
