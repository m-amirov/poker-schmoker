import json
from importlib.resources import files
import unittest

from PIL import Image, ImageDraw

from poker_schmoker.cards import CardBox, observe_cards, read_card
from poker_schmoker.model import Card


def glyphs() -> dict:
    resource = files("poker_schmoker").joinpath("data/card_glyphs.json")
    return json.loads(resource.read_text(encoding="utf-8"))


def draw_mask(image: Image.Image, rows: list[str], x: int, y: int, color: tuple[int, int, int]):
    for dy, row in enumerate(rows):
        for dx, bit in enumerate(row):
            if bit == "1":
                image.putpixel((x + dx, y + dy), color)


def render_card(rank: str, suit: str) -> Image.Image:
    data = glyphs()
    template_rank = "10" if rank == "T" else rank
    card = Image.new("RGB", (56, 78), (231, 231, 231))
    draw_mask(card, data["ranks"][template_rank], 2, 2, (33, 35, 38))
    suit_color = (187, 35, 67) if suit in "hd" else (33, 35, 38)
    draw_mask(card, data["suits"][suit], 2, 31, suit_color)
    return card


def table_with_cards(hero: list[str], board: list[str]) -> Image.Image:
    image = Image.new("RGB", (813, 678), (45, 34, 40))
    ImageDraw.Draw(image).ellipse((35, 140, 775, 560), fill=(3, 100, 54))
    for i, code in enumerate(hero):
        image.paste(render_card(code[:-1], code[-1]), (345 + i * 60, 483))
    for i, code in enumerate(board):
        image.paste(render_card(code[:-1], code[-1]), (256 + i * 60, 297))
    return image


class CardGlyphTests(unittest.TestCase):
    def test_rank_and_suit_are_recognized_independently(self):
        for code in ("Ac", "Ah", "Ts", "Td", "9c", "6h", "2s", "4c", "5c"):
            with self.subTest(code=code):
                image = render_card(code[:-1], code[-1])
                self.assertEqual(read_card(image, CardBox(0, 0, 56, 78)), Card.parse(code))

    def test_blank_face_is_unknown(self):
        image = Image.new("RGB", (56, 78), (231, 231, 231))
        self.assertIsNone(read_card(image, CardBox(0, 0, 56, 78)))

    def test_full_flop_cards_are_observed(self):
        observed = observe_cards(table_with_cards(["Ts", "5c"], ["9c", "6h", "Ac"]))
        self.assertEqual(observed.hero_cards, (Card.parse("Ts"), Card.parse("5c")))
        self.assertEqual(observed.board_cards, (Card.parse("9c"), Card.parse("6h"), Card.parse("Ac")))
        self.assertEqual(observed.street, "flop")
        self.assertTrue(observed.complete)

    def test_unsupported_board_card_count_is_unknown_street(self):
        observed = observe_cards(table_with_cards(["Ts", "5c"], ["9c"]))
        self.assertEqual(observed.street, "unknown")
        self.assertFalse(observed.complete)

    def test_duplicate_card_across_zones_is_not_accepted(self):
        observed = observe_cards(table_with_cards(["Ts", "5c"], ["9c", "6h", "Ts"]))
        self.assertFalse(observed.complete)
        self.assertNotEqual(observed.board_cards[-1], Card.parse("Ts"))


if __name__ == "__main__":
    unittest.main()
