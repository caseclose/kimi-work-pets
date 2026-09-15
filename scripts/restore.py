#!/usr/bin/env python3
"""restore.py — 恢复 Kimi Work 默认桌宠(macOS / Windows / Linux)

用法:
    python3 scripts/restore.py [--appdata <Kimi应用数据目录>]

需要备份目录(~/.kimi-work-pet-backup/)中存在 install.py 生成的备份;
若备份中有 index.html,会一并还原桌宠页面(撤销全部交互补丁);
若备份中有 widget.json,会一并还原组件标题/描述。
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import backup_dir, blueprint_dir, find_pet_widget_id


def die(msg: str) -> "NoReturn":
    print(f"错误:{msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore the default Kimi Work desktop pet")
    parser.add_argument("--appdata", default=None, help="Kimi 应用数据目录(路径不符时手动指定)")
    args = parser.parse_args()

    bk = backup_dir()
    base = blueprint_dir(args.appdata)
    widget_id = find_pet_widget_id(base)
    ws = base / "widgets" / widget_id / "workspace"

    for name in ("current.json", "pet.json", "pet.riv"):
        if not (bk / name).is_file():
            die(f"未找到备份 {bk/name},无法回滚。")

    shutil.copy2(bk / "pet.json", ws / "pet.json")
    shutil.copy2(bk / "pet.riv", ws / "pet.riv")
    shutil.copy2(bk / "current.json", base / "pet" / "current.json")
    for extra in ws.glob("spritesheet.*"):
        extra.unlink()

    if (bk / "widget.json").is_file():
        shutil.copy2(bk / "widget.json", base / "widgets" / widget_id / "widget.json")
        print("已一并还原组件标题/描述。")

    if (bk / "index.html").is_file():
        shutil.copy2(bk / "index.html", ws / "index.html")
        print("已一并还原桌宠页面(撤销全部交互补丁)。")

    print("✅ 已恢复默认 Kimi 桌宠,重启 Kimi 应用后生效。")


if __name__ == "__main__":
    main()
