#!/usr/bin/env python3
"""patch-sprite-canvas.py — 修复桌宠长时间挂起后播放动画时"人物消失一小会儿"

根因:精灵图通过 CSS background-image + background-position 渲染。macOS 挂起
不可见 WebView 后,WebKit 会丢弃已解码的图片数据;唤醒后第一次切帧时,CSS 背景
是异步重新解码的,解码完成前先合成一片空白 —— 人物消失一瞬间。

修复:改用 canvas 2d 渲染。canvas drawImage 对未解码图片是同步重新解码,
不会出现空白帧;CSS 背景路径保留为图片加载完成前的回退。

改动(幂等,可重复执行):
1. 新增 ensurePetCanvas / loadSpriteSheetImage 辅助函数,render() 优先走 canvas;
2. 应用 spritesheet manifest 时初始化 canvas 并预载精灵图;
3. visibilitychange 唤醒处理里补一次 render(),恢复可见时立即同步重绘。

用法:
    python3 scripts/patch-sprite-canvas.py [--appdata <Kimi应用数据目录> | <index.html 路径>]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, bump_widget_updated_at, find_pet_widget_id

OLD_RENDER = (
    "    function render() {\n"
    "      if (!manifest || isRiveManifest(manifest)) return;\n"
    "      const atlas = manifest.atlas;\n"
    "      const state = manifest.states[stateName] || manifest.states.idle;\n"
    "      const safeFrame = reducedMotion.matches ? 0 : frame % state.frames;\n"
    "      pet.style.backgroundPosition =\n"
    "        String(-safeFrame * atlas.frameWidth) + 'px ' + String(-state.row * atlas.frameHeight) + 'px';\n"
    "    }"
)
NEW_RENDER = (
    "    let spriteSheetImage = null;\n"
    "    let petCanvas = null;\n"
    "    let petCanvasCtx = null;\n"
    "\n"
    "    function ensurePetCanvas(atlas) {\n"
    "      if (!petCanvas) {\n"
    "        petCanvas = document.createElement('canvas');\n"
    "        petCanvas.style.position = 'absolute';\n"
    "        petCanvas.style.left = '0';\n"
    "        petCanvas.style.top = '0';\n"
    "        petCanvas.style.width = '100%';\n"
    "        petCanvas.style.height = '100%';\n"
    "        petCanvas.style.pointerEvents = 'none';\n"
    "        petCanvas.style.imageRendering = 'pixelated';\n"
    "        pet.appendChild(petCanvas);\n"
    "        petCanvasCtx = petCanvas.getContext('2d');\n"
    "        petCanvasCtx.imageSmoothingEnabled = false;\n"
    "      }\n"
    "      if (petCanvas.width !== atlas.frameWidth) petCanvas.width = atlas.frameWidth;\n"
    "      if (petCanvas.height !== atlas.frameHeight) petCanvas.height = atlas.frameHeight;\n"
    "    }\n"
    "\n"
    "    function loadSpriteSheetImage(fileName) {\n"
    "      spriteSheetImage = null;\n"
    "      const image = new Image();\n"
    "      image.addEventListener('load', () => {\n"
    "        spriteSheetImage = image;\n"
    "        pet.style.backgroundImage = 'none';\n"
    "        render();\n"
    "      });\n"
    "      image.src = '/workspace/' + encodeURIComponent(fileName);\n"
    "    }\n"
    "\n"
    "    function render() {\n"
    "      if (!manifest || isRiveManifest(manifest)) return;\n"
    "      const atlas = manifest.atlas;\n"
    "      const state = manifest.states[stateName] || manifest.states.idle;\n"
    "      const safeFrame = reducedMotion.matches ? 0 : frame % state.frames;\n"
    "      if (spriteSheetImage && petCanvasCtx) {\n"
    "        petCanvasCtx.clearRect(0, 0, atlas.frameWidth, atlas.frameHeight);\n"
    "        petCanvasCtx.drawImage(\n"
    "          spriteSheetImage,\n"
    "          safeFrame * atlas.frameWidth,\n"
    "          state.row * atlas.frameHeight,\n"
    "          atlas.frameWidth,\n"
    "          atlas.frameHeight,\n"
    "          0,\n"
    "          0,\n"
    "          atlas.frameWidth,\n"
    "          atlas.frameHeight\n"
    "        );\n"
    "        return;\n"
    "      }\n"
    "      pet.style.backgroundPosition =\n"
    "        String(-safeFrame * atlas.frameWidth) + 'px ' + String(-state.row * atlas.frameHeight) + 'px';\n"
    "    }"
)

OLD_APPLY = (
    "        pet.style.width = String(value.atlas.frameWidth) + 'px';\n"
    "        pet.style.height = String(value.atlas.frameHeight) + 'px';"
)
NEW_APPLY = (
    "        pet.style.width = String(value.atlas.frameWidth) + 'px';\n"
    "        pet.style.height = String(value.atlas.frameHeight) + 'px';\n"
    "        ensurePetCanvas(value.atlas);\n"
    "        loadSpriteSheetImage(value.spritesheet);"
)

OLD_WAKE = (
    "    document.addEventListener('visibilitychange', () => {\n"
    "      if (document.hidden) return;\n"
    "      lastFrameAt = performance.now();\n"
    "      restartAnimationSchedule();\n"
    "    });"
)
NEW_WAKE = (
    "    document.addEventListener('visibilitychange', () => {\n"
    "      if (document.hidden) return;\n"
    "      lastFrameAt = performance.now();\n"
    "      render();\n"
    "      restartAnimationSchedule();\n"
    "    });"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="精灵图改 canvas 渲染,消除唤醒空白帧")
    parser.add_argument("index", nargs="?", default=None, help="直接指定渲染器 index.html 路径")
    parser.add_argument("--appdata", default=None, help="Kimi 应用数据目录(路径不符时手动指定)")
    args = parser.parse_args()

    if args.index:
        target = Path(args.index)
        base = widget_id = None
    else:
        base = blueprint_dir(args.appdata)
        widget_id = find_pet_widget_id(base)
        target = base / "widgets" / widget_id / "workspace" / "index.html"
    if not target.is_file():
        print(f"错误: 未找到 {target}", file=sys.stderr)
        return 1

    text = target.read_text(encoding="utf-8")

    if "ensurePetCanvas" in text:
        print("补丁已存在,无需重复应用。")
        return 0

    for name, old, new in (
        ("render 改 canvas 渲染", OLD_RENDER, NEW_RENDER),
        ("manifest 应用时初始化 canvas", OLD_APPLY, NEW_APPLY),
        ("唤醒时同步重绘", OLD_WAKE, NEW_WAKE),
    ):
        count = text.count(old)
        if count != 1:
            print(f"错误: [{name}] 锚点出现 {count} 次,预期 1 次,未修改。", file=sys.stderr)
            return 1
        text = text.replace(old, new)
        print("已应用:", name)

    target.write_text(text, encoding="utf-8")
    if base is not None:
        bump_widget_updated_at(base, widget_id)
    print("目标:", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
