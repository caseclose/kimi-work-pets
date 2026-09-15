#!/bin/bash
# install.sh — 把任意 Kimi Work 格式的桌宠安装为当前桌宠
#
# 用法: bash scripts/install.sh <宠物包目录>
#   目录中需包含 pet.json(Kimi Work 精灵图格式)与其中引用的 spritesheet 文件。
#   Codex 社区包请先运行: python3 scripts/convert-codex-pet.py <目录>
#
# 首次安装会自动备份被替换的默认桌宠文件到 ~/.kimi-work-pet-backup/
set -euo pipefail

if [[ "$(uname)" != "Darwin" ]]; then
  echo "提示:本脚本按 macOS 路径编写,其他系统请手动调整 BASE 路径。" >&2
fi

if [[ $# -ne 1 ]]; then
  echo "用法: bash scripts/install.sh <宠物包目录>" >&2
  exit 1
fi

PET_DIR="$(cd "$1" && pwd)"
BASE="$HOME/Library/Application Support/kimi-desktop/daimon-share/daimon/agents/main/blueprint"
PET_WIDGET_ID="widget_d53cf028-d0fd-4751-b955-28e325bd3e01"
WS="$BASE/widgets/$PET_WIDGET_ID/workspace"
BACKUP_DIR="$HOME/.kimi-work-pet-backup"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MANIFEST="$PET_DIR/pet.json"
for f in "$BASE/pet/current.json" "$WS/pet.json" "$WS/pet.riv"; do
  [[ -f "$f" ]] || { echo "未找到 $f,请先确认 Kimi Work 桌面端已运行过并生成默认桌宠。" >&2; exit 1; }
done
[[ -f "$MANIFEST" ]] || { echo "未找到 $MANIFEST。" >&2; exit 1; }

# 校验清单与素材,并取出关键字段
read -r PET_ID SPRITESHEET < <(python3 - "$MANIFEST" <<'EOF'
import json, os, sys
d = os.path.dirname(sys.argv[1])
m = json.load(open(sys.argv[1], encoding="utf-8"))
if not (m.get("atlas") and m.get("states") and m.get("states", {}).get("idle")):
    sys.exit("pet.json 不是有效的 Kimi Work 精灵图清单(缺 atlas/states.idle)")
sheet = m.get("spritesheet")
if not sheet or not os.path.isfile(os.path.join(d, sheet)):
    sys.exit(f"精灵图文件不存在: {sheet}")
print(m.get("id", "pet"), sheet)
EOF
)

echo "安装桌宠: $PET_ID (来源: $PET_DIR)"
mkdir -p "$BACKUP_DIR"
[[ -f "$BACKUP_DIR/current.json" ]] || cp "$BASE/pet/current.json" "$BACKUP_DIR/current.json"
cp -n "$WS/pet.json" "$BACKUP_DIR/pet.json" 2>/dev/null || true
cp -n "$WS/pet.riv" "$BACKUP_DIR/pet.riv" 2>/dev/null || true
echo "已备份原桌宠文件到 $BACKUP_DIR"

mkdir -p "$BASE/pet/library/$PET_ID"
cp "$PET_DIR/$SPRITESHEET" "$BASE/pet/library/$PET_ID/$SPRITESHEET"
cp "$MANIFEST" "$BASE/pet/library/$PET_ID/pet.json"
cp "$PET_DIR/$SPRITESHEET" "$WS/$SPRITESHEET"
cp "$MANIFEST" "$WS/pet.json"

MANIFEST_TEXT="$(cat "$MANIFEST")"
python3 - "$BASE" "$PET_WIDGET_ID" "$MANIFEST_TEXT" <<'EOF'
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
echo "✅ 安装完成。重启 Kimi 应用(或重新开关桌宠)后生效。"
echo "   回滚: bash scripts/restore-default.sh"
