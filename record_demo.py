import asyncio
import os
import time
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser with video recording enabled
        video_dir = "/config/Desktop/BuildWithGemini/visual-assist/demo_raw"
        os.makedirs(video_dir, exist_ok=True)
        
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()
        
        print("Navigating to http://localhost:8080...")
        await page.goto("http://localhost:8080")
        await page.wait_for_timeout(2000)
        
        # 1. First prompt: What the app does best (Pantry item lookup & tactile markers)
        prompt_1 = "Show my pantry inventory and where items are stored"
        print("Typing prompt 1:", prompt_1)
        await page.fill("#input", prompt_1)
        await page.wait_for_timeout(1000)
        await page.click("button[type='submit']")
        
        # Wait for agent response to appear
        print("Waiting for prompt 1 response...")
        await page.wait_for_timeout(10000)
        
        # 2. Second prompt: Richer tool call / database lookup / visual aid generation
        prompt_2 = "What is my medication schedule and tactile cues for Lisinopril?"
        print("Typing prompt 2:", prompt_2)
        await page.fill("#input", prompt_2)
        await page.wait_for_timeout(1000)
        await page.click("button[type='submit']")
        
        # Wait for agent response
        print("Waiting for prompt 2 response...")
        await page.wait_for_timeout(12000)
        
        # 3. Third prompt: Show off generated visual cue card image
        prompt_3 = "Generate a visual aid card image for my Lisinopril medication"
        print("Typing prompt 3:", prompt_3)
        await page.fill("#input", prompt_3)
        await page.wait_for_timeout(1000)
        await page.click("button[type='submit']")
        
        print("Waiting for prompt 3 response and card rendering...")
        await page.wait_for_timeout(15000)
        
        await page.wait_for_timeout(3000)
        await context.close()
        await browser.close()
        print("Browser recording closed.")

asyncio.run(run())
