# server.py
#
# 常駐サーバー。ブラウザを1つ起動したまま維持し、
# ローカルソケット経由で複数のURL(タブ)への入力・回答取得リクエストを処理する。
#
# ============================================================
# Setup:
#   uv add playwright
#   uv run playwright install chromium
#
# Run (このプロセスは起動しっぱなしにする):
#   python3 server.py
#
# 別ターミナルから:
#   python3 call_cli_llm.py -url "https://chatgpt.com"
#
# 停止:
#   Ctrl+C
# ============================================================

import asyncio
import json
import re
from urllib.parse import urlparse

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

HOST = "127.0.0.1"
PORT = 8765

# サイトごとの挙動設定。
# 新しいサイトに対応する場合はここにエントリを追加する。
SITE_CONFIGS = {
    "chatgpt.com": {
        "input_selector": "textarea",
        "submit": "enter",  # "enter" または "click_selector"
        "wait_for_text": "回答が完了しました",
        "extract": {
            "start_marker": "ChatGPT:",
            "end_marker": "ChatGPT は AI",
        },
    },
    "claude.ai": {
        "input_selector": "div[contenteditable='true']",
        "submit": "enter",
        "wait_for_text": None,  # 必要に応じて調整
        "extract": {
            "start_marker": None,
            "end_marker": None,
        },
    },
}

DEFAULT_CONFIG = SITE_CONFIGS["chatgpt.com"]


def get_site_config(url: str) -> dict:
    host = urlparse(url).netloc.replace("www.", "")
    return SITE_CONFIGS.get(host, DEFAULT_CONFIG)


class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.pages: dict[str, object] = {}  # url -> page
        self.locks: dict[str, asyncio.Lock] = {}  # url -> lock (同時アクセス防止)

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                "--window-position=-10000,-10000",
                "--window-size=400,300",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-sync",
                "--disable-translate",
                "--mute-audio",
                "--no-first-run",
                "--disable-default-apps",
            ],
        )

    async def get_or_open_page(self, url: str):
        if url in self.pages:
            return self.pages[url]

        page = await self.browser.new_page(viewport={"width": 400, "height": 300})

        async def block_resources(route):
            if route.request.resource_type in {"image", "font", "media"}:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", block_resources)
        await page.goto(url, wait_until="domcontentloaded")

        self.pages[url] = page
        self.locks[url] = asyncio.Lock()
        print(f"[server] タブを開きました: {url}")
        return page

    async def ask(self, url: str, text: str) -> str:
        config = get_site_config(url)
        page = await self.get_or_open_page(url)
        lock = self.locks[url]

        async with lock:
            try:
                input_box = page.locator(config["input_selector"]).first
                await input_box.wait_for(state="visible", timeout=10000)
                await input_box.fill(text)
                await input_box.press("Enter")

                if config.get("wait_for_text"):
                    await page.get_by_text(config["wait_for_text"], exact=True).wait_for(
                        state="visible",
                        timeout=120000,
                    )
                else:
                    # 完了マーカーが無いサイトはネットワークアイドルで代用
                    await page.wait_for_load_state("networkidle", timeout=120000)

                body = await page.locator("body").inner_text()

                start_marker = config["extract"]["start_marker"]
                end_marker = config["extract"]["end_marker"]

                if start_marker:
                    start = body.rfind(start_marker)
                    end = body.find(end_marker, start) if end_marker else len(body)
                    if start != -1:
                        answer = body[start + len(start_marker):end].strip()
                        return answer
                    return "(回答を抽出できませんでした)"
                else:
                    # マーカー未設定のサイトは末尾のテキストをそのまま返す(簡易)
                    return body[-2000:].strip()

            except PlaywrightTimeoutError:
                return "[エラー] 回答の取得がタイムアウトしました。"
            except Exception as e:
                return f"[エラー] {type(e).__name__}: {e}"

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


async def handle_client(reader, writer, manager: BrowserManager):
    try:
        raw = await reader.readline()
        if not raw:
            return
        try:
            req = json.loads(raw.decode())
        except json.JSONDecodeError:
            writer.write((json.dumps({"error": "invalid json"}) + "\n").encode())
            await writer.drain()
            return

        url = req.get("url")
        text = req.get("text")

        if not url or not text:
            writer.write((json.dumps({"error": "url and text required"}) + "\n").encode())
            await writer.drain()
            return

        print(f"[server] 受信 ({url}): {text}")
        answer = await manager.ask(url, text)
        writer.write((json.dumps({"answer": answer}) + "\n").encode())
        await writer.drain()

    except Exception as e:
        try:
            writer.write((json.dumps({"error": str(e)}) + "\n").encode())
            await writer.drain()
        except Exception:
            pass
    finally:
        writer.close()


async def main():
    manager = BrowserManager()
    await manager.start()
    print(f"[server] ブラウザ起動完了。{HOST}:{PORT} で待ち受け中...")
    print("[server] 停止するには Ctrl+C")

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, manager), HOST, PORT
    )

    try:
        async with server:
            await server.serve_forever()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        print("\n[server] 終了処理中...")
        await manager.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
