#!/bin/bash
# restore-default.sh — 恢复 Kimi Work 默认桌宠
#
# 用法: bash scripts/restore-default.sh
# 需要 ~/.kimi-work-pet-backup/ 中存在安装脚本生成的备份。
# 若备份中有 index.html,会一并还原桌宠页面(撤销悬停交互补丁)。
set -euo pipefail

BASE="$HOME/Library/Application Support/kimi-desktop/daimon-share/daimon/agents/main/blueprint"
PET_WIDGET_ID="widget_d53cf028-d0fd-4751-b955-28e325bd3e01"
WS="$BASE/widgets/$PET_WIDGET_ID/workspace"
BACKUP_DIR="$HOME/.kimi-work-pet-backup"

for f in "$BACKUP_DIR/current.json" "$BACKUP_DIR/pet.json" "$BACKUP_DIR/pet.riv"; do
  [[ -f "$f" ]] || { echo "未找到备份 $f,无法回滚。" >&2; exit 1; }
done

cp "$BACKUP_DIR/pet.json" "$WS/pet.json"
cp "$BACKUP_DIR/pet.riv" "$WS/pet.riv"
cp "$BACKUP_DIR/current.json" "$BASE/pet/current.json"
rm -f "$WS/spritesheet.webp"

if [[ -f "$BACKUP_DIR/index.html" ]]; then
  cp "$BACKUP_DIR/index.html" "$WS/index.html"
  echo "已一并还原桌宠页面(撤销交互补丁)。"
fi

echo "✅ 已恢复默认 Kimi 桌宠,重启 Kimi 应用后生效。"
