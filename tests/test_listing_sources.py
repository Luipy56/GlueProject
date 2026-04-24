from app.scraper.listing_sources import normalize_listing_strategy


def test_normalize_listing_strategy_defaults_unknown() -> None:
    assert normalize_listing_strategy("") == "static"
    assert normalize_listing_strategy(None) == "static"
    assert normalize_listing_strategy("Weird") == "static"


def test_normalize_listing_strategy_accepts_known() -> None:
    assert normalize_listing_strategy("crawl4ai") == "crawl4ai"
    assert normalize_listing_strategy("AGENT_EXPERIMENTAL") == "agent_experimental"
