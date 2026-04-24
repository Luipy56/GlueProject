import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from playwright.async_api import BrowserContext, async_playwright

from app.config import settings

_log = logging.getLogger(__name__)

# Typical desktop Chrome UA; reduces trivial headless fingerprint vs Playwright default.
_CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

_INIT_PATCH = """() => {
  try {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
  } catch (e) {}
}"""


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
            user_agent=_CHROME_UA,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            await context.add_init_script(_INIT_PATCH)
            _log.debug("Playwright persistent context ready profile=%s", profile)
            yield context
        finally:
            await context.close()
