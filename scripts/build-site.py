#!/usr/bin/env python3
"""为 GitHub Pages 生成展示站点(docs/)。

用法: python3 scripts/build-site.py

- 拷贝 assets/<pet>/pet-preview.png 到 docs/assets/<pet>/
- 拷贝 pet-states.gif,并压缩为 docs/assets/<pet>/pet-states.webp(宽度上限 360px,保留动画)
- 生成 docs/index.html、docs/robots.txt、docs/sitemap.xml

注意: docs/index.html 在初版生成后经过多轮手工打磨(主题切换、品牌图标、
结构化数据等),本脚本的 build_index() 只会产出极简回退版。日常更新只应
调用 build_assets();如需整页重建,先确认接受覆盖。
"""
import html
import json
import shutil
from datetime import date
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets"
DOCS = REPO / "docs"
SITE = "https://caseclose.github.io/kimi-work-pets"
GITHUB = "https://github.com/caseclose/kimi-work-pets"
MAX_GIF_WIDTH = 360

# 顺序即页面展示顺序(与 README 表格一致)
PETS = [
    {"id": "dimo", "name": "Dimo(迪莫)",
     "desc": "《洛克王国》光属性明星宠物(社区二创)",
     "author": "swrited", "ip": "形象源自腾讯《洛克王国》"},
    {"id": "siam", "name": "Siam(暹罗猫)", "desc": "小体型暹罗猫", "author": "allen", "ip": ""},
    {"id": "maomao", "name": "Maomao(大开门)", "desc": "戴蓝色钩针帽的三花猫", "author": "kyle", "ip": ""},
    {"id": "hiyuki", "name": "Hiyuki", "desc": "持冰剑的银发红瞳 Q 版少女", "author": "foxibu", "ip": ""},
    {"id": "feixue", "name": "Feixue(绯雪)", "desc": "冷艳巫女风 Q 版少女", "author": "Akira97", "ip": ""},
    {"id": "endminguga", "name": "GUGUGAGA", "desc": "企鹅装 Q 版少女", "author": "Hibik1", "ip": ""},
    {"id": "round-cola-hatch", "name": "Round Cola Hatch", "desc": "喝可乐的蓝色圆滚滚机器人", "author": "tsang", "ip": ""},
    {"id": "hu-tao-pet", "name": "胡桃(Hu Tao)", "desc": "《原神》往生堂堂主,带小幽灵", "author": "Barometer", "ip": "形象版权归米哈游"},
    {"id": "flamy", "name": "Flamy", "desc": "戴破碎眼镜敲笔记本的红色小火龙", "author": "inwizzy", "ip": ""},
    {"id": "kimlet-move-wave", "name": "Kimlet Move Wave", "desc": "像素风挥手人物", "author": "kimehwa", "ip": "⚠️ 真人形象戏仿,介意请勿安装"},
    {"id": "kimlet", "name": "Kimlet", "desc": "带光环挥手人物", "author": "kimehwa", "ip": "⚠️ 真人形象戏仿,介意请勿安装"},
    {"id": "miyabi", "name": "星见雅(Miyabi)", "desc": "《绝区零》对空六课狐耳剑士", "author": "Eric-Terminal", "ip": "形象版权归米哈游"},
    {"id": "violet", "name": "薇尔莉特(Violet)", "desc": "《紫罗兰永恒花园》自动手记人偶", "author": "Lazenca", "ip": "形象版权归京都动画"},
    {"id": "guga", "name": "咕嘎(Guga)", "desc": "圆润版企鹅装连帽少女", "author": "CIRCUS", "ip": ""},
]


def build_assets() -> None:
    from PIL import Image

    for pet in PETS:
        src_dir = ASSETS / pet["id"]
        dst_dir = DOCS / "assets" / pet["id"]
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_dir / "pet-preview.png", dst_dir / "pet-preview.png")

        src_gif = src_dir / "pet-states.gif"
        shutil.copy2(src_gif, dst_dir / "pet-states.gif")
        dst_webp = dst_dir / "pet-states.webp"
        im = Image.open(src_gif)
        frames, durations = [], []
        for i in range(getattr(im, "n_frames", 1)):
            im.seek(i)
            frame = im.convert("RGB")
            if frame.width > MAX_GIF_WIDTH:
                ratio = MAX_GIF_WIDTH / frame.width
                frame = frame.resize(
                    (MAX_GIF_WIDTH, max(1, round(frame.height * ratio))), Image.LANCZOS
                )
            frames.append(frame)
            durations.append(int(im.info.get("duration", 200) or 200))
        frames[0].save(
            dst_webp, "WEBP", save_all=True, append_images=frames[1:],
            duration=durations, quality=80, method=6, loop=0,
        )


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def build_index() -> str:
    cards = []
    for pet in PETS:
        pid = pet["id"]
        gallery = f"https://codexpets.net/gallery/{pid}"
        ip_line = f'<p class="ip">{esc(pet["ip"])}</p>' if pet["ip"] else ""
        cards.append(f"""      <article class="card" id="{pid}">
        <div class="card-media">
          <img class="preview" src="assets/{pid}/pet-preview.png" alt="{esc(pet['name'])} 桌宠预览图" loading="lazy">
          <img class="states" src="assets/{pid}/pet-states.webp" alt="{esc(pet['name'])} 逐行动作演示" loading="lazy">
        </div>
        <h3>{esc(pet['name'])}</h3>
        <p class="desc">{esc(pet['desc'])}</p>
        <p class="author">作者 <a href="{gallery}" rel="noopener">{esc(pet['author'])}</a> · <a href="{gallery}" rel="noopener">Codex Pets 画廊</a></p>
        {ip_line}
        <div class="install"><code>python3 scripts/install.py pets/{pid}</code></div>
      </article>""")

    pet_jsonld_items = ",\n".join(
        '    {"@type": "ListItem", "position": %d, "name": %s, "url": "%s/#%s"}'
        % (i + 1, json.dumps(pet["name"].split("(")[0].strip()), SITE, pet["id"])
        for i, pet in enumerate(PETS)
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kimi Work Pets — Kimi Work 桌面宠物合集(迪莫、Hiyuki、胡桃等 14 款)</title>
  <meta name="description" content="把 Codex Pets 社区桌宠装进 Kimi Work 桌面端:一键安装迪莫、Hiyuki、绯雪、胡桃、星见雅、薇尔莉特等 14 款桌面宠物,支持悬停互动、视线跟随、macOS 与 Windows。">
  <meta name="keywords" content="Kimi Work,桌面宠物,桌宠,Codex Pets,迪莫,Hiyuki,胡桃,星见雅,薇尔莉特,desktop pet">
  <meta name="robots" content="index, follow">
  <meta name="google-site-verification" content="3O-yG5hm8o7yswYRIP9tyr6y5vBBJ4chKsrCtE2VOIg">
  <link rel="canonical" href="{SITE}/">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Kimi Work Pets">
  <meta property="og:title" content="Kimi Work Pets — Kimi Work 桌面宠物合集">
  <meta property="og:description" content="14 款 Codex Pets 社区桌宠一键装进 Kimi Work 桌面端,支持悬停互动与视线跟随。">
  <meta property="og:url" content="{SITE}/">
  <meta property="og:image" content="{SITE}/assets/dimo/pet-preview.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="assets/dimo/pet-preview.png">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Kimi Work Pets",
    "url": "{SITE}/",
    "description": "把 Codex Pets 社区桌宠装进 Kimi Work 桌面端的安装器与素材合集,含 14 款桌面宠物,支持悬停互动、视线跟随,兼容 macOS 与 Windows。",
    "applicationCategory": "UtilitiesApplication",
    "operatingSystem": "macOS, Windows",
    "offers": {{"@type": "Offer", "price": "0", "priceCurrency": "CNY"}},
    "codeRepository": "{GITHUB}",
    "license": "https://opensource.org/licenses/MIT",
    "hasPart": [
{pet_jsonld_items}
    ]
  }}
  </script>
  <style>
    :root {{
      --bg: #0f1115;
      --panel: #171a21;
      --text: #e8eaf0;
      --muted: #9aa1b0;
      --accent: #6ee7b7;
      --accent2: #7dd3fc;
      --border: #262b36;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif;
      line-height: 1.7;
    }}
    a {{ color: var(--accent2); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 20px; }}
    header.hero {{
      padding: 72px 0 40px;
      text-align: center;
      background: radial-gradient(ellipse at top, rgba(110,231,183,.08), transparent 60%);
    }}
    .hero h1 {{ font-size: 2.4rem; margin: 0 0 12px; }}
    .hero h1 .em {{ color: var(--accent); }}
    .hero p {{ color: var(--muted); max-width: 640px; margin: 0 auto 24px; }}
    .hero .cta a {{
      display: inline-block; margin: 0 6px; padding: 10px 22px;
      border-radius: 10px; border: 1px solid var(--border);
      background: var(--panel); color: var(--text); font-weight: 600;
    }}
    .hero .cta a.primary {{ background: var(--accent); color: #06251b; border-color: transparent; }}
    section {{ padding: 40px 0; }}
    h2 {{ font-size: 1.5rem; border-left: 4px solid var(--accent); padding-left: 12px; margin-bottom: 20px; }}
    .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }}
    .feature {{
      background: var(--panel); border: 1px solid var(--border);
      border-radius: 12px; padding: 16px 18px;
    }}
    .feature strong {{ color: var(--accent); }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
    .card {{
      background: var(--panel); border: 1px solid var(--border);
      border-radius: 14px; padding: 18px;
    }}
    .card-media {{ display: flex; gap: 12px; align-items: flex-start; margin-bottom: 12px; }}
    .card-media .preview {{ width: 46%; border-radius: 8px; background: #fff; }}
    .card-media .states {{ width: 50%; border-radius: 8px; image-rendering: pixelated; }}
    .card h3 {{ margin: 0 0 4px; font-size: 1.1rem; }}
    .card .desc {{ margin: 0 0 6px; color: var(--muted); font-size: .92rem; }}
    .card .author {{ margin: 0 0 4px; font-size: .85rem; }}
    .card .ip {{ margin: 0 0 8px; font-size: .82rem; color: #fbbf24; }}
    .card .install code {{
      display: block; background: #0b0d11; border: 1px solid var(--border);
      border-radius: 8px; padding: 8px 10px; font-size: .8rem;
      color: var(--accent); overflow-x: auto; white-space: nowrap;
    }}
    .steps {{ counter-reset: step; padding-left: 0; list-style: none; }}
    .steps li {{
      counter-increment: step; margin: 0 0 14px; padding: 14px 16px 14px 56px;
      background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
      position: relative;
    }}
    .steps li::before {{
      content: counter(step); position: absolute; left: 16px; top: 14px;
      width: 26px; height: 26px; border-radius: 50%;
      background: var(--accent); color: #06251b; font-weight: 700;
      display: flex; align-items: center; justify-content: center; font-size: .9rem;
    }}
    .steps code {{ background: #0b0d11; border: 1px solid var(--border); border-radius: 6px; padding: 2px 8px; font-size: .88rem; color: var(--accent2); }}
    footer {{
      border-top: 1px solid var(--border); margin-top: 40px; padding: 28px 0 48px;
      color: var(--muted); font-size: .85rem; text-align: center;
    }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="wrap">
      <h1>Kimi Work <span class="em">Pets</span></h1>
      <p>把 <a href="https://codexpets.net/" rel="noopener">Codex Pets</a> 社区桌宠一键装进 Kimi Work 桌面端。14 款精选宠物,自带悬停互动、视线跟随转头,兼容 macOS 与 Windows。</p>
      <div class="cta">
        <a class="primary" href="{GITHUB}">GitHub 仓库</a>
        <a href="#pets">浏览宠物</a>
      </div>
    </div>
  </header>

  <main class="wrap">
    <section id="features">
      <h2>特性</h2>
      <div class="features">
        <div class="feature"><strong>一键安装</strong><br>一条命令完成转换与注入,自动备份原桌宠,可随时回滚。</div>
        <div class="feature"><strong>悬停互动</strong><br>鼠标悬停时宠物主动打招呼(Hiyuki 挥剑、Dimo 挥爪)。</div>
        <div class="feature"><strong>视线跟随</strong><br>宠物会根据鼠标位置转动头部,时刻「看」着你。</div>
        <div class="feature"><strong>双平台</strong><br>支持 macOS 与 Windows,处理 Rive 动画与精灵表自动转换。</div>
      </div>
    </section>

    <section id="pets">
      <h2>宠物画廊(14 款)</h2>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </section>

    <section id="quickstart">
      <h2>快速开始</h2>
      <ol class="steps">
        <li>克隆仓库:<code>git clone {GITHUB}.git</code></li>
        <li>安装宠物(以迪莫为例):<code>python3 scripts/install.py pets/dimo</code></li>
        <li>重启 Kimi 应用,桌面上就会出现新桌宠;悬停试试它的互动动作。</li>
      </ol>
      <p>恢复默认桌宠:<code>python3 scripts/restore.py</code>(自动使用安装前的备份)。</p>
    </section>
  </main>

  <footer>
    <div class="wrap">
      <p>本站素材来自 <a href="https://codexpets.net/" rel="noopener">Codex Pets</a> 社区,版权归各位原作者;含第三方 IP 形象(腾讯、米哈游、京都动画)的宠物仅作社区二创展示。仓库代码以 MIT 协议开源。</p>
      <p><a href="{GITHUB}">GitHub</a> · <a href="{SITE}/sitemap.xml">Sitemap</a></p>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    build_assets()
    DOCS.mkdir(exist_ok=True)
    (DOCS / "index.html").write_text(build_index(), encoding="utf-8")
    pages = [f"{SITE}/", f"{SITE}/how-kimi-work-pet-works.html"]
    (DOCS / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n"
        f"Sitemap: {SITE}/sitemap.txt\n"
        f"Sitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8",
    )
    (DOCS / "sitemap.txt").write_text("\n".join(pages) + "\n", encoding="utf-8")
    today = date.today().isoformat()
    (DOCS / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url>\n    <loc>{pages[0]}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n"
        f"  <url>\n    <loc>{pages[1]}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    print(f"站点已生成: {DOCS}")


if __name__ == "__main__":
    sys.exit(main())
