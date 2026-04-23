"""Optional HTTP probe to debug LLM reachability from the container."""

from typing import Any

import httpx

from app.llm.urlutil import normalize_openai_compatible_base_url


async def probe_openai_compatible_models(base_url: str, *, timeout: float = 8.0) -> dict[str, Any]:
    """
    GET {base}/v1/models — supported by Ollama's OpenAI-compatible API.
    """
    root = normalize_openai_compatible_base_url(base_url.strip())
    url = root.rstrip("/") + "/models"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url)
        ok = r.status_code < 400
        return {
            "ok": ok,
            "request_url": url,
            "status_code": r.status_code,
            "detail": (r.text[:800] if not ok else "reachable"),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "request_url": url,
            "error_type": type(exc).__name__,
            "detail": str(exc),
        }
