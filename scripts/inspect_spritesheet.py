#!/usr/bin/env python3
"""inspect_spritesheet.py — 检查 Codex/Kimi 风格精灵图布局的小工具

用法:
    python3 inspect_spritesheet.py <spritesheet.webp> [--cols 8] [--rows 9] [--out out_dir]

输出:
    <out>/row_<r>.png          每行的横向帧条带(全分辨率)
    <out>/rows_overview.png    每行第 1 帧的缩略拼图
    终端打印每行每帧的非透明像素数(用于判断每行动画的实际帧数)
"""
import argparse
import os
import sys

from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect pet spritesheet layout")
    parser.add_argument("spritesheet")
    parser.add_argument("--cols", type=int, default=8)
    parser.add_argument("--rows", type=int, default=9)
    parser.add_argument("--out", default="spritesheet-report")
    args = parser.parse_args()

    im = Image.open(args.spritesheet).convert("RGBA")
    w, h = im.size
    fw, fh = w // args.cols, h // args.rows
    print(f"size={w}x{h} frame={fw}x{fh} grid={args.cols}x{args.rows}")
    if fw * args.cols != w or fh * args.rows != h:
        print("警告:图片尺寸不能被网格整除,请检查 --cols/--rows。", file=sys.stderr)

    os.makedirs(args.out, exist_ok=True)
    thumbs = []
    import numpy as np

    arr = np.array(im)
    for r in range(args.rows):
        im.crop((0, r * fh, w, (r + 1) * fh)).save(f"{args.out}/row_{r}.png")
        counts = []
        for c in range(args.cols):
            cell = arr[r * fh:(r + 1) * fh, c * fw:(c + 1) * fw]
            counts.append(int((cell[..., 3] > 10).sum()))
        print(f"row {r}: {counts}")
        thumbs.append(im.crop((0, r * fh, fw, (r + 1) * fh)).resize((max(fw // 2, 1), max(fh // 2, 1))))

    sheet = Image.new("RGBA", (max(fw // 2, 1), max(fh // 2, 1) * args.rows), (255, 255, 255, 255))
    for r, t in enumerate(thumbs):
        sheet.paste(t, (0, r * t.size[1]), t)
    sheet.save(f"{args.out}/rows_overview.png")
    print(f"报告已写入 {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
