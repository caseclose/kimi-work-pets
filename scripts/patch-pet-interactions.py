#!/usr/bin/env python3
"""patch-pet-interactions.py — 给 Kimi Work 桌宠页面加扩展互动

在悬停招手(patch-hover-interaction.py)之外追加三种互动,均只在宠物处于
空闲(idle)时触发,与任务状态驱动(working/waiting/failed/running)互不干扰:

  1. 开机问候:桌宠加载完成后,主动随机播放一个空闲彩蛋动作(招手/眨眼);
  2. 点击跳跃:鼠标点击/轻点宠物,随机播放兴奋动作(跳跃/眨眼),3 秒冷却;
  3. 长视撒娇:指针停在宠物身上超过 2.6 秒不放,播放大哭(failed)约两个循环。

素材缺少对应状态时自动跳过,因此对任意宠物安全。
可重复运行(幂等,以 pet-interactions 标记判断)。

用法:
    python3 scripts/patch-pet-interactions.py [--appdata <Kimi应用数据目录> | <index.html 路径>]
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, find_pet_widget_id

MARKER = "pet-interactions"

INJECTION = r"""
    /* pet-interactions: startup greet, tap-to-jump, long-hover tease */
    let piTimer = 0;
    let piTeaseTimer = 0;
    let piCooldownUntil = 0;
    let piHoverInside = false;

    function piAvailable(names) {
      if (!manifest || isRiveManifest(manifest)) return [];
      return names.filter((name) => Boolean(manifest.states[name]));
    }

    function piReact(names, cooldownMs, holdLoops) {
      if (!manifest || isRiveManifest(manifest)) return;
      if (interactionStateActive || preferredStateName !== 'idle') return;
      const nowTime = Date.now();
      if (nowTime < piCooldownUntil) return;
      const pool = piAvailable(names);
      if (pool.length === 0) return;
      const name = pool[Math.floor(Math.random() * pool.length)];
      const state = manifest.states[name];
      piCooldownUntil = nowTime + cooldownMs;
      interactionStateActive = true;
      clearIdleVariantTimer();
      setState(name);
      clearTimeout(piTimer);
      const loopMs = (state.frames * 1000) / state.fps;
      piTimer = setTimeout(() => {
        interactionStateActive = false;
        setState(preferredStateName);
        scheduleIdleVariant();
      }, Math.round(loopMs * (holdLoops || 1)));
    }

    function onPetTap() {
      piReact(['idle_random_2', 'idle_random_3'], 3000, 1);
    }

    function onPetEnterForTease() {
      piHoverInside = true;
      clearTimeout(piTeaseTimer);
      piTeaseTimer = setTimeout(() => {
        if (piHoverInside) piReact(['failed'], 6000, 2);
      }, 2600);
    }

    function onPetLeaveForTease() {
      piHoverInside = false;
      clearTimeout(piTeaseTimer);
    }

    if (pet) {
      pet.addEventListener('pointerdown', onPetTap);
      pet.addEventListener('pointerenter', onPetEnterForTease);
      pet.addEventListener('pointerleave', onPetLeaveForTease);
    }

    let piGreetTries = 0;
    function piGreetLoop() {
      if (manifest && !isRiveManifest(manifest)) {
        piReact(['idle_random_1', 'idle_random_3'], 0, 1);
        return;
      }
      if (++piGreetTries < 20) setTimeout(piGreetLoop, 500);
    }
    setTimeout(piGreetLoop, 1200);
"""

# 在 IIFE 结束(最后一个 "})();" + "</script>")之前注入,与既有补丁兼容
ANCHOR = "\n  })();\n  </script>"


def main() -> None:
    parser = argparse.ArgumentParser(description="给 Kimi Work 桌宠注入扩展互动")
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
    print("✅ 已注入扩展互动:", path)
    print("   重启 Kimi 应用后:开机主动打招呼;点击她随机跳跃/眨眼;")
    print("   鼠标停留在她身上超过 2.6 秒,她会撒娇大哭(6 秒冷却)。")


if __name__ == "__main__":
    main()
