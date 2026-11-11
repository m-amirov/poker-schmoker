"""Conservative visual cues for the Pokerdom six-max action panel.

This is intentionally *not* card OCR or a strategy engine. It detects the
presence of the three distinctive action buttons in a calibrated full-window
frame, leaving uncertain and unrelated images unclassified.
"""

from dataclasses import dataclass
from typing import Callable, Literal

from PIL import Image


TurnState = Literal["hero_turn", "not_hero_turn", "unknown"]


@dataclass(frozen=True)
class ActionPanelObservation:
    state: TurnState
    confidence: float
    evidence: tuple[str, ...]


def _is_felt(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return green >= 55 and green > red * 1.6 and green > blue * 1.25


def _is_fold(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return green > 135 and green > red * 1.6 and green > blue * 1.3


def _is_middle(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return red > 140 and green > 95 and red > green * 1.05 and blue < red * .75


def _is_raise(rgb: tuple[int, int, int]) -> bool:
    red, green, blue = rgb
    return red > 145 and red > green * 2 and red > blue * 2


def _patch_match(
    image: Image.Image,
    center_x: float,
    center_y: float,
    predicate: Callable[[tuple[int, int, int]], bool],
) -> bool:
    matches = 0
    for dx in (-.012, 0, .012):
        for dy in (-.012, 0, .012):
            x = max(0, min(image.width - 1, round(image.width * (center_x + dx))))
            y = max(0, min(image.height - 1, round(image.height * (center_y + dy))))
            matches += predicate(image.getpixel((x, y)))
    return matches >= 5


def detect_action_panel(image: Image.Image) -> ActionPanelObservation:
    """Classify a full Pokerdom table-window screenshot, not a cropped seat.

    This first calibrated skin recognizer must not be applied to arbitrary
    desktop windows as proof that the player can act: callers should select
    the table window and require a stable event over multiple frames.
    """
    if image.width < 320 or image.height < 240:
        return ActionPanelObservation("unknown", 0, ("frame_too_small",))
    rgb = image.convert("RGB")
    if not _patch_match(rgb, .5, .5, _is_felt):
        return ActionPanelObservation("unknown", .1, ("table_felt_not_confirmed",))

    cues = (
        ("fold_button", .35, _is_fold),
        ("check_or_call_button", .49, _is_middle),
        ("raise_button", .63, _is_raise),
    )
    observed = tuple(name for name, x, predicate in cues if _patch_match(rgb, x, .94, predicate))
    if len(observed) == len(cues):
        return ActionPanelObservation("hero_turn", .95, ("felt_confirmed", *observed))
    if not observed:
        return ActionPanelObservation("not_hero_turn", .8, ("felt_confirmed", "no_action_colors"))
    return ActionPanelObservation("unknown", .3, ("felt_confirmed", *observed, "partial_panel"))
