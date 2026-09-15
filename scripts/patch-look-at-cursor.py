#!/usr/bin/env python3
"""patch-look-at-cursor.py — 精灵图桌宠的"视线跟随"补丁

spritesheet 宠物没有分方向的头部位图,本补丁用 CSS transform 近似"脑袋偏向":
鼠标在桌宠窗口内移动时,宠物会平滑地向光标方向倾斜/偏移,离开后回正。
对 Rive 宠物自动跳过(它们自带眼动状态机)。

用法:
    python3 scripts/patch-look-at-cursor.py [--appdata <Kimi应用数据目录> | <index.html 路径>]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, find_pet_widget_id

MARKER = "look-at-cursor"

INJECTION = r"""
    /* look-at-cursor: sprite pets lean toward the cursor */
    let lookRafId = 0;
    let lookBaseTransform = pet ? (pet.style.transform || '') : '';
    let lookTargetX = 0;
    let lookTargetY = 0;
    let lookCurrentX = 0;
    let lookCurrentY = 0;

    const lookOriginalResize = resize;
    resize = function () {
      lookOriginalResize();
      if (pet) lookBaseTransform = pet.style.transform || '';
    };

    function lookApply() {
      lookRafId = 0;
      if (!pet || isRiveManifest(manifest)) return;
      lookCurrentX += (lookTargetX - lookCurrentX) * 0.16;
      lookCurrentY += (lookTargetY - lookCurrentY) * 0.16;
      const settled =
        !lookTargetX && !lookTargetY &&
        Math.abs(lookCurrentX) < 0.05 && Math.abs(lookCurrentY) < 0.05;
      pet.style.transform = lookBaseTransform + (settled
        ? ''
        : ' translate(' + lookCurrentX.toFixed(2) + 'px,' + lookCurrentY.toFixed(2) +
          'px) rotate(' + (lookCurrentX * 0.22).toFixed(2) + 'deg)');
      if (!settled) lookRafId = requestAnimationFrame(lookApply);
    }

    function lookKick() {
      if (!lookRafId) lookRafId = requestAnimationFrame(lookApply);
    }

    function lookOnMove(event) {
      if (!pet || isRiveManifest(manifest)) return;
      const rect = pet.getBoundingClientRect();
      const atlasWidth = manifest.atlas ? manifest.atlas.frameWidth : rect.width;
      const scale = atlasWidth > 0 ? rect.width / atlasWidth : 1;
      const dx = event.clientX - (rect.left + rect.width / 2);
      const dy = event.clientY - (rect.top + rect.height / 2);
      const deadZone = Math.min(rect.width, rect.height) * 0.15;
      if (Math.hypot(dx, dy) <= deadZone) {
        lookTargetX = 0;
        lookTargetY = 0;
      } else {
        const angle = Math.atan2(dy, dx);
        const magnitude = Math.min(16, 6 + Math.hypot(dx, dy) * 0.03) / Math.max(scale, 0.2);
        lookTargetX = Math.cos(angle) * magnitude;
        lookTargetY = Math.sin(angle) * magnitude * 0.45;
      }
      lookKick();
    }

    document.addEventListener('mousemove', lookOnMove);
    document.addEventListener('mouseleave', () => {
      lookTargetX = 0;
      lookTargetY = 0;
      lookKick();
    });
"""

# 在 IIFE 结束(最后一个 "})();" + "</script>")之前注入,与既有补丁兼容
ANCHOR = "\n  })();\n  </script>"


def main() -> None:
    parser = argparse.ArgumentParser(description="精灵图桌宠视线跟随补丁")
    parser.add_argument("path", nargs="?", default=None, help="index.html 路径(直接指定页面文件)")
    parser.add_argument("--appdata", default=None, help="Kimi 应用数据目录(路径不符时手动指定)")
    args = parser.parse_args()

    if args.path:
        path = Path(args.path)
    else:
        base = blueprint_dir(args.appdata)
        widget_id = find_pet_widget_id(base)
        path = base / "widgets" / widget_id / "workspace/index.html"
    if not path.is_file():
        sys.exit(f"未找到桌宠页面 {path},请确认 Kimi Work 桌面端已运行过,"
                 f"或用 --appdata 指定应用数据目录")

    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        print("已打过补丁,跳过:", path)
        return
    idx = html.rfind(ANCHOR)
    if idx < 0:
        sys.exit("未找到注入锚点,桌宠页面结构可能已更新,请人工检查 index.html")

    patched = html[:idx] + INJECTION + html[idx:]
    path.write_text(patched, encoding="utf-8")
    print("✅ 已注入视线跟随补丁:", path)
    print("   重启 Kimi 应用后,鼠标在桌宠附近移动时它会偏向光标方向(仅精灵图宠物)。")


if __name__ == "__main__":
    main()
