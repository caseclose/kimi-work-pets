#!/usr/bin/env python3
"""patch-look-at-cursor.py — 精灵图桌宠的"视线跟随"补丁

Codex v2 宠物若在 manifest.lookDirections 中声明 16 个方向帧,会按光标相对
宠物中心的角度直接渲染对应帧。普通 v1 spritesheet 则继续用 CSS transform
近似"脑袋偏向"。鼠标离开或任务/互动状态开始时自动回到正常动画。
对 Rive 宠物自动跳过(它们自带眼动状态机)。

用法:
    python3 scripts/patch-look-at-cursor.py [--appdata <Kimi应用数据目录> | <index.html 路径>]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, bump_widget_updated_at, find_pet_widget_id

MARKER = "look-at-cursor-v2"
LEGACY_MARKER = "look-at-cursor: sprite pets lean toward the cursor"

LEGACY_INJECTION = r"""
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

INJECTION = r"""
    /* look-at-cursor-v2: direction frames, with a transform fallback for v1 pets */
    let lookRafId = 0;
    let lookBaseTransform = pet ? (pet.style.transform || '') : '';
    let lookTargetX = 0;
    let lookTargetY = 0;
    let lookCurrentX = 0;
    let lookCurrentY = 0;
    let lookDirectionFrame = null;

    function lookDirectionConfig() {
      if (!manifest || isRiveManifest(manifest)) return null;
      const config = manifest.lookDirections;
      if (!config || !Array.isArray(config.frames) || config.frames.length !== 16) return null;
      return config;
    }

    function lookCanUseDirectionFrame() {
      return Boolean(
        lookDirectionFrame &&
        preferredStateName === 'idle' &&
        !interactionStateActive
      );
    }

    function lookRenderDirectionFrame(entry) {
      const atlas = manifest.atlas;
      const column = Number(entry.column);
      const row = Number(entry.row);
      if (!Number.isInteger(column) || !Number.isInteger(row) ||
          column < 0 || column >= atlas.columns || row < 0 || row >= atlas.rows) return false;
      if (typeof spriteSheetImage !== 'undefined' && spriteSheetImage &&
          typeof petCanvasCtx !== 'undefined' && petCanvasCtx) {
        petCanvasCtx.clearRect(0, 0, atlas.frameWidth, atlas.frameHeight);
        petCanvasCtx.drawImage(
          spriteSheetImage,
          column * atlas.frameWidth,
          row * atlas.frameHeight,
          atlas.frameWidth,
          atlas.frameHeight,
          0,
          0,
          atlas.frameWidth,
          atlas.frameHeight
        );
        return true;
      }
      pet.style.backgroundPosition =
        String(-column * atlas.frameWidth) + 'px ' + String(-row * atlas.frameHeight) + 'px';
      return true;
    }

    const lookOriginalRender = render;
    render = function () {
      if (lookCanUseDirectionFrame() && lookRenderDirectionFrame(lookDirectionFrame)) return;
      lookOriginalRender();
    };

    const lookOriginalResize = resize;
    resize = function () {
      lookOriginalResize();
      if (pet) lookBaseTransform = pet.style.transform || '';
    };

    function lookApply() {
      lookRafId = 0;
      if (!pet || isRiveManifest(manifest) || lookDirectionConfig()) return;
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
      const dx = event.clientX - (rect.left + rect.width / 2);
      const dy = event.clientY - (rect.top + rect.height / 2);
      const config = lookDirectionConfig();
      const deadZoneRatio = config && Number.isFinite(config.deadZoneRatio)
        ? config.deadZoneRatio
        : 0.15;
      const deadZone = Math.min(rect.width, rect.height) * deadZoneRatio;
      if (Math.hypot(dx, dy) <= deadZone) {
        lookDirectionFrame = null;
        lookTargetX = 0;
        lookTargetY = 0;
      } else if (config) {
        // Codex v2 uses 0° = up and increases clockwise in 22.5° steps.
        const degrees = (Math.atan2(dx, -dy) * 180 / Math.PI + 360) % 360;
        const index = Math.round(degrees / (360 / config.frames.length)) % config.frames.length;
        lookDirectionFrame = config.frames[index];
        lookTargetX = 0;
        lookTargetY = 0;
      } else {
        lookDirectionFrame = null;
        const atlasWidth = manifest.atlas ? manifest.atlas.frameWidth : rect.width;
        const scale = atlasWidth > 0 ? rect.width / atlasWidth : 1;
        const angle = Math.atan2(dy, dx);
        const magnitude = Math.min(16, 6 + Math.hypot(dx, dy) * 0.03) / Math.max(scale, 0.2);
        lookTargetX = Math.cos(angle) * magnitude;
        lookTargetY = Math.sin(angle) * magnitude * 0.45;
      }
      if (config) render();
      else lookKick();
    }

    document.addEventListener('mousemove', lookOnMove);
    document.addEventListener('mouseleave', () => {
      lookDirectionFrame = null;
      lookTargetX = 0;
      lookTargetY = 0;
      if (lookDirectionConfig()) render();
      else lookKick();
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
        base = widget_id = None
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
    if LEGACY_MARKER in html:
        if html.count(LEGACY_INJECTION) != 1:
            sys.exit("检测到旧视线补丁,但内容与已知版本不一致;请先 restore 后重新安装")
        patched = html.replace(LEGACY_INJECTION, INJECTION)
        action = "升级"
    else:
        idx = html.rfind(ANCHOR)
        if idx < 0:
            sys.exit("未找到注入锚点,桌宠页面结构可能已更新,请人工检查 index.html")
        patched = html[:idx] + INJECTION + html[idx:]
        action = "注入"
    path.write_text(patched, encoding="utf-8")
    if base is not None:
        bump_widget_updated_at(base, widget_id)
    print(f"✅ 已{action}视线跟随补丁:", path)
    print("   重启 Kimi 应用后,v2 宠物会切换 16 个方向帧;v1 宠物继续平滑偏向光标。")


if __name__ == "__main__":
    main()
