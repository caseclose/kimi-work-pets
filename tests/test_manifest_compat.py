#!/usr/bin/env python3
"""新版 Kimi Work 应用(2026-09 起)对桌宠 manifest 的强制校验:

- states.dragLeft / states.dragRight 必填(缺失时应用设置页读取桌宠状态失败,
  桌宠无法启用);
- provenance.provider 必须是 image_generation / pixellab / manual / other 之一。
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONVERTER = ROOT / "scripts" / "convert-codex-pet.py"
VALID_PROVIDERS = {"image_generation", "pixellab", "manual", "other"}


def bundled_manifests():
    for pet_json in sorted((ROOT / "pets").glob("*/pet.json")):
        yield pet_json.parent.name, json.loads(pet_json.read_text(encoding="utf-8"))


class BundledManifestCompatTests(unittest.TestCase):
    def test_all_bundled_pets_have_drag_states(self):
        for pet_id, manifest in bundled_manifests():
            with self.subTest(pet_id=pet_id):
                states = manifest["states"]
                self.assertIn("dragLeft", states)
                self.assertIn("dragRight", states)
                self.assertEqual(states["dragLeft"]["row"], states["running_left"]["row"])
                self.assertEqual(states["dragRight"]["row"], states["running_right"]["row"])

    def test_all_bundled_pets_have_valid_provenance_provider(self):
        for pet_id, manifest in bundled_manifests():
            with self.subTest(pet_id=pet_id):
                provider = manifest.get("provenance", {}).get("provider")
                self.assertIn(provider, VALID_PROVIDERS)


class ConverterCompatTests(unittest.TestCase):
    def test_converter_emits_drag_states_and_valid_provider(self):
        from PIL import Image, ImageDraw

        with tempfile.TemporaryDirectory() as temp:
            pet_dir = Path(temp)
            (pet_dir / "pet.json").write_text(
                json.dumps({"id": "compat-pet", "spritesheetPath": "spritesheet.png"}),
                encoding="utf-8",
            )
            image = Image.new("RGBA", (8 * 192, 9 * 208), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            for row in range(9):
                for column in range(8):
                    x, y = column * 192 + 80, row * 208 + 90
                    draw.rectangle((x, y, x + 8, y + 8), fill=(40, 120, 255, 255))
            image.save(pet_dir / "spritesheet.png")
            subprocess.run([sys.executable, str(CONVERTER), str(pet_dir)], check=True)
            manifest = json.loads((pet_dir / "pet.json").read_text(encoding="utf-8"))

        self.assertIn("dragLeft", manifest["states"])
        self.assertIn("dragRight", manifest["states"])
        self.assertEqual(
            manifest["states"]["dragLeft"]["row"], manifest["states"]["running_left"]["row"]
        )
        self.assertEqual(
            manifest["states"]["dragRight"]["row"], manifest["states"]["running_right"]["row"]
        )
        self.assertIn(manifest["provenance"]["provider"], VALID_PROVIDERS)


if __name__ == "__main__":
    unittest.main()
