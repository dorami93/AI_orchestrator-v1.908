# server.py
#
# ============================================================
# CLI Browser - Playwright
# ============================================================
#
# 【Setup】
# uv add playwright
# uv run playwright install chromium
#
# 【Run】
# python3 server.py -url "https://chatgpt.com"
#
# 【Usage】
# 起動後、CLIから入力するとブラウザへ送信します。
#
# > こんにちは
# 送信しました。
#
# > Pythonについて教えて
# 送信しました。
#
# 終了：
# > exit
#
# ※ ログインが必要な場合は、起動したブラウザ側でログインしてください。
#
# ============================================================


import argparse
import asyncio

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def main(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded")
            print(f"Browser ready: {url}")
            print("終了: exit\n")

            while True:
                try:
                    text = input("> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n終了します。")
                    break

                if not text:
                    continue

                if text.lower() == "exit":
                    break

                textarea = page.locator("textarea").first

                try:
                    await textarea.wait_for(state="visible", timeout=10000)
                    await textarea.fill(text)
                    await textarea.press("Enter")
                    print("送信しました。")
                except PlaywrightTimeoutError:
                    print("textareaが見つかりませんでした。")

                await page.wait_for_timeout(1000)

        finally:
            await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", required=True, help="Open URL")
    args = parser.parse_args()

    asyncio.run(main(args.url))
