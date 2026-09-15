#!/usr/bin/env python3
"""patch-bubble-info.py — 让桌宠头顶的任务气泡显示更丰富的信息

宿主推给桌宠的数据里没有时间戳,但页面能自己记录:
  - 任务开始运行的时间 → 气泡追加"已工作 X 分钟 / X 秒";
  - 最近一次调用的工具名 → 思考阶段也能看到"刚用过 Bash"。

效果示例(运行中):
    正在调用 Bash… · 已工作 2 分钟
    正在思考… · 刚用过 WebSearch · 已工作 35 秒

只在 runState === 'running' 时计时,任务结束自动清理;每 20 秒自动刷新一次
气泡让计时走动。幂等(以 bubble-rich-info 标记判断)。

用法:
    python3 scripts/patch-bubble-info.py [--appdata <Kimi应用数据目录> | <index.html 路径>]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, bump_widget_updated_at, find_pet_widget_id

MARKER = "bubble-rich-info"

INJECTION = r"""
    /* bubble-rich-info: elapsed work time + last used tool in the bubble */
    const bubbleInfoOriginalBodyText = activityBodyText;
    const bubbleInfoOriginalProgressText = conversationStatusProgressText;
    const bubbleInfoSince = new Map();
    let bubbleInfoLastTool = '';

    conversationStatusProgressText = function (part) {
      const label = bubbleInfoOriginalProgressText(part);
      if (label && part && typeof part.toolName === 'string' && part.toolName.trim()) {
        bubbleInfoLastTool = part.toolName.trim();
      }
      return label;
    };

    function bubbleInfoIsZh() {
      return String(currentLocaleTag || '').toLowerCase().indexOf('zh') === 0;
    }

    function bubbleInfoElapsedLabel(totalSeconds) {
      const minutes = Math.floor(totalSeconds / 60);
      if (minutes >= 1) {
        return bubbleInfoIsZh()
          ? '已工作 ' + minutes + ' 分钟'
          : 'Worked ' + minutes + ' min';
      }
      return bubbleInfoIsZh()
        ? '已工作 ' + totalSeconds + ' 秒'
        : 'Worked ' + totalSeconds + 's';
    }

    activityBodyText = function (activity) {
      const baseText = bubbleInfoOriginalBodyText(activity);
      const key = String(activity && activity.id);
      const nowTime = Date.now();
      if (!activity || activity.runState !== 'running') {
        bubbleInfoSince.delete(key);
        return baseText;
      }
      if (!bubbleInfoSince.has(key)) bubbleInfoSince.set(key, nowTime);
      const elapsedSec = Math.max(
        0,
        Math.floor((nowTime - bubbleInfoSince.get(key)) / 1000)
      );
      const parts = [baseText];
      if (
        bubbleInfoLastTool &&
        baseText.indexOf(bubbleInfoLastTool) < 0
      ) {
        parts.push(
          bubbleInfoIsZh()
            ? '刚用过 ' + bubbleInfoLastTool
            : 'last tool: ' + bubbleInfoLastTool
        );
      }
      if (elapsedSec >= 20) parts.push(bubbleInfoElapsedLabel(elapsedSec));
      return parts.join(' · ');
    };

    setInterval(function () {
      try {
        if (
          typeof render === 'function' &&
          activities.some(function (a) { return a.runState === 'running'; })
        ) {
          render();
        }
      } catch (bubbleInfoErr) { /* noop */ }
    }, 20000);
"""

# 在 IIFE 结束(最后一个 "})();" + "</script>")之前注入,与既有补丁兼容
ANCHOR = "\n  })();\n  </script>"


def main() -> None:
    parser = argparse.ArgumentParser(description="给桌宠气泡追加丰富信息")
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
    print("✅ 已注入气泡增强:", path)
    print("   重启 Kimi 应用后,任务气泡会显示已工作时长和最近使用的工具。")


if __name__ == "__main__":
    main()
