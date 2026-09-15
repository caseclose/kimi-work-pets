# kimi-work-dimo-pet

把 Kimi Work 桌面端的内置桌宠换成 **Dimo(迪莫)**——来自 Codex 社区宠物生态的蓝色星尾小猫。

[English](#english) below.

## 这是什么

Kimi Work 桌面端(macOS)的内置桌宠默认是一个 Rive 动画形象。本仓库提供:

- `pet/dimo/` — 转换好的 **Kimi Work 精灵图格式** Dimo 素材包(`pet.json` + `spritesheet.webp`)
- `scripts/install-dimo.sh` — 一键安装(自动备份原配置)
- `scripts/restore-default.sh` — 一键回滚
- `scripts/inspect_spritesheet.py` — 精灵图布局检查工具
- `docs/` — Kimi Work 桌宠机制调研、社区生态笔记

## 安装

要求:macOS、已安装 Kimi Work 桌面端、`python3`。

```bash
git clone https://github.com/caseclose/kimi-work-dimo-pet.git
cd kimi-work-dimo-pet
bash scripts/install-dimo.sh
```

然后**重启 Kimi 应用**(或重新开关一次桌宠)即可看到迪莫。

## 回滚

```bash
bash scripts/restore-default.sh
```

安装脚本会自动把原桌宠文件备份到 `~/.kimi-work-pet-backup/`,回滚脚本从该备份恢复。

## Dimo 状态映射

| Kimi Work 状态 | 精灵图行 | 动作 |
| --- | --- | --- |
| 空闲 idle | 0 | 站立眨眼 |
| 工作中 working | 7 | 快速奔跑 |
| 等待确认 waiting | 6 | 左右张望 |
| 向左跑动 running_left | 2 | 向左飞奔 |
| 向右跑动 running_right | 1 | 向右飞奔 |
| 失败 failed | 5 | 倒地大哭 |
| 空闲彩蛋 idle_random_1 | 3 | 招手 |
| 空闲彩蛋 idle_random_2 | 4 | 开心跳跃 |

想换别的社区宠物?参考 `docs/how-kimi-work-pet-works.md` 的 manifest 格式,
从 [CodexPets.net](https://codexpets.net/) 等社区下载素材包后改写字段即可,
`scripts/inspect_spritesheet.py` 可以帮你确认每行的动作和实际帧数。

## 素材版权与免责声明

- `spritesheet.webp` 为社区粉丝二创作品,原作者 **swrited**,经由 [CodexPets.net](https://codexpets.net/gallery/dimo) 获取,通常以 CC BY-NC 或类似协议发布,**仅供个人非商业使用**。
- 迪莫(Dimo)相关形象权利归其原版权方所有,本仓库不主张任何权利。
- 本仓库与 Moonshot AI(月之暗面)、OpenAI 均无任何隶属或授权关系;Kimi 相关商标归其各自所有者。
- 代码部分以 MIT 协议开源(见 LICENSE),素材不适用 MIT。

---

## English

Swap the built-in desktop pet of the **Kimi Work** desktop app (macOS) for **Dimo**, a blue
star-tailed cat from the Codex community pet ecosystem.

- `pet/dimo/` — the Dimo package converted to the Kimi Work spritesheet manifest format
- `scripts/install-dimo.sh` — one-command install (auto-backups your original pet)
- `scripts/restore-default.sh` — restore the default Kimi pet
- `scripts/inspect_spritesheet.py` — inspect spritesheet grids (frame counts per row)
- `docs/` — how the Kimi Work pet system works under the hood

```bash
git clone https://github.com/caseclose/kimi-work-dimo-pet.git
cd kimi-work-dimo-pet
bash scripts/install-dimo.sh   # then restart the Kimi app
```

The artwork is community fan art by **swrited** (via [CodexPets.net](https://codexpets.net/gallery/dimo)),
licensed CC BY-NC or similar — **personal, non-commercial use only**. Code is MIT; assets are not.
Not affiliated with Moonshot AI or OpenAI.
