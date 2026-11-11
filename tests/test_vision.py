import unittest

from PIL import Image, ImageDraw

from poker_schmoker.vision import detect_action_panel


def table_frame(width: int, height: int, buttons: bool = True) -> Image.Image:
    image = Image.new("RGB", (width, height), (45, 34, 40))
    draw = ImageDraw.Draw(image)
    draw.rectangle((int(width * .18), int(height * .23), int(width * .82), int(height * .77)), fill=(6, 101, 60))
    if buttons:
        for x, rgb in ((.35, (36, 186, 96)), (.49, (230, 160, 12)), (.63, (225, 45, 55))):
            draw.rectangle(
                (int(width * (x - .06)), int(height * .91), int(width * (x + .06)), int(height * .98)),
                fill=rgb,
            )
    return image


class VisionTests(unittest.TestCase):
    def test_hero_turn_with_three_action_colors(self):
        observation = detect_action_panel(table_frame(800, 680))
        self.assertEqual(observation.state, "hero_turn")
        self.assertGreaterEqual(observation.confidence, .9)

    def test_scaled_window_preserves_detection(self):
        observation = detect_action_panel(table_frame(1280, 960))
        self.assertEqual(observation.state, "hero_turn")

    def test_felt_without_action_bar_is_not_hero_turn(self):
        observation = detect_action_panel(table_frame(800, 680, buttons=False))
        self.assertEqual(observation.state, "not_hero_turn")

    def test_unrelated_desktop_abstains(self):
        observation = detect_action_panel(Image.new("RGB", (800, 680), (100, 100, 100)))
        self.assertEqual(observation.state, "unknown")

    def test_partial_action_bar_abstains(self):
        image = table_frame(800, 680)
        draw = ImageDraw.Draw(image)
        draw.rectangle((int(800 * .43), int(680 * .91), int(800 * .55), int(680 * .98)), fill=(45, 34, 40))
        self.assertEqual(detect_action_panel(image).state, "unknown")


if __name__ == "__main__":
    unittest.main()
