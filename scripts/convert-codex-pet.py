#!/usr/bin/env python3
"""convert-codex-pet.py — 把 Codex 社区宠物包转换为 Kimi Work 精灵图格式

Codex 社区包格式(codexpets.net / petdex.dev / awesome-codex-pet):
    pet.json: { "id", "displayName", "description", "spritesheetPath", "kind" }
    v1 spritesheet.webp: 8 列 × 9 行,192×208 单元格(1536×1872)
    v2 spritesheet.webp: 8 列 × 11 行,后两行是 16 个视线方向(1536×2288)

前九行的标准语义:
    0 idle        1 running_right  2 running_left  3 waving   4 jumping
    5 failed      6 waiting        7 running       8 review

用法:
    python3 scripts/convert-codex-pet.py <宠物包目录>

行为:
    - 原 pet.json 备份为 pet.codex.json(已存在则不覆盖)
    - 按每行实际非空帧数生成 Kimi Work 状态的 pet.json(原地覆盖)
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

COLS, BASE_ROWS, V2_ROWS = 8, 9, 11
CELL_W, CELL_H = 192, 208

# Kimi Work 状态 <- Codex 行号
STATE_ROWS = {
    "idle": 0,
    "running_right": 1,
    "running_left": 2,
    "idle_random_1": 3,   # waving,空闲彩蛋
    "idle_random_2": 4,   # jumping,空闲彩蛋
    "failed": 5,
    "waiting": 6,
    "working": 7,         # codex "running"
    "idle_random_3": 8,   # codex "review"/react,互动彩蛋(眨眼/庆祝)
}

FPS = {
    "idle": 4,
    "working": 8,
    "waiting": 5,
    "running_left": 10,
    "running_right": 10,
    "failed": 6,
    "idle_random_1": 3,
    "idle_random_2": 6,
    "idle_random_3": 4,
}


def die(msg: str) -> "NoReturn":
    print(f"错误:{msg}", file=sys.stderr)
    sys.exit(1)


def count_frames_per_row(img: np.ndarray, rows: int) -> list[int]:
    h, w = img.shape[:2]
    fh, fw = h // rows, w // COLS
    counts = []
    for r in range(rows):
        row = []
        for c in range(COLS):
            cell = img[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw]
            row.append(int((cell[..., 3] > 10).sum()))
        counts.append(row)
    frames = []
    for row in counts:
        last = 0
        for i in range(COLS - 1, -1, -1):
            if row[i] > 0:
                last = i + 1
                break
        frames.append(last)
    return frames


def make_look_directions() -> dict:
    """Codex v2 的角度约定:0° 朝上,顺时针每 22.5° 一帧。"""
    frames = []
    for index in range(16):
        frames.append({
            "angle": index * 22.5,
            "row": 9 + index // COLS,
            "column": index % COLS,
        })
    return {
        "zeroDirection": "up",
        "clockwise": True,
        "deadZoneRatio": 0.15,
        "frames": frames,
    }


def has_complete_look_grid(img: np.ndarray) -> bool:
    """v2 必须包含两个完整的 8 帧方向行，不能只检查最后一格。"""
    for row in range(BASE_ROWS, V2_ROWS):
        for column in range(COLS):
            cell = img[
                row * CELL_H:(row + 1) * CELL_H,
                column * CELL_W:(column + 1) * CELL_W,
            ]
            if not np.any(cell[..., 3] > 10):
                return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a Codex pet package to Kimi Work format")
    parser.add_argument("pet_dir", help="包含 pet.json 与 spritesheet 的目录")
    args = parser.parse_args()

    d = Path(args.pet_dir)
    codex_manifest_path = d / "pet.json"
    if not codex_manifest_path.is_file():
        die(f"未找到 {codex_manifest_path}")
    codex = json.loads(codex_manifest_path.read_text(encoding="utf-8"))
    sheet_name = codex.get("spritesheetPath") or codex.get("spritesheet") or "spritesheet.webp"
    sheet_path = d / sheet_name
    if not sheet_path.is_file():
        die(f"未找到精灵图 {sheet_path}")

    img = Image.open(sheet_path).convert("RGBA")
    valid_sizes = {
        (COLS * CELL_W, BASE_ROWS * CELL_H): BASE_ROWS,
        (COLS * CELL_W, V2_ROWS * CELL_H): V2_ROWS,
    }
    rows = valid_sizes.get(img.size)
    if rows is None:
        expected = ", ".join(f"{COLS * CELL_W}x{r * CELL_H}" for r in (BASE_ROWS, V2_ROWS))
        die(f"精灵图尺寸 {img.size} 不符合标准尺寸 {expected},"
            f"请先用 scripts/inspect_spritesheet.py 确认布局")

    image_array = np.array(img)
    frames = count_frames_per_row(image_array, rows)
    print("每行实际帧数:", frames)

    if frames[0] == 0:
        die("第 0 行(idle)没有可用帧,无法转换")

    states = {}
    for name, row in STATE_ROWS.items():
        if frames[row] > 0:
            states[name] = {"row": row, "frames": frames[row], "fps": FPS[name], "loop": True}

    manifest = {
        "schemaVersion": 1,
        "id": codex.get("id") or d.name.lower(),
        "name": codex.get("displayName") or codex.get("name") or d.name,
        "description": codex.get("description", ""),
        "spritesheet": sheet_name,
        "atlas": {"frameWidth": CELL_W, "frameHeight": CELL_H, "columns": COLS, "rows": rows},
        "states": states,
        "theme": {
            "bubble": {"background": "#445F7E", "foreground": "#FFFFFF", "border": "#6D829A"}
        },
        "provenance": {
            "provider": "codex-pets-community",
            "summary": f"Converted from Codex community pet '{codex.get('id', d.name)}'",
        },
    }

    if rows == V2_ROWS:
        if not has_complete_look_grid(image_array):
            die("v2 精灵图的 16 个视线方向帧(第 9、10 行)不完整")
        manifest["spriteVersionNumber"] = 2
        manifest["lookDirections"] = make_look_directions()

    backup = d / "pet.codex.json"
    if not backup.exists():
        shutil.copy2(codex_manifest_path, backup)
        print(f"原清单已备份: {backup}")

    codex_manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"✅ 已生成 Kimi Work 格式清单: {codex_manifest_path}")
    print(f"   宠物: {manifest['name']} (id: {manifest['id']}), 状态: {', '.join(states)}")
    print(f"   下一步: python3 scripts/install.py {d}")


if __name__ == "__main__":
    main()
