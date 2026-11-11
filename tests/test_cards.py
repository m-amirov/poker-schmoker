import unittest
import warnings

from PIL import Image, ImageDraw

from poker_schmoker.cards import detect_card_boxes


def synthetic_table(board_count: int = 3) -> Image.Image:
    image = Image.new("RGB", (813, 678), (45, 34, 40))
    draw = ImageDraw.Draw(image)
    draw.ellipse((35, 140, 775, 560), fill=(3, 100, 54))
    for left in (345, 405):
        draw.rectangle((left, 483, left + 55, 560), fill=(231, 231, 231))
    for i in range(board_count):
        left = 256 + i * 60
        draw.rectangle((left, 297, left + 55, 374), fill=(231, 231, 231))
    return image


class FaceBoxTests(unittest.TestCase):
    def test_detects_two_hero_faces(self):
        boxes = detect_card_boxes(synthetic_table(), "hero")
        self.assertEqual([(b.left, b.top, b.right, b.bottom) for b in boxes],
                         [(345, 483, 401, 561), (405, 483, 461, 561)])

    def test_detects_three_four_and_five_board_faces(self):
        for count in (3, 4, 5):
            with self.subTest(count=count):
                boxes = detect_card_boxes(synthetic_table(count), "board")
                self.assertEqual(len(boxes), count)

    def test_does_not_count_dark_card_back(self):
        image = synthetic_table(0)
        draw = ImageDraw.Draw(image)
        draw.rectangle((256, 297, 311, 374), fill=(85, 32, 58))
        self.assertEqual(detect_card_boxes(image, "board"), ())

    def test_tiny_bright_fragment_not_detected(self):
        image = synthetic_table(0)
        draw = ImageDraw.Draw(image)
        draw.rectangle((256, 297, 265, 374), fill=(231, 231, 231))
        self.assertEqual(detect_card_boxes(image, "board"), ())

    def test_card_text_holes_do_not_split_face(self):
        image = synthetic_table(3)
        draw = ImageDraw.Draw(image)
        draw.rectangle((260, 302, 276, 330), fill=(25, 27, 30))
        self.assertEqual(len(detect_card_boxes(image, "board")), 3)

    def test_card_detection_uses_non_deprecated_pillow_api(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            self.assertEqual(len(detect_card_boxes(synthetic_table(), "hero")), 2)

    def test_small_window_keeps_entire_hero_card(self):
        image = Image.new("RGB", (710, 575), (45, 34, 40))
        draw = ImageDraw.Draw(image)
        draw.ellipse((35, 130, 690, 520), fill=(3, 100, 54))
        for left in (281, 341):
            draw.rectangle((left, 419, left + 55, 496), fill=(231, 231, 231))
        boxes = detect_card_boxes(image, "hero")
        self.assertEqual([(box.left, box.top, box.right, box.bottom) for box in boxes],
                         [(281, 419, 337, 497), (341, 419, 397, 497)])


if __name__ == "__main__":
    unittest.main()
