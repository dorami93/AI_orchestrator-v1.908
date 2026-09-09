#===============================================================
# server.py
#
# 常駐サーバー。ブラウザを1つ起動し保持したまま、
# ソケット経由で複数URL(タブ)への入力・回答取得を処理する。
#
# Setup:
#   uv add playwright markdownify
#   uv run playwright install chromium
#
# Run:
#   python3 server.py
#
# 別ターミナルから:
#   python3 call_cli_llm.py -url "https://chatgpt.com"
#
# サイト追加/変更は sites.json を編集するだけでよい
#
# 停止: Ctrl+C
#===============================================================

import asyncio
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from markdownify import markdownify as html_to_markdown

HOST, PORT = "127.0.0.1", 8765
SITE_CONFIGS = json.loads((Path(__file__).parent / "sites.json").read_text(encoding="utf-8"))

STREAM_MARKER_RE = re.compile(
    r'(start|marker)\s+name="assistant-pending-[a-zA-Z0-9-]*"\?'
    r'|(?<![a-zA-Z])end\s\?',
)


def get_config(url):
    return SITE_CONFIGS.get(urlparse(url).netloc.replace("www.", ""), SITE_CONFIGS["default"])


class BrowserManager:
    def __init__(self):
        self.pages = {}
        self.locks = {}

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=["--window-position=-10000,-10000", "--window-size=400,300", "--mute-audio"],
        )
        self.context = await self.browser.new_context(
            permissions=["clipboard-read", "clipboard-write"],
            viewport={"width": 400, "height": 300},
        )

    async def get_or_open_page(self, key, url):
        if key in self.pages:
            return self.pages[key]
        page = await self.context.new_page()
        await page.goto(url, wait_until="domcontentloaded")
        self.pages[key] = page
        self.locks[key] = asyncio.Lock()
        return page

    async def ask(self, session_id, url, text):
        key = (session_id, url)
        config = get_config(url)
        page = await self.get_or_open_page(key, url)
        async with self.locks[key]:
            try:
                box = page.locator(config["input_selector"]).first
                await box.wait_for(state="visible", timeout=10000)
                await box.fill(text)
                await box.press("Enter")

                copy_button = page.get_by_role("button", name=config["copy_button_name"]).last
                await copy_button.wait_for(state="visible", timeout=120000)
                ancestor = copy_button.locator("xpath=" + "/".join([".."] * config["answer_ancestor_level"]))
                markdown = html_to_markdown(await ancestor.inner_html()).strip()
                markdown = STREAM_MARKER_RE.sub("", markdown)
                return re.sub(r"\n{3,}", "\n\n", markdown).strip()
            except PlaywrightTimeoutError:
                return "[エラー] タイムアウトしました"


async def handle_client(reader, writer, manager):
    req = json.loads((await reader.readline()).decode())
    print(f"[server] 受信 [{req['session_id']}] ({req['url']}): {req['text']}")
    answer = await manager.ask(req["session_id"], req["url"], req["text"])
    writer.write((json.dumps({"answer": answer}) + "\n").encode())
    await writer.drain()
    writer.close()


async def main():
    manager = BrowserManager()
    await manager.start()
    print(f"[server] 起動完了。{HOST}:{PORT} で待ち受け中")
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, manager), HOST, PORT)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
