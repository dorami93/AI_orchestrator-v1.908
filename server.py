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
        browser = await p.chromium.launch(headless=False, args=[
            "--window-position=-10000,-10000",
            "--window-size=400,300",
        ])
        page = await browser.new_page(viewport={"width": 400, "height": 300})

        async def block_resources(route):
            if route.request.resource_type in {"image", "font", "media"}:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", block_resources)

        try:
            await page.goto(url, wait_until="domcontentloaded")
            textarea = page.locator("textarea").first
            print(f"Browser ready: {url}")
            print("終了: exit\n")

            while True:
                text = input("> ").strip()
                if not text:
                    continue
                if text.lower() == "exit":
                    break

                try:
                    await textarea.wait_for(state="visible", timeout=10000)
                    await textarea.fill(text)
                    await textarea.press("Enter")

                    await page.get_by_text("回答が完了しました", exact=True).wait_for(
                        state="visible",
                        timeout=120000,
                    )

                    body = await page.locator("body").inner_text()
                    start = body.rfind("ChatGPT:")
                    end = body.find("ChatGPT は AI", start)

                    if start != -1:
                        answer = body[start + len("ChatGPT:"):end].strip()
                        print(f"\n{answer}\n")

                except PlaywrightTimeoutError:
                    print("回答の取得がタイムアウトしました。")

        finally:
            await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.url))
