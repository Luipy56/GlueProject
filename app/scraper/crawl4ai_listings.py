import logging
import re

from app.config import settings

_log = logging.getLogger(__name__)

# Idealista property URLs in markdown / HTML bodies
_INMUEBLE_URL_RE = re.compile(
    r"https?://(?:www\.)?idealista\.com/inmueble/\d+/?",
    re.IGNORECASE,
)


async def extract_listing_candidates(page_url: str) -> list[dict[str, str]]:
    """Crawl a listing search URL with Crawl4AI (own Chromium), then regex-gather /inmueble/ links."""
    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
    except ImportError as exc:
        raise RuntimeError(
            "Crawl4AI no está instalado (paquete `crawl4ai`). Añádelo al entorno o en Config elige estrategia «Playwright (estático)»."
        ) from exc

    timeout = max(5_000, int(settings.crawl4ai_page_timeout_ms))
    browser_config = BrowserConfig(headless=True, browser_type="chromium", locale="es-ES")
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=timeout,
        wait_until="domcontentloaded",
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=page_url, config=crawler_config)

    combined = "\n".join(
        x
        for x in (
            getattr(result, "markdown", None) or "",
            getattr(result, "html", None) or "",
            getattr(result, "cleaned_html", None) or "",
        )
        if x
    )
    urls = _INMUEBLE_URL_RE.findall(combined)
    seen: set[str] = set()
    ordered: list[str] = []
    for u in urls:
        u2 = u.split("#", 1)[0].rstrip("/") + "/"
        if u2 not in seen:
            seen.add(u2)
            ordered.append(u2)

    items: list[dict[str, str]] = []
    for href in ordered:
        snippet = ""
        for line in combined.splitlines():
            if href.rstrip("/") in line.replace("https://www.idealista.com", "https://idealista.com"):
                snippet = line.strip()[:1200]
                break
        if not snippet:
            snippet = (combined[:400] + "…") if len(combined) > 400 else combined
        items.append({"url": href, "snippet": snippet})

    if not items:
        _log.warning("Crawl4AI: no /inmueble/ links in markdown/html for %s", page_url)
    else:
        _log.info("Crawl4AI: %d listing URL(s) from %s", len(items), page_url)
    return items
