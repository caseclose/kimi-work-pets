#!/usr/bin/env python3
"""generate_previews.py — 从精灵图生成 README 用预览素材

用法:
    python3 scripts/generate_previews.py [--spritesheet pets/dimo/spritesheet.webp] [--out assets]

输出:
    pet-preview.png   待机帧 2x 预览图
    pet-states.gif    各状态带标注的演示动画
    pet-rows.png      9/11 行原始动作条带(逐行标注)
"""
import argparse
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# 中文字体回退:macOS -> Windows -> 无标注
FONT_CANDIDATES = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]
BG = (238, 243, 249)          # 浅色背景
LABEL_BG = (220, 230, 242)
TEXT = (45, 62, 82)

COLS, BASE_ROWS, V2_ROWS = 8, 9, 11
FW, FH = 192, 208

# 精灵图每行的语义(来自 Codex 社区规范)与 Kimi Work 状态映射
ROW_META = [
    ("row 0", "idle 待机", "idle"),
    ("row 1", "running_right 向右奔跑", "running_right"),
    ("row 2", "running_left 向左奔跑", "running_left"),
    ("row 3", "waving 招手", "idle_random_1"),
    ("row 4", "jumping 跳跃", "idle_random_2"),
    ("row 5", "failed 失败大哭", "failed"),
    ("row 6", "waiting 等待张望", "waiting"),
    ("row 7", "running 工作奔跑", "working"),
    ("row 8", "react 互动彩蛋", "idle_random_3"),
    ("row 9", "look 000°–157.5°", "视线方向 0–7"),
    ("row 10", "look 180°–337.5°", "视线方向 8–15"),
]

# 演示 GIF 中依次展示的状态: (行, 实际帧数, fps, 标注)
DEMO_STATES = [
    (0, 6, 4, "idle 待机"),
    (7, 6, 8, "working 工作中"),
    (6, 6, 5, "waiting 等待确认"),
    (1, 8, 10, "running_right 向右奔跑"),
    (5, 8, 6, "failed 任务失败"),
    (3, 4, 3, "idle 彩蛋 · 招手"),
    (4, 5, 6, "idle 彩蛋 · 跳跃"),
    (8, 8, 4, "idle 彩蛋 · 互动"),
]


_FONT_CACHE: dict[int, ImageFont.FreeTypeFont] = {}


def font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _FONT_CACHE:
        for candidate in FONT_CANDIDATES:
            if Path(candidate).is_file():
                _FONT_CACHE[size] = ImageFont.truetype(candidate, size)
                break
        else:
            _FONT_CACHE[size] = ImageFont.load_default()
    return _FONT_CACHE[size]


def flatten(frame: Image.Image, size=(FW, FH), bg=BG) -> Image.Image:
    canvas = Image.new("RGB", size, bg)
    canvas.paste(frame, (0, 0), frame)
    return canvas


def make_preview(sheet: Image.Image, out: Path) -> None:
    frame = sheet.crop((0, 0, FW, FH)).resize((FW * 2, FH * 2), Image.NEAREST)
    canvas = Image.new("RGB", (FW * 2 + 80, FH * 2 + 80), BG)
    canvas.paste(frame, (40, 40), frame)
    canvas.save(out / "pet-preview.png")
    print("written", out / "pet-preview.png")


def make_states_gif(sheet: Image.Image, out: Path, scale: int = 2) -> None:
    wf, hf = FW * scale, FH * scale
    bar = 40
    font_bar = font(22)

    def valid_frames(row: int) -> int:
        """该行实际有内容的帧数(裁剪 DEMO_STATES 里超出的空帧)。"""
        n = 0
        for c in range(COLS):
            cell = sheet.crop((c * FW, row * FH, (c + 1) * FW, (row + 1) * FH))
            if cell.getchannel("A").getextrema()[1] > 10:
                n = c + 1
        return n

    def labeled(label: str) -> Image.Image:
        canvas = Image.new("RGB", (wf, hf + bar), LABEL_BG)
        draw = ImageDraw.Draw(canvas)
        draw.text((14, 8), label, font=font_bar, fill=TEXT)
        return canvas

    frames, durations = [], []
    for row, count, fps, label in DEMO_STATES:
        count = min(count, valid_frames(row))
        if count == 0:
            continue
        holder = labeled(label)
        for c in range(count):
            cell = sheet.crop((c * FW, row * FH, (c + 1) * FW, (row + 1) * FH))
            cell = cell.resize((wf, hf), Image.NEAREST)
            canvas = holder.copy()
            canvas.paste(flatten(cell, (wf, hf)), (0, bar))
            frames.append(canvas)
            durations.append(int(1000 / fps))
        # 状态之间停顿 0.6s
        for _ in range(2):
            frames.append(holder.copy())
            durations.append(300)
    if sheet.height == V2_ROWS * FH:
        holder = labeled("look directions · 16 方向视线跟随")
        for index in range(16):
            row, column = 9 + index // COLS, index % COLS
            cell = sheet.crop((column * FW, row * FH, (column + 1) * FW, (row + 1) * FH))
            cell = cell.resize((wf, hf), Image.NEAREST)
            canvas = holder.copy()
            canvas.paste(flatten(cell, (wf, hf)), (0, bar))
            frames.append(canvas)
            durations.append(180)
    frames[0].save(
        out / "pet-states.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print("written", out / "pet-states.gif", f"({len(frames)} frames)")


def make_rows_png(sheet: Image.Image, out: Path, scale: float = 0.5) -> None:
    rows = sheet.height // FH
    tw, th = int(FW * scale), int(FH * scale)
    bar, pad = 30, 6
    width, height = tw + pad * 2, (th + bar + pad) * rows + pad
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    font_row = font(18)
    for r in range(rows):
        y0 = pad + r * (th + bar + pad)
        label, desc, mapped = ROW_META[r]
        draw.rectangle([0, y0, width, y0 + bar], fill=LABEL_BG)
        draw.text(
            (10, y0 + 5),
            f"{label} · {desc}    → Kimi Work 状态: {mapped}",
            font=font_row,
            fill=TEXT,
        )
        strip = sheet.crop((0, r * FH, COLS * FW, (r + 1) * FH)).resize((tw, th), Image.NEAREST)
        canvas.paste(flatten(strip, (tw, th)), (pad, y0 + bar))
    canvas.save(out / "pet-rows.png")
    print("written", out / "pet-rows.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spritesheet", default=str(Path(__file__).parent.parent / "pets/dimo/spritesheet.webp"))
    parser.add_argument("--out", default=str(Path(__file__).parent.parent / "assets"))
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(args.spritesheet).convert("RGBA")
    assert sheet.size in {
        (COLS * FW, BASE_ROWS * FH),
        (COLS * FW, V2_ROWS * FH),
    }, f"unexpected spritesheet size {sheet.size}"

    make_preview(sheet, out)
    make_states_gif(sheet, out)
    make_rows_png(sheet, out)


if __name__ == "__main__":
    main()
