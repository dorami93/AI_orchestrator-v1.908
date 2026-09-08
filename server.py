# server.py
#
# ============================================================
# Setup: uv add playwright
#        uv run playwright install chromium
#
# Run:   python3 server.py -url "https://chatgpt.com"
#
# Exit:  > exit
# ============================================================

import argparse
import asyncio

from playwright.async_api import async_playwright


async def main(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded")
            textarea = page.locator("textarea").first

            while True:
                text = input("> ").strip()

                if text.lower() == "exit":
                    break
                if not text:
                    continue

                await textarea.fill(text)
                await textarea.press("Enter")

                await page.wait_for_timeout(1000)
                print("送信しました。")

        finally:
            await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", required=True)
    args = parser.parse_args()

    asyncio.run(main(args.url))
