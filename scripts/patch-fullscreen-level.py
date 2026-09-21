#!/usr/bin/env python3
"""patch-fullscreen-level.py — 桌宠/组件 pin 窗口「全屏置顶」补丁

问题:macOS 上其他应用进入全屏后,桌宠窗口不会跟随显示在最前。

根因(宿主主进程 out/main/index.js):
- #applyWindowLevel 只调用 setAlwaysOnTop(flag),使用默认 floating 层级,
  低于全屏空间,无法浮在全屏应用之上;
- #applyWorkspaceVisibility 只调用 setVisibleOnAllWorkspaces(true),
  缺少 { visibleOnFullScreen: true, skipTransformProcessType: true } 选项;
- #setAlwaysOnTop(IPC 开关)同样丢了层级。
  而宿主的图片 pin 窗口创建处本来就用的是
  setAlwaysOnTop(true, "screen-saver") + 完整工作区选项,本补丁把组件 pin
  窗口对齐到同样行为。

补丁内容(3 处,均为混淆代码里的唯一锚点):
1. #applyWorkspaceVisibility:  setVisibleOnAllWorkspaces(true)
   → setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true,
     skipTransformProcessType: true })
2. #applyWindowLevel:          setAlwaysOnTop(flag)
   → setAlwaysOnTop(flag, "screen-saver")
3. #setAlwaysOnTop(IPC):       setAlwaysOnTop(flag)
   → setAlwaysOnTop(flag, "screen-saver")

注意:
- 宿主启用了 EnableEmbeddedAsarIntegrityValidation,补丁后会自动重算
  app.asar 的 SHA256 并写回 Info.plist 的 ElectronAsarIntegrity,
  否则应用无法启动。
- 修改前自动备份 app.asar 与 Info.plist(后缀 .bak-pet-fullscreen,
  已存在则不覆盖)。
- 应用升级会覆盖本补丁,升级后重跑本脚本即可(幂等,已打过则直接退出)。
- 补丁在应用重启后生效。

用法:
    python3 scripts/patch-fullscreen-level.py [--app /Applications/Kimi.app]
    python3 scripts/patch-fullscreen-level.py --check   # 只检查不修改
    python3 scripts/patch-fullscreen-level.py --restore # 从备份还原
"""
import argparse
import hashlib
import json
import plistlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_APP = "/Applications/Kimi.app"
BACKUP_SUFFIX = ".bak-pet-fullscreen"
MAIN_ENTRY = "out/main/index.js"

# (锚点, 替换为)。锚点/替换文本都来自混淆后的 index.js,升级后若失效会报错退出。
PATCHES = [
    (
        '_0x22d176[_0x2282c2(3714)](!![]);',
        '_0x22d176[_0x2282c2(3714)](!![], { "visibleOnFullScreen": !![],'
        ' "skipTransformProcessType": !![] });',
    ),
    (
        '_0x3ce7fb[_0x52b829(7899)](_0x492753["widgetKind"] === "pet"'
        ' || _0x492753[_0x52b829(12337)]);',
        '_0x3ce7fb[_0x52b829(7899)](_0x492753["widgetKind"] === "pet"'
        ' || _0x492753[_0x52b829(12337)], "screen-saver");',
    ),
    (
        '_0xa3232a[_0x4b0b41(7899)](_0x29d1b2), _0x158b31(',
        '_0xa3232a[_0x4b0b41(7899)](_0x29d1b2, "screen-saver"), _0x158b31(',
    ),
]


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def asar(*args):
    run(["npx", "--yes", "@electron/asar", *args])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def patch_source(text: str) -> tuple[str, list[str]]:
    """返回 (新文本, 已应用的补丁说明)。未打过的锚点缺失时报错。"""
    applied = []
    for anchor, replacement in PATCHES:
        if replacement in text:
            continue  # 已打过
        count = text.count(anchor)
        if count != 1:
            raise SystemExit(
                f"错误:锚点出现 {count} 次(期望 1 次),宿主版本可能已变化,"
                f"补丁中止。\n锚点: {anchor[:80]}..."
            )
        text = text.replace(anchor, replacement)
        applied.append(anchor[:60] + "...")
    return text, applied


def is_patched(text: str) -> bool:
    return all(rep in text for _, rep in PATCHES)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app", default=DEFAULT_APP, help="Kimi.app 路径")
    ap.add_argument("--check", action="store_true", help="只检查补丁状态,不修改")
    ap.add_argument("--restore", action="store_true", help="从备份还原 app.asar 与 Info.plist")
    args = ap.parse_args()

    app = Path(args.app)
    asar_path = app / "Contents/Resources/app.asar"
    plist_path = app / "Contents/Info.plist"
    asar_bak = asar_path.with_name(asar_path.name + BACKUP_SUFFIX)
    plist_bak = plist_path.with_name(plist_path.name + BACKUP_SUFFIX)
    for p in (asar_path, plist_path):
        if not p.exists():
            raise SystemExit(f"错误:{p} 不存在")

    if args.restore:
        unpacked_path = asar_path.with_name("app.asar.unpacked")
        unpacked_bak = unpacked_path.with_name(unpacked_path.name + BACKUP_SUFFIX)
        for bak, dst in ((asar_bak, asar_path), (plist_bak, plist_path),
                         (unpacked_bak, unpacked_path)):
            if not bak.exists():
                raise SystemExit(f"错误:备份 {bak} 不存在,无法还原")
            if bak.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(bak, dst)
            else:
                shutil.copy2(bak, dst)
            print(f"已还原 {dst} ← {bak}")
        print("还原完成,重启 Kimi 后生效。")
        return

    # 1. 解出主进程入口并检查状态
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        # extract-file 没有 --output,只能把文件按基名解到当前目录
        run(["npx", "--yes", "@electron/asar", "extract-file",
             str(asar_path), MAIN_ENTRY], cwd=tmp)
        src_path = tmp / Path(MAIN_ENTRY).name
        text = src_path.read_text(encoding="utf-8")

        if is_patched(text):
            print("已打过全屏置顶补丁,无需重复操作。")
            return
        if args.check:
            print("尚未打补丁(--check 模式,未做修改)。")
            return

        text, applied = patch_source(text)
        print("应用补丁:")
        for a in applied:
            print(f"  ✓ {a}")

        # 2. 全量解包 → 替换 → 重打包
        print("解包 app.asar(约 100MB,需要十几秒)...")
        extract_dir = tmp / "asar-root"
        asar("extract", str(asar_path), str(extract_dir))
        (extract_dir / MAIN_ENTRY).write_text(text, encoding="utf-8")
        new_asar = tmp / "app.asar.new"
        print("重新打包...")
        # 与原始 asar 保持一致:原生模块和 worker 脚本必须 unpack,
        # 否则无法 dlopen / 被 Worker 按文件路径加载
        asar("pack", str(extract_dir), str(new_asar), "--unpack",
             "{**/*.node,**/*-worker.mjs}")

        # 3. 备份(只在首次)
        unpacked_path = asar_path.with_name("app.asar.unpacked")
        unpacked_bak = unpacked_path.with_name(unpacked_path.name + BACKUP_SUFFIX)
        for src, bak in ((asar_path, asar_bak), (plist_path, plist_bak),
                         (unpacked_path, unpacked_bak)):
            if src.exists() and not bak.exists():
                if src.is_dir():
                    shutil.copytree(src, bak)
                else:
                    shutil.copy2(src, bak)
                print(f"已备份 {src} → {bak}")

        # 4. 替换 asar(及配套 unpacked 目录)并更新 Info.plist 完整性哈希
        new_unpacked = tmp / "app.asar.new.unpacked"
        shutil.move(str(new_asar), str(asar_path))
        if new_unpacked.exists():
            if unpacked_path.exists():
                shutil.rmtree(unpacked_path)
            shutil.move(str(new_unpacked), str(unpacked_path))
        with plist_path.open("rb") as f:
            plist = plistlib.load(f)
        integrity = plist.setdefault("ElectronAsarIntegrity", {})
        entry = integrity.setdefault("Resources/app.asar", {})
        entry["algorithm"] = "SHA256"
        new_hash = sha256(asar_path)
        entry["hash"] = new_hash
        with plist_path.open("wb") as f:
            plistlib.dump(plist, f)
        print(f"已更新 ElectronAsarIntegrity: {new_hash[:16]}...")

    print("\n完成。请完全退出并重新打开 Kimi(⌘Q 后重开),补丁才会生效。")
    print(f"如需还原:python3 {Path(__file__).name} --restore")


if __name__ == "__main__":
    main()
