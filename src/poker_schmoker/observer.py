"""Debounce vision observations to avoid acting on a single animation frame."""

from .vision import ActionPanelObservation


class TurnDebouncer:
    def __init__(self, required: int = 2) -> None:
        if required < 1:
            raise ValueError("required must be positive")
        self.required = required
        self._streak = 0
        self._notified = False

    def push(self, observation: ActionPanelObservation) -> bool:
        if observation.state != "hero_turn" or observation.confidence < .9:
            self._streak = 0
            self._notified = False
            return False
        self._streak += 1
        if self._streak >= self.required and not self._notified:
            self._notified = True
            return True
        return False
