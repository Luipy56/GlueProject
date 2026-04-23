import re
from typing import Any

from playwright.async_api import BrowserContext


async def extract_listing_candidates(page_url: str, context: BrowserContext) -> list[dict[str, str]]:
    page = await context.new_page()
    try:
        await page.goto(page_url, wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(1500)
        items: list[dict[str, str]] = await page.evaluate(
            """() => {
              const out = [];
              const seen = new Set();
              const anchors = Array.from(document.querySelectorAll('a[href*="/inmueble/"]'));
              for (const a of anchors) {
                let href = a.href || "";
                href = href.split('#')[0];
                if (!href.includes('/inmueble/')) continue;
                if (seen.has(href)) continue;
                seen.add(href);
                let card = a.closest('article');
                if (!card) card = a.parentElement;
                let text = '';
                if (card) text = (card.innerText || '').slice(0, 1200);
                else text = (a.innerText || '').slice(0, 400);
                text = text.replace(/\\s+/g, ' ').trim();
                out.push({ url: href, snippet: text });
              }
              return out;
            }"""
        )
        return items
    finally:
        await page.close()


_PHONE_RE = re.compile(r"(?:\+34|0034)?[\s-]?(?:6|7)\d{8}")


async def extract_detail_phone(detail_url: str, context: BrowserContext) -> str | None:
    page = await context.new_page()
    try:
        await page.goto(detail_url, wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(1200)
        # Try tel: links
        hrefs: list[str] = await page.eval_on_selector_all(
            'a[href^="tel:"]', "els => els.map(e => e.getAttribute('href'))"
        )
        for h in hrefs:
            if h and h.lower().startswith("tel:"):
                return h.split(":", 1)[1].strip()
        text: str = await page.inner_text("body")
        m = _PHONE_RE.search(text.replace(" ", ""))
        if m:
            return m.group(0)
        return None
    finally:
        await page.close()
