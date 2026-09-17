#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CONVERTER = ROOT / "scripts" / "convert-codex-pet.py"
PATCHER = ROOT / "scripts" / "patch-look-at-cursor.py"


def load_patcher():
    spec = importlib.util.spec_from_file_location("patch_look_at_cursor", PATCHER)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def make_sheet(path: Path, rows: int) -> None:
    image = Image.new("RGBA", (8 * 192, rows * 208), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for row in range(rows):
        for column in range(8):
            x, y = column * 192 + 80, row * 208 + 90
            draw.rectangle((x, y, x + 8, y + 8), fill=(40, 120, 255, 255))
    image.save(path)


class V2ConversionTests(unittest.TestCase):
    def convert(self, rows: int) -> dict:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        pet_dir = Path(temp.name)
        (pet_dir / "pet.json").write_text(
            json.dumps({
                "id": "test-pet",
                "displayName": "Test Pet",
                "spritesheetPath": "spritesheet.png",
                "spriteVersionNumber": 2 if rows == 11 else 1,
            }),
            encoding="utf-8",
        )
        make_sheet(pet_dir / "spritesheet.png", rows)
        subprocess.run([sys.executable, str(CONVERTER), str(pet_dir)], check=True)
        return json.loads((pet_dir / "pet.json").read_text(encoding="utf-8"))

    def test_v2_converter_preserves_all_sixteen_directions(self):
        manifest = self.convert(11)
        self.assertEqual(manifest["atlas"]["rows"], 11)
        self.assertEqual(manifest["spriteVersionNumber"], 2)
        frames = manifest["lookDirections"]["frames"]
        self.assertEqual(len(frames), 16)
        self.assertEqual(frames[0], {"angle": 0.0, "row": 9, "column": 0})
        self.assertEqual(frames[8], {"angle": 180.0, "row": 10, "column": 0})
        self.assertEqual(frames[-1], {"angle": 337.5, "row": 10, "column": 7})

    def test_v1_converter_remains_backward_compatible(self):
        manifest = self.convert(9)
        self.assertEqual(manifest["atlas"]["rows"], 9)
        self.assertNotIn("lookDirections", manifest)
        self.assertNotIn("spriteVersionNumber", manifest)

    def test_bundled_v2_pets_are_complete(self):
        for pet_id in ("dimo", "yoimiya"):
            with self.subTest(pet_id=pet_id):
                pet_dir = ROOT / "pets" / pet_id
                manifest = json.loads((pet_dir / "pet.json").read_text(encoding="utf-8"))
                with Image.open(pet_dir / "spritesheet.webp") as image:
                    self.assertEqual(image.size, (1536, 2288))
                self.assertEqual(manifest["spriteVersionNumber"], 2)
                self.assertEqual(manifest["atlas"]["rows"], 11)
                self.assertEqual(len(manifest["lookDirections"]["frames"]), 16)


class LookPatchTests(unittest.TestCase):
    def test_patch_is_idempotent_for_an_explicit_page(self):
        patcher = load_patcher()
        with tempfile.TemporaryDirectory() as temp:
            page = Path(temp) / "index.html"
            page.write_text("<script>\n  (() => {\n  })();\n  </script>", encoding="utf-8")
            subprocess.run([sys.executable, str(PATCHER), str(page)], check=True)
            once = page.read_text(encoding="utf-8")
            subprocess.run([sys.executable, str(PATCHER), str(page)], check=True)
            self.assertEqual(page.read_text(encoding="utf-8"), once)
            self.assertEqual(once.count(patcher.MARKER), 1)

    def test_legacy_patch_is_upgraded_in_place(self):
        patcher = load_patcher()
        with tempfile.TemporaryDirectory() as temp:
            page = Path(temp) / "index.html"
            page.write_text(
                "<script>\n  (() => {" + patcher.LEGACY_INJECTION + "\n  })();\n  </script>",
                encoding="utf-8",
            )
            subprocess.run([sys.executable, str(PATCHER), str(page)], check=True)
            upgraded = page.read_text(encoding="utf-8")
            self.assertIn(patcher.MARKER, upgraded)
            self.assertNotIn(patcher.LEGACY_MARKER, upgraded)

    def test_cardinal_pointer_positions_select_v2_atlas_frames(self):
        injection = load_patcher().INJECTION
        manifest = json.loads((ROOT / "pets" / "dimo" / "pet.json").read_text(encoding="utf-8"))
        harness = f"""
const calls = [];
const listeners = {{}};
const document = {{addEventListener: (name, callback) => listeners[name] = callback}};
const pet = {{
  style: {{transform: '', backgroundPosition: ''}},
  getBoundingClientRect: () => ({{left: 0, top: 0, width: 200, height: 200}})
}};
let manifest = {json.dumps(manifest)};
let preferredStateName = 'idle';
let interactionStateActive = false;
let spriteSheetImage = {{}};
let petCanvasCtx = {{
  clearRect: () => {{}},
  drawImage: (...args) => calls.push([args[1], args[2]])
}};
let render = () => calls.push(['original']);
let resize = () => {{}};
const isRiveManifest = () => false;
const requestAnimationFrame = (callback) => {{ callback(); return 1; }};
{injection}
for (const point of [[100, 0], [200, 100], [100, 200], [0, 100]]) {{
  listeners.mousemove({{clientX: point[0], clientY: point[1]}});
}}
console.log(JSON.stringify(calls));
"""
        result = subprocess.run(
            ["node", "-e", harness], check=True, capture_output=True, text=True
        )
        self.assertEqual(
            json.loads(result.stdout),
            [[0, 1872], [768, 1872], [0, 2080], [768, 2080]],
        )


if __name__ == "__main__":
    unittest.main()
