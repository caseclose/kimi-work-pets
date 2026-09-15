#!/bin/bash
# install-dimo.sh — 把 Dimo(迪莫)桌宠安装为 Kimi Work 桌面端的当前桌宠
#
# 用法: bash scripts/install-dimo.sh
# 首次运行会自动备份被替换的默认桌宠文件到 ~/.kimi-work-pet-backup/
set -euo pipefail

if [[ "$(uname)" != "Darwin" ]]; then
  echo "提示:本脚本按 macOS 路径编写,其他系统请手动调整 BASE 路径。" >&2
fi

BASE="$HOME/Library/Application Support/kimi-desktop/daimon-share/daimon/agents/main/blueprint"
PET_WIDGET_ID="widget_d53cf028-d0fd-4751-b955-28e325bd3e01"
WS="$BASE/widgets/$PET_WIDGET_ID/workspace"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIMO_DIR="$SCRIPT_DIR/../pet/dimo"
BACKUP_DIR="$HOME/.kimi-work-pet-backup"

for f in "$BASE/pet/current.json" "$WS/pet.json" "$WS/pet.riv"; do
  [[ -f "$f" ]] || { echo "未找到 $f,请先确认 Kimi Work 桌面端已运行过并生成默认桌宠。" >&2; exit 1; }
done
[[ -f "$DIMO_DIR/pet.json" && -f "$DIMO_DIR/spritesheet.webp" ]] || { echo "缺少 Dimo 素材文件。" >&2; exit 1; }

mkdir -p "$BACKUP_DIR"
cp "$BASE/pet/current.json" "$BACKUP_DIR/current.json"
cp "$WS/pet.json" "$BACKUP_DIR/pet.json"
cp "$WS/pet.riv" "$BACKUP_DIR/pet.riv"
echo "已备份原桌宠文件到 $BACKUP_DIR"

mkdir -p "$BASE/pet/library/dimo"
cp "$DIMO_DIR/spritesheet.webp" "$BASE/pet/library/dimo/spritesheet.webp"
cp "$DIMO_DIR/pet.json" "$BASE/pet/library/dimo/pet.json"
cp "$DIMO_DIR/spritesheet.webp" "$WS/spritesheet.webp"
cp "$DIMO_DIR/pet.json" "$WS/pet.json"

DIMO_MANIFEST="$(cat "$DIMO_DIR/pet.json")"
python3 - "$BASE" "$PET_WIDGET_ID" "$DIMO_MANIFEST" <<'EOF'
import json, sys, datetime
base, widget_id, manifest_text = sys.argv[1], sys.argv[2], sys.argv[3]
manifest = json.loads(manifest_text)
current = {
    "version": 1,
    "selectedPetId": manifest["id"],
    "installed": [{
        "petId": manifest["id"],
        "widgetId": widget_id,
        "manifest": manifest,
        "installedAt": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    }],
}
with open(f"{base}/pet/current.json", "w", encoding="utf-8") as f:
    json.dump(current, f, ensure_ascii=False, indent=2)
print("current.json 已更新,当前桌宠:", manifest["id"])
EOF

echo ""
echo "✅ Dimo 安装完成。重启 Kimi 应用(或重新开关桌宠)后生效。"
echo "   回滚: bash scripts/restore-default.sh"
