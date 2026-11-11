import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "poker_schmoker", *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )


class CliTests(unittest.TestCase):
    def test_missing_screenshot_returns_error(self):
        result = run_cli("inspect", "file-that-does-not-exist.png")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Could not read screenshot", result.stderr)

    def test_image_without_pokerdom_table_is_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "desktop.png"
            Image.new("RGB", (800, 680), (110, 110, 110)).save(path)
            result = run_cli("inspect", str(path))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["state"], "unknown")

    def test_inspect_can_crop_a_table_inside_desktop_screenshot(self):
        desktop = Image.new("RGB", (1600, 900), (100, 100, 100))
        table = Image.new("RGB", (800, 680), (45, 34, 40))
        draw = ImageDraw.Draw(table)
        draw.rectangle((150, 150, 650, 500), fill=(6, 101, 60))
        for x, color in ((.35, (36, 186, 96)), (.49, (230, 160, 12)), (.63, (225, 45, 55))):
            draw.rectangle((int(800 * (x - .06)), 620, int(800 * (x + .06)), 666), fill=color)
        desktop.paste(table, (400, 120))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "desktop.png"
            desktop.save(path)
            result = run_cli("inspect", str(path), "--bbox", "400,120,1200,800")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["state"], "hero_turn")

    def test_private_screenshot_directory_is_gitignored(self):
        result = subprocess.run(
            ["git", "check-ignore", "local_samples/example.png"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
