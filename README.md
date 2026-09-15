# kimi-work-pets

把 **Codex 社区桌宠**装进 **Kimi Work 桌面端**(macOS)。

Kimi Work 内置桌宠除了默认的 Rive 动画形象,还支持**精灵图(spritesheet)模式**,
与 [Codex 社区宠物生态](https://codexpets.net/)(codexpets.net、petdex.dev、
awesome-codex-pet 等)的素材格式同源。本仓库提供一键转换与安装工具,
[CodexPets.net](https://codexpets.net/) 上现成的几百只社区宠物(罗小黑、刻晴、
派蒙、Hello Kitty、PotatOS……)都可以尝试装进 Kimi Work。

内置示例:**Dimo(迪莫)**,蓝色星尾小猫。

| 预览 | 状态演示 |
| --- | --- |
| <img src="assets/dimo-preview.png" width="170"> | <img src="assets/dimo-states.gif" width="150"> |

[English](#english) below.

## 快速开始(以内置的迪莫为例)

要求:macOS、已安装 Kimi Work 桌面端、`python3`。

```bash
git clone https://github.com/caseclose/kimi-work-pets.git
cd kimi-work-pets
bash scripts/install.sh pets/dimo
```

然后**重启 Kimi 应用**(或重新开关一次桌宠)即可。

## 安装其他社区宠物

```bash
# 1. 从 codexpets.net 等社区下载宠物包并解压(内含 pet.json + spritesheet.webp)
unzip 0829-xxxx.zip -d my-pet

# 2. 转换为 Kimi Work 格式(自动统计每行实际帧数,原清单备份为 pet.codex.json)
python3 scripts/convert-codex-pet.py my-pet

# 3. 安装(自动备份当前桌宠到 ~/.kimi-work-pet-backup/)
bash scripts/install.sh my-pet
```

转换器按 Codex 标准 8×9 布局(192×208 单元格)识别每行动作:

| 行 | Codex 语义 | Kimi Work 状态 |
| --- | --- | --- |
| 0 | idle | 空闲 |
| 1 | running_right | 向右拖动 |
| 2 | running_left | 向左拖动 |
| 3 | waving | 空闲彩蛋 1 |
| 4 | jumping | 空闲彩蛋 2 |
| 5 | failed | 失败 |
| 6 | waiting | 等待确认 |
| 7 | running | 工作中 |
| 8 | review | (未映射,完成庆祝) |

如果某只宠物的布局不同,先用 `scripts/inspect_spritesheet.py <spritesheet.webp>`
逐行确认动作,再手动调整生成的 `pet.json`。

## 悬停交互(可选补丁)

默认行为:拖动桌宠时它会朝拖动方向奔跑;悬停时空闲动画会加快。
想要更多互动,可以打补丁让桌宠**在鼠标悬停时招手回应**:

```bash
python3 scripts/patch-hover-interaction.py
```

效果:悬停在桌宠身上时播放 `idle_random_1`(通常是 waving 招手)一个循环后回到待机,
内置 6 秒冷却避免频繁触发;只对精灵图宠物生效,幂等可重复运行。
`restore-default.sh` 会一并还原页面、撤销补丁。

## 回滚

```bash
bash scripts/restore-default.sh
```

## 仓库结构

```
pets/dimo/                 # 内置示例:已转换好的迪莫素材包
scripts/
├── install.sh             # 通用安装器(任意 Kimi 格式宠物包)
├── restore-default.sh     # 回滚默认 Kimi 桌宠
├── convert-codex-pet.py   # Codex 社区包 → Kimi Work 格式转换器
├── inspect_spritesheet.py # 精灵图布局检查(逐行帧条带 + 非空帧统计)
├── generate_previews.py   # 从精灵图生成 README 预览素材
└── patch-hover-interaction.py # 悬停招手交互补丁(可选,幂等)
docs/
├── how-kimi-work-pet-works.md   # Kimi Work 桌宠机制调研(manifest 格式、状态映射)
└── kimi-pet-plugin-notes.md     # wbxl2000/kimi-pet(Kimi Code 桌宠插件)调研
assets/                    # README 预览图与演示 GIF(由 generate_previews.py 生成)
```

## 素材版权与免责声明

- `pets/dimo/spritesheet.webp` 为社区粉丝二创作品,原作者 **swrited**,经由
  [CodexPets.net](https://codexpets.net/gallery/dimo) 获取,通常以 CC BY-NC 或类似
  协议发布,**仅供个人非商业使用**;形象权利归原版权方所有。
- 其他社区宠物素材的版权以各自来源页面声明为准。
- 本仓库与 Moonshot AI(月之暗面)、OpenAI 均无任何隶属或授权关系;Kimi 相关商标
  归其各自所有者。
- 代码部分以 MIT 协议开源(见 LICENSE),素材不适用 MIT。

---

## English

Install **Codex community pets** (from [CodexPets.net](https://codexpets.net/) and similar
galleries) as the built-in desktop pet of the **Kimi Work** desktop app (macOS).

Kimi Work's pet widget supports a **spritesheet renderer** that is compatible with the
Codex community pet format. This repo provides a converter and installer:

```bash
python3 scripts/convert-codex-pet.py <pet-dir>   # convert a Codex package (8x9 grid, 192x208 cells)
bash scripts/install.sh <pet-dir>                # install (auto-backups your current pet)
bash scripts/restore-default.sh                  # restore the default Kimi pet
```

`pets/dimo/` is a built-in example (Dimo, a blue star-tailed cat, fan art by
[swrited](https://codexpets.net/gallery/dimo), CC BY-NC or similar — personal,
non-commercial use only). See `docs/how-kimi-work-pet-works.md` for the manifest format
and host-state mapping. Code is MIT; assets are not. Not affiliated with Moonshot AI or OpenAI.
