# kimi-work-pets

把 [Codex 社区桌宠](https://codexpets.net/)装进 **Kimi Work 桌面端**(macOS / Windows)。

Kimi Work 内置桌宠除默认 Rive 形象外,还支持精灵图(spritesheet)模式,与 Codex 社区宠物素材(8×9 网格、192×208 单元格)格式同源。本仓库提供转换、安装、回滚工具;社区画廊里的宠物按同样流程都可以装。

内置示例 **Dimo(迪莫)**:腾讯《洛克王国》的光属性明星宠物([角色背景](https://baike.baidu.com/item/%E8%BF%AA%E8%8E%AB/10570042)),精灵图为社区二创(swrited)。

| 预览 | 状态演示 |
| --- | --- |
| <img src="assets/dimo-preview.png" width="170"> | <img src="assets/dimo-states.gif" width="150"> |

## 快速开始

要求:Kimi Work 桌面端、`python3`。支持 **macOS / Windows**(Windows 路径按 Electron
惯例定位 `%APPDATA%\kimi-desktop`,未经真机验证;若定位失败,各脚本均支持
`--appdata <Kimi应用数据目录>` 手动指定)。

```bash
git clone https://github.com/caseclose/kimi-work-pets.git
cd kimi-work-pets
python3 scripts/install.py pets/dimo   # 内置示例:迪莫
```

重启 Kimi 应用(或重新开关桌宠)后生效,桌宠已带悬停交互(见下节)。
回滚默认形象:`python3 scripts/restore.py`(原配置自动备份在用户目录的 `.kimi-work-pet-backup/`)。

## 安装其他社区宠物

1. 从 [CodexPets.net](https://codexpets.net/)(或 petdex.dev 等画廊)下载宠物包并解压(内含 `pet.json` + `spritesheet.webp`);
2. 转换:`python3 scripts/convert-codex-pet.py <目录>`(自动统计每行实际帧数,原清单备份为 `pet.codex.json`);
3. 安装:`python3 scripts/install.py <目录>`。

转换器按标准 9 行布局映射动作:

| 行 | 语义 | Kimi Work 状态 |
| --- | --- | --- |
| 0 | idle | 空闲 |
| 1 | running_right | 向右拖动 |
| 2 | running_left | 向左拖动 |
| 3 | waving | 空闲彩蛋 1 |
| 4 | jumping | 空闲彩蛋 2 |
| 5 | failed | 失败 |
| 6 | waiting | 等待确认 |
| 7 | running | 工作中 |
| 8 | review | (未映射) |

布局不符时,用 `scripts/inspect_spritesheet.py` 逐行确认动作后手动调整 `pet.json`;
manifest 字段与宿主状态映射详见 [docs/how-kimi-work-pet-works.md](docs/how-kimi-work-pet-works.md)。

## 交互增强

安装时自动注入两个补丁(`restore.py` 会一并还原页面、全部撤销):

- **悬停招手**:鼠标悬停桌宠时,播放招手动作(`idle_random_1`)一个循环后回到待机,
  6 秒冷却,不影响工作/等待等状态。
  实现:[scripts/patch-hover-interaction.py](scripts/patch-hover-interaction.py)。
- **视线跟随**:鼠标在桌宠附近移动时,宠物会平滑地向光标方向倾斜、偏移,离开后回正
  (用 CSS transform 近似"脑袋偏向";仅精灵图宠物,Rive 宠物自带眼动状态机会自动跳过)。
  实现:[scripts/patch-look-at-cursor.py](scripts/patch-look-at-cursor.py)。

两个补丁均幂等、可单独重复运行,也可加 `--appdata` 指定应用数据目录。

## 版权

- 代码:MIT(见 LICENSE)。
- `pets/dimo/` 精灵图:社区粉丝二创,作者 [swrited](https://codexpets.net/gallery/dimo),
  CC BY-NC 类协议,**仅供个人非商业使用**;迪莫形象来自腾讯《洛克王国》,权利归原版权方。
  其他社区素材的版权以各自来源页面为准。
- 本仓库与 Moonshot AI、OpenAI 无任何隶属或授权关系。

## English

Install Codex community pets as the desktop pet of the Kimi Work desktop app (macOS/Windows).
Convert a Codex package with `scripts/convert-codex-pet.py`, install it with
`scripts/install.py <pet-dir>`(built-in example: `pets/dimo`, Dimo from Tencent's
*Roco Kingdom*), roll back with `scripts/restore.py`. Installation also injects
hover interactions: the pet waves back when you hover over it, and sprite pets
lean toward the cursor as you move the mouse around.
All scripts accept `--appdata <dir>` if the app data folder is located elsewhere.
Manifest format and host-state mapping: [docs/how-kimi-work-pet-works.md](docs/how-kimi-work-pet-works.md).
Code is MIT; bundled assets are community fan art (CC BY-NC, personal use only).
Not affiliated with Moonshot AI or OpenAI.
