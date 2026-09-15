"""petlib.py — 跨平台的 Kimi Work 桌宠路径与组件发现

Kimi Work 桌面端基于 Electron,各平台应用数据目录:
    macOS   ~/Library/Application Support/kimi-desktop
    Windows %APPDATA%\\kimi-desktop  (C:\\Users\\<用户>\\AppData\\Roaming\\kimi-desktop)
    Linux   ~/.config/kimi-desktop  (按 XDG 惯例推断)
"""
import json
import os
import sys
from pathlib import Path

# 早期版本脚本使用的硬编码桌宠组件 ID,仅在自动发现失败时兜底
FALLBACK_PET_WIDGET_ID = "widget_d53cf028-d0fd-4751-b955-28e325bd3e01"


def appdata_dir(override: str | None = None) -> Path:
    """Kimi 桌面端应用数据目录。"""
    if override:
        return Path(override)
    if sys.platform == "darwin":
        return Path.home() / "Library/Application Support/kimi-desktop"
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            appdata = str(Path.home() / "AppData" / "Roaming")
        return Path(appdata) / "kimi-desktop"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "kimi-desktop"


def blueprint_dir(override: str | None = None) -> Path:
    return appdata_dir(override) / "daimon-share/daimon/agents/main/blueprint"


def find_pet_widget_id(base: Path) -> str:
    """扫描 widgets/*/widget.json,返回 kind == "pet" 的组件 ID。"""
    widgets = base / "widgets"
    if widgets.is_dir():
        for d in sorted(widgets.iterdir()):
            meta_file = d / "widget.json"
            if not meta_file.is_file():
                continue
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8")).get("widget", {})
            except (json.JSONDecodeError, OSError):
                continue
            if meta.get("kind") == "pet":
                return d.name
    print("⚠️ 未能自动发现桌宠组件,回退到内置组件 ID;若桌宠未生效请用 "
          "--appdata 指定应用数据目录", file=sys.stderr)
    return FALLBACK_PET_WIDGET_ID


def backup_dir() -> Path:
    return Path.home() / ".kimi-work-pet-backup"


def bump_widget_updated_at(base: Path, widget_id: str) -> None:
    """把组件的 updatedAt 刷成当前时间,促使宿主重载桌宠页面。

    宿主(Electron)会缓存桌宠页面,只改 workspace/index.html 时重启应用
    也可能拿到旧页面;widget.json 的 updatedAt 变化会让宿主认为组件已更新。
    """
    import datetime
    meta_file = base / "widgets" / widget_id / "widget.json"
    if not meta_file.is_file():
        return
    try:
        doc = json.loads(meta_file.read_text(encoding="utf-8"))
        widget = doc.get("widget")
        if not isinstance(widget, dict):
            return
        widget["updatedAt"] = datetime.datetime.now(
            datetime.timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        meta_file.write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    except (json.JSONDecodeError, OSError):
        pass
