#!/usr/bin/env python3
"""patch-task-done-sound.py — 任务完成提示音补丁

宿主在 Agent 回合结束(活动流清空)时会把桌宠状态从 working 切回 idle。
本补丁包装渲染器的 setPreferredState,捕获 "working → 非 working/waiting"
的跳变并播放一声提示音(assets/sounds/task-done.mp3,AI 生成的双音马林巴
chime);working → waiting(等待确认)不触发,失败/取消也会提示(回合同样
结束)。

音效文件会被复制到每个桌宠组件的 workspace/ 下(名为 task-done.mp3);
组件可能有多个(多宠物切换),脚本自动遍历全部 kind == "pet" 的组件。

用法:
    python3 scripts/patch-task-done-sound.py [--appdata <Kimi应用数据目录>]
    python3 scripts/patch-task-done-sound.py <index.html 路径>   # 只补丁单个页面
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import blueprint_dir, bump_widget_updated_at, find_pet_widget_ids

MARKER = "task-done-sound"

SOUND_SOURCE = Path(__file__).resolve().parent.parent / "assets/sounds/task-done.mp3"
SOUND_NAME = "task-done.mp3"

INJECTION = r"""
    /* task-done-sound: chime when a run finishes (working -> idle) */
    (function () {
      const DONE_SOUND_URL = 'task-done.mp3';
      const DONE_SOUND_VOLUME = 0.6;
      let tdsLastState = 'idle';
      let tdsAudio = null;
      // 提前创建以预加载,避免第一次完成时才下载解码
      try {
        tdsAudio = new Audio(DONE_SOUND_URL);
        tdsAudio.preload = 'auto';
        tdsAudio.volume = DONE_SOUND_VOLUME;
      } catch (tdsErr) { /* noop */ }
      function tdsPlay() {
        try {
          if (!tdsAudio) {
            tdsAudio = new Audio(DONE_SOUND_URL);
            tdsAudio.preload = 'auto';
            tdsAudio.volume = DONE_SOUND_VOLUME;
          }
          tdsAudio.currentTime = 0;
          const p = tdsAudio.play();
          if (p && typeof p.catch === 'function') p.catch(() => {});
        } catch (tdsErr) { /* noop */ }
      }

      const tdsOriginalSetPreferredState = setPreferredState;
      setPreferredState = function (nextState) {
        // 回合结束:working -> idle/failed 等(working -> waiting 是等待确认,不算完成)
        if (
          tdsLastState === 'working' &&
          nextState !== 'working' &&
          nextState !== 'waiting'
        ) {
          tdsPlay();
        }
        tdsLastState =
          nextState === 'working' || nextState === 'waiting' ? nextState : 'idle';
        return tdsOriginalSetPreferredState(nextState);
      };
    })();
"""

# 在 IIFE 结束(最后一个 "})();" + "</script>")之前注入,与既有补丁兼容
ANCHOR = "\n  })();\n  </script>"


def patch_html(path: Path) -> bool:
    """注入补丁。返回是否发生了修改(已打过则返回 False)。"""
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    if ANCHOR not in text:
        raise SystemExit(f"错误:{path} 找不到注入锚点,渲染器结构可能已变化")
    text = text.replace(ANCHOR, INJECTION + ANCHOR, 1)
    path.write_text(text, encoding="utf-8")
    return True


def install_sound(workspace: Path) -> bool:
    """把音效拷进组件 workspace(内容一致则跳过)。返回是否发生复制。"""
    if not SOUND_SOURCE.is_file():
        raise SystemExit(f"错误:音效素材缺失 {SOUND_SOURCE}")
    target = workspace / SOUND_NAME
    if target.is_file() and target.read_bytes() == SOUND_SOURCE.read_bytes():
        return False
    shutil.copy2(SOUND_SOURCE, target)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="给 Kimi Work 桌宠注入任务完成提示音")
    parser.add_argument("path", nargs="?", default=None,
                        help="index.html 路径(直接指定单个页面文件)")
    parser.add_argument("--appdata", default=None,
                        help="Kimi 应用数据目录(路径不符时手动指定)")
    args = parser.parse_args()

    if args.path:
        path = Path(args.path)
        if not path.is_file():
            raise SystemExit(f"错误:{path} 不存在")
        changed = patch_html(path)
        sound_copied = install_sound(path.parent)
        print(("已注入提示音补丁" if changed else "已打过补丁,跳过")
              + (";已复制音效" if sound_copied else ";音效已存在")
              + f":{path}")
        return

    base = blueprint_dir(args.appdata)
    widget_ids = find_pet_widget_ids(base)
    if not widget_ids:
        raise SystemExit("错误:未发现任何桌宠组件(widgets/*/widget.json kind=pet)")
    for widget_id in widget_ids:
        workspace = base / "widgets" / widget_id / "workspace"
        path = workspace / "index.html"
        if not path.is_file():
            print(f"⚠️ 跳过 {widget_id}:{path} 不存在", file=sys.stderr)
            continue
        changed = patch_html(path)
        sound_copied = install_sound(workspace)
        bump_widget_updated_at(base, widget_id)
        print(f"{'已注入' if changed else '已打过,跳过'}"
              f"{' + 音效已复制' if sound_copied else ''}:{widget_id}")
    print("完成。宿主检测到组件更新后会自动重载桌宠页面;未生效则重启 Kimi。")


if __name__ == "__main__":
    main()
