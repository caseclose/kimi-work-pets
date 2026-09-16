#!/usr/bin/env python3
"""patch-idle-flicker.py — 修复桌宠长时间空闲后唤醒时的补帧跳变(瞬移闪烁)

两处补丁:
1. tick() 里挂起时间超过 4 个帧间隔时,只前进 1 帧并把 lastFrameAt 对齐到现在,
   不再按经过时间一次补跳大量帧。
2. 新增 visibilitychange 监听:页面重新可见时重置 lastFrameAt 并重启动画调度,
   避免 rAF 恢复瞬间的陈旧时间戳。

幂等,可重复执行。

用法:
    python3 scripts/patch-idle-flicker.py [--appdata <Kimi应用数据目录> | <index.html 路径>]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, bump_widget_updated_at, find_pet_widget_id

OLD_TICK = (
    "          const steps = Math.max(1, Math.floor((now - lastFrameAt) / interval));\n"
    "          frame = state.loop ? (frame + steps) % state.frames : Math.min(state.frames - 1, frame + steps);\n"
    "          lastFrameAt += steps * interval;"
)
NEW_TICK = (
    "          const elapsed = now - lastFrameAt;\n"
    "          const resumedFromSuspension = elapsed > interval * 4;\n"
    "          const steps = resumedFromSuspension\n"
    "            ? 1\n"
    "            : Math.max(1, Math.floor(elapsed / interval));\n"
    "          frame = state.loop ? (frame + steps) % state.frames : Math.min(state.frames - 1, frame + steps);\n"
    "          lastFrameAt = resumedFromSuspension ? now : lastFrameAt + steps * interval;"
)

OLD_SCHED = (
    "    function restartAnimationSchedule() {\n"
    "      clearAnimationSchedule();\n"
    "      scheduleAnimationTick();\n"
    "    }"
)
NEW_SCHED = (
    "    function restartAnimationSchedule() {\n"
    "      clearAnimationSchedule();\n"
    "      scheduleAnimationTick();\n"
    "    }\n"
    "\n"
    "    document.addEventListener('visibilitychange', () => {\n"
    "      if (document.hidden) return;\n"
    "      lastFrameAt = performance.now();\n"
    "      restartAnimationSchedule();\n"
    "    });"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="修复桌宠空闲后唤醒的补帧跳变")
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

    if "resumedFromSuspension" in text and "visibilitychange" in text:
        print("补丁已存在,无需重复应用。")
        return 0

    if text.count(OLD_TICK) != 1:
        print(f"错误: tick 锚点出现 {text.count(OLD_TICK)} 次,预期 1 次,未修改。", file=sys.stderr)
        return 1
    text = text.replace(OLD_TICK, NEW_TICK)
    print("已应用: tick 补帧钳制")

    if text.count(OLD_SCHED) != 1:
        print(f"错误: 调度函数锚点出现 {text.count(OLD_SCHED)} 次,预期 1 次,未修改。", file=sys.stderr)
        return 1
    text = text.replace(OLD_SCHED, NEW_SCHED)
    print("已应用: visibilitychange 唤醒重置")

    target.write_text(text, encoding="utf-8")
    if base is not None:
        bump_widget_updated_at(base, widget_id)
    print("目标:", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
