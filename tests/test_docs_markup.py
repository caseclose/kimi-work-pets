#!/usr/bin/env python3
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
GUIDE = ROOT / "docs" / "how-kimi-work-pet-works.html"
SITEMAP = (ROOT / "docs" / "sitemap.xml").read_text(encoding="utf-8")


class DocsMarkupTests(unittest.TestCase):
    def test_mechanism_page_exists_and_is_linked(self):
        self.assertTrue(GUIDE.is_file())
        self.assertIn('href="how-kimi-work-pet-works.html"', INDEX)
        self.assertNotIn("how-kimi-work-pet-works.md", INDEX)
        self.assertIn("how-kimi-work-pet-works.html", SITEMAP)
        self.assertTrue((ROOT / "docs" / ".nojekyll").is_file())
        self.assertTrue((ROOT / "docs" / "assets" / "dimo" / "pet-rows.png").is_file())

    def test_filters_are_toggle_buttons_not_tabs(self):
        self.assertNotIn('role="tablist"', INDEX)
        self.assertIn('role="group"', INDEX)
        self.assertGreaterEqual(INDEX.count('aria-pressed="false"'), 3)
        self.assertIn('aria-pressed="true"', INDEX)

    def test_gallery_gifs_are_lazy_data_attributes(self):
        gifs = re.findall(r'data-gif="assets/[^"]+/pet-states\.gif"', INDEX)
        self.assertEqual(len(gifs), 14)
        self.assertIn(
            'src="assets/dimo/pet-preview.png" data-gif="assets/dimo/pet-states.gif"',
            INDEX,
        )
        self.assertIn('src="assets/dimo/pet-states.gif"', INDEX)

    def test_font_weights_are_standard(self):
        self.assertNotIn("font-weight: 750", INDEX)
        self.assertNotIn("font-weight: 650", INDEX)

    def test_hash_and_menu_and_gif_observers_exist(self):
        for needle in (
            "revealHashTarget",
            "hashchange",
            'event.key === "Escape"',
            "IntersectionObserver",
            "menuFocusables",
        ):
            self.assertIn(needle, INDEX)


if __name__ == "__main__":
    unittest.main()
