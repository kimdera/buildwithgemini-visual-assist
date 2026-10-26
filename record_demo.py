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
        
        # Wait until agent 1 response arrives and finishes typing
        print("Waiting for prompt 1 response...")
        await page.locator(".msg-wrapper.agent").nth(0).locator(".bubble:not(:has(.typing-indicator))").wait_for(timeout=60000)
        await page.wait_for_timeout(6000) # Ample time for viewer to read pantry card
        
        # 2. Second prompt: Medication Schedule & Tactile Identifiers (exercises FDA tool + Memory + Structured Table/Text)
        prompt_2 = "What is my medication schedule and tactile cues for Lisinopril?"
        print("Typing prompt 2:", prompt_2)
        await page.fill("#input", prompt_2)
        await page.wait_for_timeout(800)
        await page.click("button[type='submit']")
        
        print("Waiting for prompt 2 response...")
        # Wait until agent 2 response arrives and finishes typing
        await page.locator(".msg-wrapper.agent").nth(1).locator(".bubble:not(:has(.typing-indicator))").wait_for(timeout=60000)
        await page.wait_for_timeout(8000) # Give viewer plenty of time to read the schedule and tactile cues!
        
        # 3. Third prompt: Visual Aid Card Image Generation (exercises Imagen 3.0 tool + Cloud Storage upload + Card Image embed)
        prompt_3 = "Generate a visual aid card image for my Lisinopril medication"
        print("Typing prompt 3:", prompt_3)
        await page.fill("#input", prompt_3)
        await page.wait_for_timeout(800)
        await page.click("button[type='submit']")
        
        print("Waiting for prompt 3 visual aid image and card...")
        # Wait until agent 3 response arrives (typing indicator is detached/removed)
        agent_3_bubble = page.locator(".msg-wrapper.agent").nth(2).locator(".bubble")
        await agent_3_bubble.locator(".typing-indicator").wait_for(state="detached", timeout=90000)
        
        # Wait for the visual aid image to be rendered and visible
        print("Waiting for image to become visible...")
        img_locator = agent_3_bubble.locator("img.a2img")
        await img_locator.wait_for(state="visible", timeout=30000)
        
        # Smoothly scroll the card into full center view so all details & image are prominent
        print("Scrolling card into full view...")
        await page.evaluate("const el = document.getElementById('log'); if (el) el.scrollTop = el.scrollHeight;")
        await page.wait_for_timeout(1000)
        await agent_3_bubble.scroll_into_view_if_needed()
        await page.wait_for_timeout(12000) # Give viewer plenty of time to view the entire generated image and card details!
        
        print("Closing browser recording...")
        await context.close()
        await browser.close()
        print("Browser recording closed cleanly.")

asyncio.run(run())
