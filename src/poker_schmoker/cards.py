"""Locate face-up card rectangles on a calibrated Pokerdom table skin."""

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files
import json
from typing import Literal

from PIL import Image

from .model import Card


Zone = Literal["hero", "board"]
_REGIONS = {
    "hero": (.30, .68, .70, .89),
    "board": (.18, .40, .82, .58),
}


@dataclass(frozen=True, order=True)
class CardBox:
    left: int
    top: int
    right: int
    bottom: int

    def crop(self, image: Image.Image) -> Image.Image:
        return image.crop((self.left, self.top, self.right, self.bottom))


@dataclass(frozen=True)
class CardObservation:
    hero_cards: tuple[Card | None, ...]
    board_cards: tuple[Card | None, ...]
    street: Literal["preflop", "flop", "turn", "river", "unknown"]
    complete: bool


def _light_components(image: Image.Image) -> list[tuple[int, int, int, int, int]]:
    """Return (pixel_count, minx, miny, maxx, maxy), local coordinates."""
    width, height = image.size
    pixels = image.convert("RGB").tobytes()
    light = bytearray(
        1 if min(pixels[i:i + 3]) > 175 and max(pixels[i:i + 3]) - min(pixels[i:i + 3]) < 35 else 0
        for i in range(0, len(pixels), 3)
    )
    components = []
    for start in range(len(light)):
        if not light[start]:
            continue
        light[start] = 0
        pending = deque((start,))
        count = 0
        min_x, min_y = width, height
        max_x = max_y = 0
        while pending:
            index = pending.popleft()
            y, x = divmod(index, width)
            count += 1
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            for neighbor in (
                index - 1 if x > 0 else -1,
                index + 1 if x + 1 < width else -1,
                index - width if y > 0 else -1,
                index + width if y + 1 < height else -1,
            ):
                if neighbor >= 0 and light[neighbor]:
                    light[neighbor] = 0
                    pending.append(neighbor)
        components.append((count, min_x, min_y, max_x + 1, max_y + 1))
    return components


def detect_card_boxes(image: Image.Image, zone: Zone) -> tuple[CardBox, ...]:
    """Find entire light card faces, omitting backs and small bright fragments."""
    if zone not in _REGIONS:
        raise ValueError(f"Unknown card zone: {zone}")
    if image.width < 320 or image.height < 240:
        return ()
    x0, y0, x1, y1 = _REGIONS[zone]
    left, top = int(x0 * image.width), int(y0 * image.height)
    right, bottom = int(x1 * image.width), int(y1 * image.height)
    roi = image.crop((left, top, right, bottom))
    boxes = []
    for area, lx, ty, rx, by in _light_components(roi):
        width, height = rx - lx, by - ty
        if not (.04 * image.width <= width <= .12 * image.width):
            continue
        if not (.06 * image.height <= height <= .20 * image.height):
            continue
        if not (.60 <= width / height <= .85):
            continue
        if area < width * height * .45:
            continue
        boxes.append(CardBox(left + lx, top + ty, left + rx, top + by))
    return tuple(sorted(boxes, key=lambda box: box.left))


@lru_cache(maxsize=1)
def _glyph_data() -> dict:
    text = files("poker_schmoker").joinpath("data/card_glyphs.json").read_text(encoding="utf-8")
    return json.loads(text)


def _find_glyph(
    face: Image.Image,
    offset: tuple[int, int],
    width: int,
    height: int,
    templates: dict[str, list[str]],
) -> str | None:
    gray = face.convert("L").crop((offset[0], offset[1], offset[0] + width, offset[1] + height))
    observed = [value < 175 for value in gray.tobytes()]
    if len(observed) != width * height:
        return None
    matches = []
    for key, rows in templates.items():
        template = [bit == "1" for row in rows for bit in row]
        if len(template) != len(observed):
            continue
        distance = sum(a != b for a, b in zip(observed, template)) / len(template)
        matches.append((distance, key))
    if not matches:
        return None
    matches.sort()
    best_distance, name = matches[0]
    second_distance = matches[1][0] if len(matches) > 1 else 1.0
    if best_distance > .035 or second_distance - best_distance < .02:
        return None
    return name


def read_card(image: Image.Image, box: CardBox) -> Card | None:
    """Read a known glyph from a detected card face; never guess unknowns."""
    face = box.crop(image).convert("RGB")
    if face.size != (56, 78):
        face = face.resize((56, 78), Image.Resampling.BILINEAR)
    data = _glyph_data()
    rank = _find_glyph(face, (2, 2), 30, 30, data["ranks"])
    suit = _find_glyph(face, (2, 31), 18, 19, data["suits"])
    if rank is None or suit is None:
        return None
    return Card.parse(("T" if rank == "10" else rank) + suit)


def observe_cards(image: Image.Image) -> CardObservation:
    """Return face-up card observations without filling gaps or duplicates."""
    hero = [read_card(image, box) for box in detect_card_boxes(image, "hero")]
    board = [read_card(image, box) for box in detect_card_boxes(image, "board")]
    seen: set[Card] = set()
    for observed in (hero, board):
        for index, card in enumerate(observed):
            if card is None:
                continue
            if card in seen:
                observed[index] = None
            else:
                seen.add(card)
    streets = {0: "preflop", 3: "flop", 4: "turn", 5: "river"}
    street = streets.get(len(board), "unknown")
    complete = (len(hero) == 2 and street != "unknown" and
                all(card is not None for card in hero + board))
    return CardObservation(tuple(hero), tuple(board), street, complete)
