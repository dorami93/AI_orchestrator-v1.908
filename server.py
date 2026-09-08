# server.py
#
# ============================================================
# Setup:
#   uv add playwright
#   uv run playwright install chromium
#
# Run:
#   python3 server.py -url "https://chatgpt.com"
#
# Exit:
#   > exit
# ============================================================

import argparse
import asyncio

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


async def main(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            channel="chromium",
        )
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded")

            print(f"Browser ready: {url}")
            print("終了: exit\n")

            while True:
                text = input("> ").strip()

                if not text:
                    continue

                if text.lower() == "exit":
                    break

                textarea = page.locator("textarea").first

                print("count:", await page.locator("textarea").count())
                print("visible:", await textarea.is_visible())
                print("enabled:", await textarea.is_enabled())

                try:
                    await textarea.wait_for(
                        state="visible",
                        timeout=10000,
                    )

                    await textarea.fill(text)
                    await textarea.press("Enter")

                    print("送信しました。")

                except PlaywrightTimeoutError:
                    print("textareaが見つかりませんでした。")

        finally:
            await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", required=True)
    args = parser.parse_args()

    asyncio.run(main(args.url))
