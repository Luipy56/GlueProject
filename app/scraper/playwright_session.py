from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import BrowserContext, async_playwright

from app.config import settings


@asynccontextmanager
async def persistent_browser_context() -> AsyncIterator[BrowserContext]:
    """
    Persistent Chromium profile under DATA_DIR for cookie/session continuity.
    """
    profile = settings.data_dir / "pw_profile"
    profile.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            str(profile),
            headless=True,
            viewport={"width": 1280, "height": 900},
            locale="es-ES",
        )
        try:
            yield context
        finally:
            await context.close()
