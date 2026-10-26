import asyncio
import os
import time
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
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
        await page.wait_for_timeout(2500)
        
        # 1. First prompt: Pantry Inventory & physical placement (exercises Firestore & A2UI card)
        prompt_1 = "Show my pantry inventory and where items are stored"
        print("Typing prompt 1:", prompt_1)
        await page.fill("#input", prompt_1)
        await page.wait_for_timeout(800)
        await page.click("button[type='submit']")
        
        # Wait until typing indicator disappears and A2UI card is rendered
        print("Waiting for prompt 1 response...")
        await page.wait_for_selector(".msg-wrapper.agent .a2card", timeout=45000)
        await page.wait_for_timeout(5000) # Let viewer appreciate the rich card
        
        # 2. Second prompt: Medication Schedule & Tactile Identifiers (exercises FDA tool + Memory + Structured Table/Text)
        prompt_2 = "What is my medication schedule and tactile cues for Lisinopril?"
        print("Typing prompt 2:", prompt_2)
        await page.fill("#input", prompt_2)
        await page.wait_for_timeout(800)
        await page.click("button[type='submit']")
        
        print("Waiting for prompt 2 response...")
        # Wait until second agent message is no longer typing
        await page.wait_for_selector(".msg-wrapper.agent:nth-of-type(2) .bubble:not(:has(.typing-indicator))", timeout=45000)
        await page.wait_for_timeout(5000)
        
        # 3. Third prompt: Visual Aid Card Image Generation (exercises Imagen 3.0 tool + Cloud Storage upload + Card Image embed)
        prompt_3 = "Generate a visual aid card image for my Lisinopril medication"
        print("Typing prompt 3:", prompt_3)
        await page.fill("#input", prompt_3)
        await page.wait_for_timeout(800)
        await page.click("button[type='submit']")
        
        print("Waiting for prompt 3 visual aid image and card...")
        # Wait until prompt 3 response arrives (typing indicator is replaced by content)
        await page.wait_for_selector(".msg-wrapper.agent:nth-of-type(3) .bubble:not(:has(.typing-indicator))", timeout=90000)
        await page.wait_for_timeout(7000) # Give plenty of time to view the generated image and details
        
        print("Closing browser recording...")
        await context.close()
        await browser.close()
        print("Browser recording closed.")

asyncio.run(run())
