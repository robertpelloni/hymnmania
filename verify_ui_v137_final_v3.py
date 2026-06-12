import time
import os
import subprocess
from playwright.sync_api import sync_playwright

def main():
    print("Starting Streamlit...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    proc = subprocess.Popen(["streamlit", "run", "hymn_remaker/app.py", "--server.port", "8522"], env=env)
    time.sleep(30)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 1000})
            page.goto("http://localhost:8522", timeout=60000)

            # Wait for content
            print("Waiting for main title...")
            page.wait_for_selector("text=Hymn Remaker Pipeline", timeout=60000)

            # Navigate to Tab 5
            print("Clicking Tab 5...")
            page.click("text=Optimization & Analytics")
            time.sleep(2)

            # Look for button
            print("Waiting for Health Audit button...")
            page.wait_for_selector("text=Run Health Audit", timeout=30000)

            page.screenshot(path="v137_final_ui_verify.png")
            print("Screenshot taken: v137_final_ui_verify.png")
            browser.close()
    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        proc.terminate()

if __name__ == "__main__":
    main()
