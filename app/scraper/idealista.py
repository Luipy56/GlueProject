import logging
import re

from playwright.async_api import BrowserContext, Page

_log = logging.getLogger(__name__)

LISTING_ANCHOR_SELECTOR = 'a[href*="/inmueble/"]'

_CONSENT_SELECTORS = (
    "#didomi-notice-agree-button",
    "button#didomi-notice-agree-button",
    ".didomi-continue-without-agreeing",
    "#onetrust-accept-btn-handler",
    "button[data-testid='TcfAccept']",
)

_EXTRACT_JS = """() => {
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


async def _try_dismiss_consent(page: Page) -> bool:
    """Best-effort CMP / cookie banners (Didomi, OneTrust, generic)."""
    clicked = False
    for sel in _CONSENT_SELECTORS:
        try:
            loc = page.locator(sel).first
            if await loc.count() == 0:
                continue
            await loc.click(timeout=2500)
            clicked = True
            await page.wait_for_timeout(600)
        except Exception:
            continue
    for pattern in (
        r"Aceptar y cerrar",
        r"Aceptar todas",
        r"Aceptar todo",
        r"^Aceptar$",
        r"Accept all",
        r"Consentir",
    ):
        try:
            btn = page.get_by_role("button", name=re.compile(pattern, re.I))
            if await btn.count() == 0:
                continue
            await btn.first.click(timeout=2500)
            clicked = True
            await page.wait_for_timeout(600)
            break
        except Exception:
            continue
    return clicked


async def _scroll_listing_page(page: Page, rounds: int = 10) -> None:
    for _ in range(rounds):
        await page.evaluate(
            "() => { window.scrollBy(0, Math.floor(window.innerHeight * 0.92)); }"
        )
        await page.wait_for_timeout(450)


async def extract_listing_candidates(page_url: str, context: BrowserContext) -> list[dict[str, str]]:
    page = await context.new_page()
    try:
        await page.goto(page_url, wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(1200)
        await _try_dismiss_consent(page)

        try:
            await page.wait_for_selector(LISTING_ANCHOR_SELECTOR, timeout=50_000)
        except Exception:
            _log.warning(
                "Idealista: no anchors %s after first wait; will scroll / retry consent",
                LISTING_ANCHOR_SELECTOR,
            )

        await _try_dismiss_consent(page)
        await _scroll_listing_page(page)
        await _try_dismiss_consent(page)

        try:
            await page.wait_for_selector(LISTING_ANCHOR_SELECTOR, timeout=20_000)
        except Exception:
            _log.warning("Idealista: still no %s after scroll", LISTING_ANCHOR_SELECTOR)

        items: list[dict[str, str]] = await page.evaluate(_EXTRACT_JS)
        if not items:
            _log.warning(
                "Idealista: 0 listing candidates from %s (bot-wall, consent, or DOM change)",
                page_url,
            )
        else:
            _log.info("Idealista: extracted %d raw listing anchor(s)", len(items))
        return items
    finally:
        await page.close()


_PHONE_RE = re.compile(r"(?:\+34|0034)?[\s-]?(?:6|7)\d{8}")


async def extract_detail_phone(detail_url: str, context: BrowserContext) -> str | None:
    page = await context.new_page()
    try:
        await page.goto(detail_url, wait_until="domcontentloaded", timeout=90_000)
        await page.wait_for_timeout(1200)
        await _try_dismiss_consent(page)
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
