# main.py
# ====== Usage ======
# python3 main.py -url "https://chatgpt.com"

import argparse
import asyncio

from playwright.async_api import async_playwright


async def main(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")

        while True:
            text = input("> ").strip()

            if not text:
                continue

            if text == "exit":
                break

            await page.locator("textarea").fill(text)
            await page.locator("textarea").press("Enter")

            await page.wait_for_timeout(1000)
            print("送信しました")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", required=True)
    args = parser.parse_args()

    asyncio.run(main(args.url))
