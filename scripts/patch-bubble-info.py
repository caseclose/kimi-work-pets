#!/usr/bin/env python3
"""patch-bubble-info.py — 让桌宠头顶的任务气泡显示更丰富的信息

宿主(Electron)推给桌宠的数据里没有时间戳,但页面能自己记录:
  - 任务开始运行的时间 → 气泡追加"已工作 X 分钟 / X 秒"(每 15 秒自动刷新);
  - 最近一次调用的工具名 → 思考阶段也能看到刚做过什么;
  - 按回合累计用过的工具种类 → "已用 N 种工具(Bash、WebSearch、Read…)"。

效果示例(运行中):
    正在调用 Bash… · 已用 5 种工具(Bash、WebSearch、Read…) · 已工作 2 分钟
    正在思考… · 已用 2 种工具(Bash、Grep) · 已工作 35 秒

只在 runState === 'running' 时计时,回合切换(turnId 变化)自动重置统计。
幂等(以 bubble-rich-info 标记判断)。

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
    /* bubble-rich-info: elapsed time + per-turn tool usage in the bubble */
    const bubbleInfoOriginalBodyText = activityBodyText;
    const bubbleInfoOriginalNormalize = normalizeConversationStatus;
    const bubbleInfoSince = new Map();
    const bubbleInfoToolSets = new Map();
    let bubbleInfoLastTool = '';

    normalizeConversationStatus = function (status) {
      const feed = bubbleInfoOriginalNormalize(status);
      try {
        const conversations =
          status && Array.isArray(status.conversations) ? status.conversations : [];
        for (const conv of conversations) {
          const part = conv && conv.latestPart;
          if (
            !part ||
            part.kind !== 'tool-call' ||
            typeof part.toolName !== 'string' ||
            !part.toolName.trim()
          ) {
            continue;
          }
          const key = String(conv.id);
          const turnId = typeof conv.turnId === 'string' ? conv.turnId : '';
          let entry = bubbleInfoToolSets.get(key);
          if (!entry || entry.turnId !== turnId) {
            entry = { turnId: turnId, tools: [] };
            bubbleInfoToolSets.set(key, entry);
          }
          const name = part.toolName.trim();
          if (entry.tools.indexOf(name) < 0 && entry.tools.length < 8) {
            entry.tools.push(name);
          }
          bubbleInfoLastTool = name;
        }
      } catch (bubbleInfoNormalizeErr) { /* noop */ }
      return feed;
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
      const key =
        String(activity && activity.id) + ':' +
        String((activity && activity.turnId) || '');
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
      const entry = bubbleInfoToolSets.get(String(activity.id));
      if (entry && entry.tools.length > 0) {
        const names = entry.tools.slice(0, 3).join(bubbleInfoIsZh() ? '、' : ', ');
        const more = entry.tools.length > 3 ? '…' : '';
        parts.push(
          entry.tools.length === 1
            ? bubbleInfoIsZh()
              ? '已用工具 ' + names
              : 'tool: ' + names
            : bubbleInfoIsZh()
              ? '已用 ' + entry.tools.length + ' 种工具 ' + names + more
              : entry.tools.length + ' tools: ' + names + more
        );
      } else if (
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
        if (!activities.some(function (a) { return a.runState === 'running'; })) return;
        // 卡片文本由 renderConversationCenter 负责,render 只画宠物精灵
        if (typeof renderConversationCenter === 'function') {
          renderConversationCenter();
        } else if (typeof render === 'function') {
          render();
        }
      } catch (bubbleInfoErr) { /* noop */ }
    }, 15000);
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
