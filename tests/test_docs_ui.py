#!/usr/bin/env python3
import http.server
import json
import os
import socketserver
import subprocess
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PWCLI = Path.home() / ".codex" / "skills" / "playwright" / "scripts" / "playwright_cli.sh"
SESSION = "docs-ui-tests"


def _playwright():
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except ImportError:
        return None


class DocsUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class QuietHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(DOCS), **kwargs)

            def log_message(self, format, *args):
                return

        cls._httpd = socketserver.TCPServer(("127.0.0.1", 0), QuietHandler)
        cls._httpd.allow_reuse_address = True
        cls.port = cls._httpd.server_address[1]
        cls._thread = threading.Thread(target=cls._httpd.serve_forever, daemon=True)
        cls._thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"
        cls._pw_factory = _playwright()

    @classmethod
    def tearDownClass(cls):
        cls._httpd.shutdown()
        cls._httpd.server_close()

    def test_theme_filter_search_copy_menu_and_hash(self):
        if self._pw_factory is not None:
            self._run_python_playwright()
            return
        if not PWCLI.is_file():
            self.skipTest("playwright 不可用")
        env = os.environ.copy()
        env["PLAYWRIGHT_CLI_SESSION"] = SESSION
        self._cli(env, "open", self.base + "/")
        theme = self._eval(env, "() => document.documentElement.getAttribute('data-theme')")
        self._eval(env, "() => document.getElementById('theme-toggle').click()")
        flipped = self._eval(env, "() => document.documentElement.getAttribute('data-theme')")
        self.assertNotEqual(theme, flipped)

        parody = self._eval(
            env,
            "() => { document.querySelector('[data-filter=parody]').click(); return document.getElementById('pet-count').textContent; }",
        )
        self.assertEqual(parody, "显示 2 / 15 款")

        search = self._eval(
            env,
            "() => { document.querySelector('[data-filter=all]').click(); const s=document.getElementById('pet-search'); s.value='胡桃'; s.dispatchEvent(new Event('input')); return document.getElementById('pet-count').textContent; }",
        )
        self.assertEqual(search, "显示 1 / 15 款")
        copies = self._eval(env, "() => document.querySelectorAll('.copy-btn').length")
        self.assertGreaterEqual(copies, 15)

        self._cli(env, "open", self.base + "/#dimo")
        hash_count = self._eval(env, "() => document.getElementById('pet-count').textContent")
        dimo_hidden = self._eval(
            env, "() => document.getElementById('dimo').classList.contains('hidden')"
        )
        self.assertEqual(hash_count, "显示 15 / 15 款")
        self.assertIs(dimo_hidden, False)

        self._cli(env, "resize", "390", "844")
        self._cli(env, "open", self.base + "/")
        menu = self._eval(
            env,
            "() => { const b=document.getElementById('menu-toggle'); b.click(); const opened=b.getAttribute('aria-expanded'); document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true})); return {opened, closed:b.getAttribute('aria-expanded')}; }",
        )
        self.assertEqual(menu["opened"], "true")
        self.assertEqual(menu["closed"], "false")

        self._cli(env, "open", self.base + "/how-kimi-work-pet-works.html")
        title = self._eval(env, "() => document.querySelector('h1').textContent")
        self.assertIn("桌面宠物机制调研", title)

    def _cli(self, env, *args):
        subprocess.run(
            ["bash", str(PWCLI), "--session", SESSION, *args],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )

    def _eval(self, env, expr):
        result = subprocess.run(
            ["bash", str(PWCLI), "--session", SESSION, "eval", expr],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )
        text = result.stdout
        start = text.find("### Result")
        if start == -1:
            self.fail("playwright eval 没有 Result:\n" + text)
        rest = text[start + len("### Result") :].lstrip("\n")
        end = rest.find("\n### ")
        payload = (rest if end == -1 else rest[:end]).strip()
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return payload

    def _run_python_playwright(self):
        with self._pw_factory() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(self.base + "/", wait_until="domcontentloaded")
            theme = page.get_attribute("html", "data-theme")
            page.locator("#theme-toggle").click()
            self.assertNotEqual(page.get_attribute("html", "data-theme"), theme)
            page.get_by_role("button", name="戏仿").click()
            self.assertEqual(page.locator("#pet-count").inner_text(), "显示 2 / 15 款")
            page.get_by_role("button", name="全部").click()
            page.locator("#pet-search").fill("胡桃")
            self.assertEqual(page.locator("#pet-count").inner_text(), "显示 1 / 15 款")
            page.goto(self.base + "/#dimo", wait_until="domcontentloaded")
            page.wait_for_function(
                "() => !document.getElementById('dimo').classList.contains('hidden')"
            )
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(self.base + "/", wait_until="domcontentloaded")
            page.locator("#menu-toggle").click()
            page.keyboard.press("Escape")
            self.assertEqual(
                page.locator("#menu-toggle").get_attribute("aria-expanded"), "false"
            )
            page.goto(
                self.base + "/how-kimi-work-pet-works.html",
                wait_until="domcontentloaded",
            )
            self.assertIn("桌面宠物机制调研", page.locator("h1").inner_text())
            browser.close()


if __name__ == "__main__":
    unittest.main()
