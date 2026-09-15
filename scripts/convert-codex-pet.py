#!/usr/bin/env python3
"""convert-codex-pet.py — 把 Codex 社区宠物包转换为 Kimi Work 精灵图格式

Codex 社区包格式(codexpets.net / petdex.dev / awesome-codex-pet):
    pet.json: { "id", "displayName", "description", "spritesheetPath", "kind" }
    spritesheet.webp: 8 列 × 9 行,192×208 单元格(1536×1872)

九行的标准语义:
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

COLS, ROWS = 8, 9
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
    # row 8 "review"(完成庆祝)Kimi Work 无对应宿主状态,不映射
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
}


def die(msg: str) -> "NoReturn":
    print(f"错误:{msg}", file=sys.stderr)
    sys.exit(1)


def count_frames_per_row(img: np.ndarray) -> list[int]:
    h, w = img.shape[:2]
    fh, fw = h // ROWS, w // COLS
    counts = []
    for r in range(ROWS):
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
    if img.size != (COLS * CELL_W, ROWS * CELL_H):
        die(f"精灵图尺寸 {img.size} 不符合标准 {COLS*CELL_W}x{ROWS*CELL_H},"
            f"请先用 scripts/inspect_spritesheet.py 确认布局")

    frames = count_frames_per_row(np.array(img))
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
        "atlas": {"frameWidth": CELL_W, "frameHeight": CELL_H, "columns": COLS, "rows": ROWS},
        "states": states,
        "theme": {
            "bubble": {"background": "#445F7E", "foreground": "#FFFFFF", "border": "#6D829A"}
        },
        "provenance": {
            "provider": "codex-pets-community",
            "summary": f"Converted from Codex community pet '{codex.get('id', d.name)}'",
        },
    }

    backup = d / "pet.codex.json"
    if not backup.exists():
        shutil.copy2(codex_manifest_path, backup)
        print(f"原清单已备份: {backup}")

    codex_manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"✅ 已生成 Kimi Work 格式清单: {codex_manifest_path}")
    print(f"   宠物: {manifest['name']} (id: {manifest['id']}), 状态: {', '.join(states)}")
    print("   下一步: bash scripts/install.sh", d)


if __name__ == "__main__":
    main()
