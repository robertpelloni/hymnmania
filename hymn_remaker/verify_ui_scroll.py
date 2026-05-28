import asyncio
from playwright.async_api import async_playwright
import os

async def verify_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 2400}) # Taller viewport

        try:
            await page.goto("http://localhost:8501", timeout=60000)
            await page.wait_for_selector(".stApp", timeout=30000)

            await page.click("text=Live Psy-Mono Studio")
            await asyncio.sleep(2)

            # Click the expander for Novel AI if it exists
            expanders = await page.query_selector_all(".stExpander")
            for exp in expanders:
                text = await exp.inner_text()
                if "Novel AI Generation" in text:
                    await exp.click()
                    await asyncio.sleep(1)

            await page.screenshot(path="studio_v5_scrolled.png")
            print("Captured studio_v5_scrolled.png")

        except Exception as e:
            print(f"Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_ui())
