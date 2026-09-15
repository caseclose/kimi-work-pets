#!/usr/bin/env python3
"""install.py — 把任意 Kimi Work 格式的桌宠安装为当前桌宠(macOS / Windows / Linux)

用法:
    python3 scripts/install.py <宠物包目录> [--appdata <Kimi应用数据目录>]

目录中需包含 pet.json(Kimi Work 精灵图格式)与其中引用的 spritesheet 文件。
Codex 社区包请先运行: python3 scripts/convert-codex-pet.py <目录>

首次安装会自动备份被替换的桌宠文件到 ~/.kimi-work-pet-backup/(Windows 为
C:\\Users\\<用户>\\.kimi-work-pet-backup\\)。
"""
import argparse
import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from petlib import backup_dir, blueprint_dir, find_pet_widget_id


def die(msg: str) -> "NoReturn":
    print(f"错误:{msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install a pet as the Kimi Work desktop pet")
    parser.add_argument("pet_dir", help="包含 pet.json 与 spritesheet 的目录")
    parser.add_argument("--appdata", default=None, help="Kimi 应用数据目录(路径不符时手动指定)")
    args = parser.parse_args()

    pet_dir = Path(args.pet_dir).resolve()
    manifest_path = pet_dir / "pet.json"
    if not manifest_path.is_file():
        die(f"未找到 {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    states = manifest.get("states") or {}
    if not (manifest.get("atlas") and states.get("idle")):
        die("pet.json 不是有效的 Kimi Work 精灵图清单(缺 atlas/states.idle),"
            "Codex 社区包请先用 convert-codex-pet.py 转换")
    sheet = manifest.get("spritesheet")
    if not sheet or not (pet_dir / sheet).is_file():
        die(f"精灵图文件不存在: {sheet}")
    pet_id = manifest.get("id") or pet_dir.name.lower()

    base = blueprint_dir(args.appdata)
    widget_id = find_pet_widget_id(base)
    ws = base / "widgets" / widget_id / "workspace"
    for f in (base / "pet/current.json", ws / "pet.json", ws / "pet.riv"):
        if not f.is_file():
            die(f"未找到 {f},请先确认 Kimi Work 桌面端已运行过并生成默认桌宠")

    print(f"安装桌宠: {manifest.get('name', pet_id)} (id: {pet_id})")
    print(f"桌宠组件: {widget_id}")

    bk = backup_dir()
    bk.mkdir(parents=True, exist_ok=True)
    for name, src in (("current.json", base / "pet/current.json"),
                      ("pet.json", ws / "pet.json"),
                      ("pet.riv", ws / "pet.riv")):
        dst = bk / name
        if not dst.exists():
            shutil.copy2(src, dst)
    print(f"已备份原桌宠文件到 {bk}")

    lib = base / "pet/library" / pet_id
    lib.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pet_dir / sheet, lib / sheet)
    shutil.copy2(manifest_path, lib / "pet.json")
    shutil.copy2(pet_dir / sheet, ws / sheet)
    shutil.copy2(manifest_path, ws / "pet.json")

    current = {
        "version": 1,
        "selectedPetId": pet_id,
        "installed": [{
            "petId": pet_id,
            "widgetId": widget_id,
            "manifest": manifest,
            "installedAt": datetime.datetime.now(datetime.timezone.utc)
                              .strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        }],
    }
    (base / "pet/current.json").write_text(
        json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("current.json 已更新,当前桌宠:", pet_id)

    print("注入悬停交互补丁(悬停时宠物招手回应)...")
    patch = Path(__file__).parent / "patch-hover-interaction.py"
    try:
        subprocess.run([sys.executable, str(patch)]
                       + (["--appdata", args.appdata] if args.appdata else []), check=True)
    except subprocess.CalledProcessError:
        print("⚠️ 补丁注入失败(不影响桌宠使用),可稍后手动运行 "
              "python3 scripts/patch-hover-interaction.py", file=sys.stderr)

    print()
    print("✅ 安装完成。重启 Kimi 应用(或重新开关桌宠)后生效。")
    print("   回滚: python3 scripts/restore.py")


if __name__ == "__main__":
    main()
