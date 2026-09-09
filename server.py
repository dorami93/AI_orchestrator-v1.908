# ============================================================
# server.py
#
# 常駐サーバー。ブラウザを1つ起動し保持したまま、
# ソケット経由で複数URL(タブ)への入力・回答取得を処理する。
#
# Setup:
#   uv add playwright html2text
#   uv run playwright install chromium
#
# Run:
#   python3 server.py
#
# 別ターミナルから:
#   python3 call_cli_llm.py -url "https://chatgpt.com"
#
# 停止: Ctrl+C
# ============================================================

import asyncio
import json
import re
import html2text
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

HOST, PORT = "127.0.0.1", 8765
converter = html2text.HTML2Text()
converter.body_width = 0

SITE_CONFIGS = {
    "chatgpt.com": {
        "input_selector": "textarea",
        "wait_for_text": "回答が完了しました",
        "answer_selector": "[data-assistant-markdown]",
    },
    "claude.ai": {
        "input_selector": "div[contenteditable='true']",
        "wait_for_text": None,
        "answer_selector": "[data-testid='message-content']",
    },
}
DEFAULT_CONFIG = SITE_CONFIGS["chatgpt.com"]


def get_config(url):
    return SITE_CONFIGS.get(urlparse(url).netloc.replace("www.", ""), DEFAULT_CONFIG)


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

    async def get_or_open_page(self, key, url):
        if key in self.pages:
            return self.pages[key]
        page = await self.browser.new_page(viewport={"width": 400, "height": 300})
        await page.route("**/*", lambda route: route.abort()
                          if route.request.resource_type in {"image", "font", "media"}
                          else route.continue_())
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

                if config["wait_for_text"]:
                    await page.get_by_text(config["wait_for_text"], exact=True).wait_for(timeout=120000)
                else:
                    await page.wait_for_load_state("networkidle", timeout=120000)

                answer_html = await page.locator(config["answer_selector"]).last.inner_html()
                answer_html = re.sub(r"<\?.*?\?>", "", answer_html)
                return converter.handle(answer_html).strip()
            except PlaywrightTimeoutError:
                return "[エラー] タイムアウトしました"

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()


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
