#!/usr/bin/env python3
"""修复桌宠长时间空闲后唤醒时的补帧跳变（闪烁）。

两处补丁:
1. tick() 里挂起时间超过 4 个帧间隔时,只前进 1 帧并把 lastFrameAt 对齐到现在,
   不再按经过时间一次补跳大量帧。
2. 新增 visibilitychange 监听:页面重新可见时重置 lastFrameAt 并重启动画调度,
   避免 rAF 恢复瞬间的陈旧时间戳。
"""
import os
import sys
import glob

WIDGET_WS = os.path.expanduser(
    "~/Library/Application Support/kimi-desktop/daimon-share/daimon/agents/main/"
    "blueprint/widgets/widget_d53cf028-d0fd-4751-b955-28e325bd3e01/workspace"
)
TARGET = os.path.join(WIDGET_WS, "index.html")

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


def main():
    with open(TARGET, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8")

    if NEW_TICK in text and NEW_SCHED in text:
        print("补丁已存在,无需重复应用。")
        return 0

    applied = []
    if text.count(OLD_TICK) != 1:
        print(f"错误: tick 锚点出现 {text.count(OLD_TICK)} 次,预期 1 次,未修改。")
        return 1
    text = text.replace(OLD_TICK, NEW_TICK)
    applied.append("tick 补帧钳制")

    if text.count(OLD_SCHED) != 1:
        print(f"错误: 调度函数锚点出现 {text.count(OLD_SCHED)} 次,预期 1 次,未修改。")
        return 1
    text = text.replace(OLD_SCHED, NEW_SCHED)
    applied.append("visibilitychange 唤醒重置")

    with open(TARGET, "wb") as f:
        f.write(text.encode("utf-8"))
    print("已应用补丁:", ", ".join(applied))
    print("目标:", TARGET)
    return 0


if __name__ == "__main__":
    sys.exit(main())
