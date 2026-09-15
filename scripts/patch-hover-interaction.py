#!/usr/bin/env python3
"""patch-hover-interaction.py — 给 Kimi Work 桌宠页面加"悬停招手"交互

桌宠组件的 workspace/index.html 是单文件 IIFE。本脚本在 IIFE 结束前注入一段代码:
鼠标悬停在宠物身上时,播放 idle_random_1(通常为 waving 招手)一个循环后回到待机。
可重复运行(幂等,以 hover-wave-interaction 标记判断)。

用法:
    python3 scripts/patch-hover-interaction.py [index.html 路径]
"""
import sys
from pathlib import Path

MARKER = "hover-wave-interaction"

INJECTION = r"""
    /* hover-wave-interaction: pet waves back when the pointer hovers it */
    let hoverWaveTimer = 0;
    let hoverWaveCooldownUntil = 0;

    function triggerHoverWave() {
      if (!manifest || isRiveManifest(manifest)) return;
      if (interactionStateActive || preferredStateName !== 'idle') return;
      if (stateName !== 'idle' && stateName !== 'idle_random_2') return;
      const nowTime = Date.now();
      if (nowTime < hoverWaveCooldownUntil) return;
      const waveState = manifest.states.idle_random_1;
      if (!waveState) return;
      hoverWaveCooldownUntil = nowTime + 6000;
      interactionStateActive = true;
      clearIdleVariantTimer();
      setState('idle_random_1');
      clearTimeout(hoverWaveTimer);
      hoverWaveTimer = setTimeout(() => {
        interactionStateActive = false;
        setState(preferredStateName);
        scheduleIdleVariant();
      }, Math.round((waveState.frames * 1000) / waveState.fps));
    }

    if (pet) {
      pet.addEventListener('pointerenter', triggerHoverWave);
    }
    const hoverWaveOriginalPointerPresence = handlePointerPresence;
    handlePointerPresence = function (inside) {
      hoverWaveOriginalPointerPresence(inside);
      if (inside === true) triggerHoverWave();
    };
"""

ANCHOR = "reason instanceof Error ? reason.message : String(reason)));\n  })();"


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if path is None:
        base = Path.home() / ("Library/Application Support/kimi-desktop/daimon-share/daimon/"
                              "agents/main/blueprint/widgets/"
                              "widget_d53cf028-d0fd-4751-b955-28e325bd3e01/workspace/index.html")
        path = base
    html = path.read_text(encoding="utf-8")

    if MARKER in html:
        print("已打过补丁,跳过:", path)
        return
    if ANCHOR not in html:
        sys.exit("未找到注入锚点,桌宠页面结构可能已更新,请人工检查 index.html")

    patched = html.replace(ANCHOR, ANCHOR.replace("})();", INJECTION + "\n  })();"), 1)
    path.write_text(patched, encoding="utf-8")
    print("✅ 已注入悬停交互:", path)
    print("   重启 Kimi 应用后,鼠标悬停桌宠即可看到它招手回应(6 秒冷却)。")


if __name__ == "__main__":
    main()
