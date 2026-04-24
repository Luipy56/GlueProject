import json
import logging
from typing import Any

from playwright.async_api import BrowserContext
from sqlmodel.ext.asyncio.session import AsyncSession

from app.llm.client import chat_completion_json
from app.llm.refusal import llm_raw_text_suggests_refusal
from app.llm.resolver import resolve_llm_base_url_with_report
from app.models import Portal
from app.scraper import idealista, listing_sources
from app.scraper.errors import LlmExtractionEmptyError
from app.settings_store import effective_list_extraction_system_prompt, get_all_settings

_log = logging.getLogger(__name__)

_LLM_SNIPPET_PORTAL_MAX = 2000


def _llm_snippet(raw: str, max_len: int = _LLM_SNIPPET_PORTAL_MAX) -> str:
    t = (raw or "").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _empty_extraction_message(
    *,
    portal_name: str,
    candidate_count: int,
    raw_text: str,
    bad_listings_shape: bool,
) -> str:
    refusal = llm_raw_text_suggests_refusal(raw_text)
    if bad_listings_shape:
        core = (
            f"Extracción LLM vacía («{portal_name}»): había {candidate_count} candidato(s) en HTML, "
            "pero la respuesta no contenía un array JSON «listings» válido."
        )
    else:
        core = (
            f"Extracción LLM vacía («{portal_name}»): había {candidate_count} candidato(s) en HTML, "
            "pero ninguna fila con «url» válida tras el modelo."
        )
    if refusal:
        core += (
            " La respuesta parece un rechazo a «navegar» o hacer scraping; aquí no aplica: "
            "los textos ya van en el mensaje y el modelo solo debe devolver JSON. "
            "Prueba otro modelo o ajusta el prompt de sistema en Config."
        )
    else:
        core += (
            " Revisa modelo y prompt en Config; modelos locales pequeños a veces omiten campos o devuelven JSON vacío."
        )
    return core


async def run_portal_llm_pass(
    session: AsyncSession,
    portal: Portal,
    context: BrowserContext,
    *,
    max_listings: int = 45,
) -> tuple[list[dict[str, Any]], str]:
    settings_map = await get_all_settings(session)
    base_url, res_report = await resolve_llm_base_url_with_report(session)
    if note := res_report.get("note"):
        _log.info("LLM URL: %s", note)
    api_key = settings_map.get("llm_api_key", "")
    model = settings_map.get("llm_model", "gpt-4o-mini")
    temperature = float(settings_map.get("llm_temperature", "0.2"))
    system_list = effective_list_extraction_system_prompt(settings_map)

    strategy = settings_map.get("listing_strategy", "static")
    candidates = await listing_sources.extract_listing_candidates_for_strategy(
        strategy,
        portal.search_url,
        context,
    )
    candidates = candidates[:max_listings]
    _log.info("portal=%s listing_anchor_candidates=%d (cap %d)", portal.name, len(candidates), max_listings)

    user_payload = {
        "portal": portal.name,
        "search_url": portal.search_url,
        "listings": candidates,
    }
    messages = [
        {"role": "system", "content": system_list},
        {
            "role": "user",
            "content": json.dumps(user_payload, ensure_ascii=False),
        },
    ]
    parsed, raw_llm_text = await chat_completion_json(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=temperature,
        messages=messages,
    )
    listings = parsed.get("listings")
    if not isinstance(listings, list):
        _log.warning(
            "portal=%s LLM JSON missing 'listings' array (keys=%s)",
            portal.name,
            list(parsed.keys()) if isinstance(parsed, dict) else type(parsed),
        )
        if candidates:
            raise LlmExtractionEmptyError(
                _empty_extraction_message(
                    portal_name=portal.name,
                    candidate_count=len(candidates),
                    raw_text=raw_llm_text,
                    bad_listings_shape=True,
                ),
                raw_snippet=_llm_snippet(raw_llm_text, 4000),
            )
        return [], _llm_snippet(raw_llm_text)
    normalized: list[dict[str, Any]] = []
    for row in listings:
        if not isinstance(row, dict):
            continue
        url = str(row.get("url", "")).strip()
        if not url:
            continue
        normalized.append(
            {
                "url": url,
                "title": row.get("title"),
                "price_raw": row.get("price_raw"),
                "m2": row.get("m2"),
                "seller_type": str(row.get("seller_type", "unknown")).lower(),
                "phone": row.get("phone"),
            }
        )
    if candidates and not normalized:
        _log.warning(
            "portal=%s had %d DOM candidates but 0 rows after LLM/validation",
            portal.name,
            len(candidates),
        )
        raise LlmExtractionEmptyError(
            _empty_extraction_message(
                portal_name=portal.name,
                candidate_count=len(candidates),
                raw_text=raw_llm_text,
                bad_listings_shape=False,
            ),
            raw_snippet=_llm_snippet(raw_llm_text, 4000),
        )
    _log.info("portal=%s llm_normalized_listings=%d", portal.name, len(normalized))
    return normalized, _llm_snippet(raw_llm_text)


async def enrich_with_detail_phones(
    rows: list[dict[str, Any]],
    context: BrowserContext,
    *,
    fetch_detail: bool,
) -> list[dict[str, Any]]:
    if not fetch_detail:
        return rows
    out: list[dict[str, Any]] = []
    for row in rows:
        st = row.get("seller_type", "unknown")
        url = row.get("url", "")
        phone = row.get("phone")
        if st == "private" and url and not phone:
            try:
                phone = await idealista.extract_detail_phone(url, context)
            except Exception:
                phone = None
            row = {**row, "phone": phone}
        out.append(row)
    return out
