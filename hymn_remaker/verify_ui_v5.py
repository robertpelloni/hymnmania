import asyncio
from playwright.async_api import async_playwright
import os

async def verify_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 1600})

        # Increase timeout for slow streamlit loading
        try:
            await page.goto("http://localhost:8501", timeout=60000)
            # Wait for streamlit to load
            await page.wait_for_selector(".stApp", timeout=30000)

            # 1. Take screenshot of Main Studio
            # Click on "Live Psy-Mono Studio" tab
            await page.click("text=Live Psy-Mono Studio")
            await asyncio.sleep(2) # Allow tab to switch
            await page.screenshot(path="studio_v5_full.png")
            print("Captured studio_v5_full.png")

            # 2. Take screenshot of Library
            await page.click("text=Library")
            await asyncio.sleep(2)
            await page.screenshot(path="library_v5_full.png")
            print("Captured library_v5_full.png")

        except Exception as e:
            print(f"Error during verification: {e}")
            # Try to capture whatever is there
            await page.screenshot(path="error_state.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_ui())
