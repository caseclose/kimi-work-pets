# wbxl2000/kimi-pet 仓库调研笔记

> 调研日期:2026-09-15 · 仓库:https://github.com/wbxl2000/kimi-pet

## 定位

面向 **Kimi Code(命令行编码工具)** 的第三方桌宠插件,通过插件市场安装:

```
/plugins install https://github.com/wbxl2000/kimi-pet
```

注意:它管理的是 Kimi Code CLI 的悬浮窗宠物,**与 Kimi Work 桌面端内置桌宠是两套独立体系**。
想让 Kimi Work 桌面端换形象,需要直接改本仓库 README 所述的配置文件。

## 架构

```
Kimi Code 会话事件
  → 插件 hooks(hooks/pet-hook.mjs,node,fire-and-forget)
  → <kimi_home>/pets/run/sessions/<session_id>.json   (状态文件)
  → pet daemon(daemon/pet_daemon.py,PySide6)轮询(250ms)
  → 无边框、透明、置顶悬浮窗
```

宠物状态与触发条件:

| 状态 | 触发 |
| --- | --- |
| `running` | 提交 prompt、工具调用、压缩、子代理(静默 10 分钟后衰减) |
| `waiting` | 有待处理的权限请求(会响铃,不衰减) |
| `review` | 回合结束 / 后台通知(庆祝约 60 秒后回空闲) |
| `failed` | 工具或回合失败(数秒后衰减) |
| `idle` | 会话空闲 |
| `waving` / `jumping` | 宠物出现 / 鼠标悬停 |

多会话按 `waiting > failed > running > review > idle` 优先级聚合。
气泡显示活跃会话数、项目名与当前动作;点击气泡可暂时关闭。

## 素材生态(重点)

- 宠物素材遵循 **Codex 社区格式**:`~/.kimi-code/pets/<pet-id>/{pet.json, spritesheet.webp}`
- 精灵图规格:**8×9 网格,192×208 单元格,1536×1872 WebP**
- 自动回退读取 `~/.codex/pets/` —— 给 Codex 装过的宠物可直接用
- 社区画廊通过 `petctl install <slug>` 安装;大多数作品是粉丝二创(**CC BY-NC 或类似,仅限个人非商业使用**)
- 自带 `hatch-pet` skill:向 agent 说 "hatch a pet" 可从头生成兼容素材

## 命令行控制(petctl,零依赖 node 脚本)

```bash
node bin/petctl.mjs gallery      # 浏览社区画廊
node bin/petctl.mjs install <slug>
node bin/petctl.mjs summon       # 首次运行会下载预编译 daemon(约 100MB PySide6 兜底)
node bin/petctl.mjs use <pet-id> # 切换宠物
node bin/petctl.mjs status / dismiss
```

## 对本项目的启发

Kimi Work 内置桌宠的精灵图 manifest 状态机(见 docs/how-kimi-work-pet-works.md)
与 Codex 素材的行列布局高度同源:Codex 包的 9 行通常依次是
`idle / running_right / running_left / waving / jumping / failed / waiting / running / review`,
可以直接映射到 Kimi Work 的
`idle / running_right / running_left / idle_random_1 / idle_random_2 / failed / waiting / working`。
