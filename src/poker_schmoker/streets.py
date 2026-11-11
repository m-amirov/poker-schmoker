"""Conservative transitions through one observed Hold'em board."""

from .cards import CardObservation


class StreetTracker:
    def __init__(self) -> None:
        self._previous: CardObservation | None = None

    def push(self, observation: CardObservation) -> str | None:
        if not observation.complete or observation.street == "unknown":
            self._previous = None
            return None
        previous = self._previous
        self._previous = observation
        if previous is None:
            return None
        if previous.hero_cards != observation.hero_cards:
            return None
        old, new = previous.board_cards, observation.board_cards
        if len(new) <= len(old) or new[:len(old)] != old:
            return None
        if (len(old), len(new)) in {(0, 3), (3, 4), (3, 5), (4, 5)}:
            return observation.street
        return None
