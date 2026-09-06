import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:5000/?error=Acc%C3%A8s+refus%C3%A9")
        await page.screenshot(path="auth_verification.png", full_page=True)
        await browser.close()

asyncio.run(run())
