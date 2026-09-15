#!/usr/bin/env python3
"""patch-pet-display.py — 宠物显示 2 倍 + 悬停交互范围扩大补丁

两件事一次完成:
1. 显示 2 倍:在宿主 display-scale 消息的基础上把 displayScale 再乘 2
   (页面上限 DISPLAY_SCALE_MAX = 2,精灵图宠物不会超限);
2. 交互范围:上报给宿主的"可交互区域"(宠物矩形)外扩 24px,
   悬停/点击/拖动的响应范围随之扩大,无需精确对准宠物。

用法:
    python3 scripts/patch-pet-display.py [--appdata <Kimi应用数据目录> | <index.html 路径>]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, bump_widget_updated_at, find_pet_widget_id

MARKER = "pet-display-x2-range"

INJECTION = r"""
    /* pet-display-x2-range: 2x display scale + inflated interactive region */
    const PET_DISPLAY_SCALE_FACTOR = 2;
    const PET_INTERACTIVE_MARGIN_PX = 24;

    (function applyPetDisplayScale() {
      displayScale = Math.min(
        DISPLAY_SCALE_MAX,
        Math.max(DISPLAY_SCALE_MIN, displayScale * PET_DISPLAY_SCALE_FACTOR)
      );
      resize();
    })();

    addEventListener('message', (event) => {
      const data = event.data;
      if (!data || data.type !== DISPLAY_SCALE_MESSAGE_TYPE) return;
      // 宿主消息处理完后(监听器按注册顺序执行)再把缩放乘 2
      queueMicrotask(() => {
        displayScale = Math.min(
          DISPLAY_SCALE_MAX,
          Math.max(DISPLAY_SCALE_MIN, displayScale * PET_DISPLAY_SCALE_FACTOR)
        );
        resize();
      });
    });

    const rangeOriginalReportInteractiveRegion = reportInteractiveRegion;
    reportInteractiveRegion = function (dragRect) {
      const m = PET_INTERACTIVE_MARGIN_PX;
      rangeOriginalReportInteractiveRegion({
        x: Math.round(dragRect.x - m),
        y: Math.round(dragRect.y - m),
        width: Math.round(dragRect.width + m * 2),
        height: Math.round(dragRect.height + m * 2)
      });
    };
"""

# 在 IIFE 结束(最后一个 "})();" + "</script>")之前注入,与既有补丁兼容
ANCHOR = "\n  })();\n  </script>"


def main() -> None:
    parser = argparse.ArgumentParser(description="宠物 2 倍大小 + 交互范围扩大补丁")
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
    bump_widget_updated_at(
        blueprint_dir(args.appdata), find_pet_widget_id(blueprint_dir(args.appdata))
    )
    print("✅ 已注入显示/交互范围补丁:", path)
    print("   宠物显示为原来的 2 倍,悬停/点击响应范围外扩 24px。重启 Kimi 应用后生效。")


if __name__ == "__main__":
    main()
