# kimi-work-pets

[![Kimi Work 桌宠](https://img.shields.io/badge/在线画廊-Kimi%20Work%20桌宠-0c7c6e)](https://caseclose.github.io/kimi-work-pets/)
[![内置宠物](https://img.shields.io/badge/内置宠物-15-0c7c6e)](#内置宠物)
[![Codex Pet v2](https://img.shields.io/badge/Codex%20Pet%20v2-16%20方向-d8893d)](#v2-视线跟随更新)

把 [Codex 社区桌宠](https://codexpets.net/)装进 **Kimi Work 桌面端**(macOS / Windows)。

**在线画廊（GitHub Pages）：** [https://caseclose.github.io/kimi-work-pets/](https://caseclose.github.io/kimi-work-pets/) — 浏览全部 15 款宠物、GIF 演示与安装说明。

Kimi Work 内置桌宠除默认 Rive 形象外,还支持精灵图(spritesheet)模式,与 Codex 社区宠物素材(8×9 网格、192×208 单元格)格式同源。本仓库也支持 Codex v2 的 8×11 图集:后两行提供 16 个视线方向。本仓库提供转换、安装、回滚工具;社区画廊里的宠物按同样流程都可以装。

## v2 视线跟随更新

本轮已把 **Dimo(迪莫)** 升级为 Codex Pet v2,并新增 **Yoimiya(宵宫)** 的
Kimi Work 适配。两只宠物都保留 9 行标准动作,再用第 9、10 行承载 16 个
视线方向:以正上方为 0°,顺时针每 22.5° 一帧。鼠标越过角色中心死区后,
桌宠会直接切换对应方向帧;其余 v1 宠物继续使用平滑倾斜兼容模式。

| v2 宠物 | 预览 | 安装命令 |
| --- | --- | --- |
| **Dimo(迪莫)** · 《洛克王国》 | <img src="assets/dimo/pet-states.gif" width="150" alt="Dimo v2 动作与方向演示"> | `python3 scripts/install.py pets/dimo` |
| **Yoimiya(宵宫)** · 《原神》 | <img src="assets/yoimiya/pet-states.gif" width="150" alt="宵宫 v2 动作与方向演示"> | `python3 scripts/install.py pets/yoimiya` |

两份 v2 包均采用 `1536×2288` 的 8×11 图集、`192×208` 单帧,并在
`pet.json` 中显式声明 `spriteVersionNumber: 2` 与全部 16 个
`lookDirections`。安装器会自动注入视线跟随、悬停互动、唤醒防闪烁和
canvas 渲染补丁;无需另行运行补丁脚本。

## 内置宠物

`pets/` 下每只宠物一个目录,安装命令为 `python3 scripts/install.py pets/<目录名>`:

| 宠物 | 预览 | 状态演示 |
| --- | --- | --- |
| **Dimo(迪莫)** · **v2 / 16 方向**,《洛克王国》光属性明星宠物([角色背景](https://baike.baidu.com/item/%E8%BF%AA%E8%8E%AB/10570042);社区二创,作者 [swrited](https://codexpets.net/gallery/dimo)) | <img src="assets/dimo/pet-preview.png" width="150"> | <img src="assets/dimo/pet-states.gif" width="130"> |
| **Siam(暹罗猫)**,小体型暹罗猫(作者 [allen](https://codexpets.net/gallery/siam)) | <img src="assets/siam/pet-preview.png" width="150"> | <img src="assets/siam/pet-states.gif" width="130"> |
| **Maomao(大开门)**,戴蓝色钩针帽的三花猫(作者 [kyle](https://codexpets.net/gallery/maomao)) | <img src="assets/maomao/pet-preview.png" width="150"> | <img src="assets/maomao/pet-states.gif" width="130"> |
| **Hiyuki**,持冰剑的银发红瞳 Q 版少女(作者 [foxibu](https://codexpets.net/gallery/hiyuki)) | <img src="assets/hiyuki/pet-preview.png" width="150"> | <img src="assets/hiyuki/pet-states.gif" width="130"> |
| **Feixue(绯雪)**,冷艳巫女风 Q 版少女(作者 [Akira97](https://codexpets.net/gallery/feixue)) | <img src="assets/feixue/pet-preview.png" width="150"> | <img src="assets/feixue/pet-states.gif" width="130"> |
| **GUGUGAGA**,企鹅装 Q 版少女(作者 [Hibik1](https://codexpets.net/gallery/endminguga)) | <img src="assets/endminguga/pet-preview.png" width="150"> | <img src="assets/endminguga/pet-states.gif" width="130"> |
| **Round Cola Hatch**,喝可乐的蓝色圆滚滚机器人(作者 [tsang](https://codexpets.net/gallery/round-cola-hatch)) | <img src="assets/round-cola-hatch/pet-preview.png" width="150"> | <img src="assets/round-cola-hatch/pet-states.gif" width="130"> |
| **胡桃(Hu Tao)**,《原神》往生堂堂主,带小幽灵(作者 [Barometer](https://codexpets.net/gallery/hu-tao-pet);形象版权归米哈游) | <img src="assets/hu-tao-pet/pet-preview.png" width="150"> | <img src="assets/hu-tao-pet/pet-states.gif" width="130"> |
| **Flamy**,戴破碎眼镜敲笔记本的红色小火龙(作者 [inwizzy](https://codexpets.net/gallery/flamy)) | <img src="assets/flamy/pet-preview.png" width="150"> | <img src="assets/flamy/pet-states.gif" width="130"> |
| **Kimlet Move Wave**,像素风挥手人物(作者 [kimehwa](https://codexpets.net/gallery/kimlet-move-wave);⚠️ 真人形象戏仿,介意请勿安装) | <img src="assets/kimlet-move-wave/pet-preview.png" width="150"> | <img src="assets/kimlet-move-wave/pet-states.gif" width="130"> |
| **Kimlet**,带光环挥手人物(作者 [kimehwa](https://codexpets.net/gallery/kimlet);⚠️ 真人形象戏仿,介意请勿安装) | <img src="assets/kimlet/pet-preview.png" width="150"> | <img src="assets/kimlet/pet-states.gif" width="130"> |
| **星见雅(Miyabi)**,《绝区零》对空六课狐耳剑士(作者 [Eric-Terminal](https://codexpets.net/gallery/miyabi);形象版权归米哈游) | <img src="assets/miyabi/pet-preview.png" width="150"> | <img src="assets/miyabi/pet-states.gif" width="130"> |
| **薇尔莉特(Violet)**,《紫罗兰永恒花园》自动手记人偶(作者 [Lazenca](https://codexpets.net/gallery/violet);形象版权归京都动画) | <img src="assets/violet/pet-preview.png" width="150"> | <img src="assets/violet/pet-states.gif" width="130"> |
| **咕嘎(Guga)**,圆润版企鹅装连帽少女(作者 [CIRCUS](https://codexpets.net/gallery/guga)) | <img src="assets/guga/pet-preview.png" width="150"> | <img src="assets/guga/pet-states.gif" width="130"> |
| **宵宫(Yoimiya)** · **v2 / 16 方向**,《原神》长野原烟花店店主与火花骑士(社区二创,作者 [Ruller](https://codexpets.net/gallery/yoimiya);形象版权归米哈游) | <img src="assets/yoimiya/pet-preview.png" width="150"> | <img src="assets/yoimiya/pet-states.gif" width="130"> |

## 快速开始

要求:Kimi Work 桌面端、`python3`。支持 **macOS / Windows**(Windows 路径按 Electron
惯例定位 `%APPDATA%\kimi-desktop`,未经真机验证;若定位失败,各脚本均支持
`--appdata <Kimi应用数据目录>` 手动指定)。

```bash
git clone https://github.com/caseclose/kimi-work-pets.git
cd kimi-work-pets
python3 scripts/install.py pets/dimo   # 换成 pets/ 下任意目录名即可
```

重启 Kimi 应用(或重新开关桌宠)后生效,桌宠已带悬停交互(见下节)。
回滚默认形象:`python3 scripts/restore.py`(原配置自动备份在用户目录的 `.kimi-work-pet-backup/`)。

### 在多个宠物之间切换

安装过的宠物会进入应用的宠物素材库,之后**不必重跑 install.py**:
打开「设置 → 桌面宠物 → 选择桌面宠物」,列表里点「切换」即可——应用会为选中的
宠物创建专属渲染组件(并复制当前渲染器,已注入的交互补丁随之保留)。
切换列表只显示通过应用 manifest 校验的宠物,所以请确保清单是本仓库最新版本
(见上文的校验要求);重跑 `install.py` 会同时刷新素材库里的对应文件。

注意:**应用升级可能重置渲染器**,导致交互补丁丢失。发现悬停/视线跟随等
行为消失时,重跑一次 `python3 scripts/install.py pets/<当前宠物>` 即可重新注入
(空闲闪烁修复与 canvas 渲染自 2026-09-18 的应用版本起已官方内置,无需补丁)。

## 安装其他社区宠物

1. 从 [CodexPets.net](https://codexpets.net/)(或 petdex.dev 等画廊)下载宠物包并解压(内含 `pet.json` + `spritesheet.webp`);
2. 转换:`python3 scripts/convert-codex-pet.py <目录>`(自动统计每行实际帧数,原清单备份为 `pet.codex.json`);
3. 安装:`python3 scripts/install.py <目录>`。

转换器自动识别标准 v1(9 行)和 v2(11 行)布局。前 9 行都按下表映射动作:

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
| 8 | react/review | 空闲彩蛋 3(互动,全部宠物已映射) |

v2 的第 9、10 行按从正上方 0° 起、顺时针每 22.5° 一帧映射为 16 个
`lookDirections`。当前内置 Dimo 与宵宫已升级到 v2;光标越过角色中心死区后会直接切换
对应方向帧，而不是只做整体倾斜。

注意:新版 Kimi Work 应用(2026-09 起)启用桌宠前会校验 manifest——
`states.dragLeft` / `states.dragRight` 必填(与 `running_left` / `running_right`
共用行即可),`provenance.provider` 限 `image_generation` / `pixellab` / `manual` /
`other`。仓库内全部宠物与转换器输出均已满足;缺字段时应用设置页会报
"读取桌面宠物状态失败"且无法启用桌宠。

布局不符时,用 `scripts/inspect_spritesheet.py` 逐行确认动作后手动调整 `pet.json`;
manifest 字段与宿主状态映射详见 [Kimi Work 桌宠机制调研](https://caseclose.github.io/kimi-work-pets/how-kimi-work-pet-works.html)。

## 交互行为

安装即自带,无需额外操作(`restore.py` 会一并还原页面、全部撤销)。所有互动只在
宠物空闲时触发,不影响工作/等待/失败等任务状态驱动:

- **开机问候**:桌宠加载完成后,主动随机播放一个空闲彩蛋动作(如招手、眨眼)打招呼。
- **悬停回应**:鼠标悬停桌宠时,随机回应一个空闲彩蛋动作(招手 / 眨眼 / 跳跃,
  素材里有的才会被选中),6 秒冷却。
- **点击跳跃**:点击/轻点桌宠,兴奋地随机跳跃或眨眼,3 秒冷却。
- **长视撒娇**:鼠标停留在桌宠身上超过 2.6 秒不放,她会撒娇大哭(failed)约两个循环。
- **视线跟随**:v2 精灵图宠物根据光标角度切换 16 个方向帧;普通 v1 精灵图继续
  平滑地向光标方向倾斜、偏移。离开后回正;Rive 宠物自带眼动状态机会自动跳过。
- **拖动奔跑**:拖动桌宠时朝拖动方向奔跑(应用原生行为)。
- **气泡信息增强**:任务运行时,头顶气泡在原有状态文案之外追加"已用 N 种工具
  (Bash、WebSearch、Read…)"(按回合累计)和"已工作 X 分钟/秒"(页面本地计时,
  每 15 秒自动刷新),不再只有"正在思考…";回合结束自动重置。
  例:`正在思考… · 已用 5 种工具(Bash、WebSearch、Read…) · 已工作 2 分钟`。
- **显示与响应范围**:宠物显示为默认的 2 倍大小;悬停/点击的响应范围在宠物轮廓外
  再外扩 24px,不用精确对准(由页面主动上报可交互区域实现)。

部分宠物素材带有第 9 行隐藏动作(眨眼、庆祝等),转换时已映射为 `idle_random_3`
纳入随机彩蛋池;没有该行的宠物自动跳过,互不影响。

交互与稳定性由安装时自动注入的补丁实现(均幂等,可单独重复运行,
可加 `--appdata` 指定应用数据目录):
[patch-hover-interaction.py](scripts/patch-hover-interaction.py) ·
[patch-pet-interactions.py](scripts/patch-pet-interactions.py) ·
[patch-bubble-info.py](scripts/patch-bubble-info.py) ·
[patch-look-at-cursor.py](scripts/patch-look-at-cursor.py) ·
[patch-pet-display.py](scripts/patch-pet-display.py) ·
[patch-idle-flicker.py](scripts/patch-idle-flicker.py) ·
[patch-sprite-canvas.py](scripts/patch-sprite-canvas.py)。

## 已知问题:空闲后闪烁(已修复)

长时间不操作鼠标键盘后,桌宠可能出现两种闪烁,均有对应补丁:

**1. 唤醒瞬间姿势"瞬移"** —— 渲染器在指针离开 1 秒后切到 800ms 慢速动画档;
macOS 挂起不可见 WebView 期间计时器冻结,唤醒后 `tick()` 按累积时间一次补跳
几十上百帧。修复:`python3 scripts/patch-idle-flicker.py` —— 挂起超过 4 个帧间隔
只前进 1 帧并对齐时间轴;`visibilitychange` 恢复可见时重置时间轴并重启动画调度。

**2. 播放动画时人物"消失一小会儿"** —— 精灵图用 CSS `background-image` 切帧,
WebKit 挂起后丢弃已解码图片数据,唤醒后第一次切帧时 CSS 背景异步重新解码,
解码完成前先合成空白。修复:`python3 scripts/patch-sprite-canvas.py` —— 改为
canvas 2d 渲染(`drawImage` 对未解码图片同步重解码,不出空白帧),并在唤醒时
立即同步重绘;CSS 背景路径保留为图片加载前的回退。

两个补丁均幂等,支持 `--appdata` 参数;`install.py` 安装时会自动应用,无需手动重跑。
重启 Kimi 应用后生效。

## 全屏时置顶(宿主应用补丁)

macOS 上其他应用全屏后,桌宠默认不会浮到全屏空间之上:宿主给组件 pin 窗口
只用默认 floating 层级,且未开 `visibleOnFullScreen`。修复:

```bash
python3 scripts/patch-fullscreen-level.py
```

该补丁直接修改 `Kimi.app` 主进程(与宿主图片 pin 窗口同款行为):
置顶层级提升为 `screen-saver`,并开启
`setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true, skipTransformProcessType: true })`。
脚本自动重算并写回 `ElectronAsarIntegrity` 哈希(否则应用无法启动),
修改前备份 `app.asar` / `app.asar.unpacked` / `Info.plist`(后缀
`.bak-pet-fullscreen`);`--check` 只检查不修改,`--restore` 一键还原。
**完全退出 Kimi(⌘Q)再重开后生效;应用升级会覆盖补丁,升级后重跑即可。**

## 版权

- 代码:MIT(见 LICENSE)。
- **社区原创素材**(siam/maomao/hiyuki/feixue/endminguga/round-cola-hatch/flamy/guga):
  来自 Codex 社区画廊,版权以各来源页面为准,**仅供个人非商业使用**。
- **含第三方 IP 形象**:
  - dimo:社区二创(作者 swrited,CC BY-NC 类协议);迪莫形象来自腾讯《洛克王国》,权利归原版权方。
  - hu-tao-pet 与 yoimiya:胡桃、宵宫形象来自米哈游《原神》;miyabi:星见雅形象来自米哈游《绝区零》;
    violet:薇尔莉特形象来自京都动画《紫罗兰永恒花园》——权利均归原版权方。
- **戏仿内容**(kimlet/kimlet-move-wave):含真实公众人物形象,**仅供个人非商业使用**,介意者可不安装。
- 本仓库与 Moonshot AI、OpenAI 无任何隶属或授权关系。

## English

Install Codex community pets as the desktop pet of the Kimi Work desktop app (macOS/Windows).
Run `python3 scripts/install.py pets/<dir>` for any of the 15 bundled pets (see the gallery
table above; includes Dimo from Tencent's *Roco Kingdom*, a Siamese cat, a calico cat,
several original chibi characters, Hu Tao and Yoimiya from *Genshin Impact*, Hoshimi Miyabi from
*Zenless Zone Zero*, Violet Evergarden, and two pixel-art public-figure parodies).
Convert new pets with `scripts/convert-codex-pet.py`, roll back with `scripts/restore.py`.
Installation also injects interactions: a startup greeting, random hover/tap reactions
(wave, wink, jump), a long-hover tease where the pet bursts into tears, and sprite pets
use 16-direction look frames for Codex v2 atlases (with the original smooth-lean fallback
for v1 sprites) as you move the mouse around.
All scripts accept `--appdata <dir>` if the app data folder is located elsewhere.
Manifest format and host-state mapping: [how the Kimi Work pet works](https://caseclose.github.io/kimi-work-pets/how-kimi-work-pet-works.html).
Known issue fixed: after long pointer inactivity the pet could visibly "jump" when the screen recomposited — the renderer clamps frame catch-up after system suspension and resets on visibility recovery; apply `scripts/patch-idle-flicker.py` and restart the app.
Code is MIT; bundled assets are community fan art (CC BY-NC, personal use only).
Not affiliated with Moonshot AI or OpenAI.
