"""
Resolución automática de la URL base del LLM para que funcione en local, Docker
(Linux/Mac), túnel en 127.0.0.1, Ollama en LAN, APIs cloud, etc.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import llm_base_url_from_env
from app.llm.diagnostics import probe_openai_compatible_models
from app.settings_store import get_all_settings

_CACHE_TTL_SEC = 600.0
_cache: dict[str, Any] = {}


def clear_llm_resolver_cache() -> None:
    _cache.clear()


def _running_in_container() -> bool:
    return Path("/.dockerenv").exists() or os.environ.get("container") == "oci"


def _should_expand_hosts(primary: str, provider: str) -> bool:
    """Solo añadir fallbacks (docker/localhost) cuando tiene sentido; no tocar APIs cloud ni Ollama en LAN."""
    if _is_managed_cloud_api(primary):
        return False
    try:
        _, host, port = _parse_local_endpoint(primary)
    except Exception:
        return False
    if (provider or "").lower() == "ollama" and host in (
        "127.0.0.1",
        "localhost",
        "0.0.0.0",
    ):
        return True
    if host in ("127.0.0.1", "localhost", "0.0.0.0", "host.docker.internal", "172.17.0.1"):
        return True
    if port == 11434 and host in ("127.0.0.1", "localhost", "0.0.0.0"):
        return True
    return False


def _is_managed_cloud_api(url: str) -> bool:
    """HTTPS hacia un host remoto típico de API gestionada: no aplicar fallbacks locales."""
    try:
        p = urlparse(url.strip())
    except Exception:
        return False
    h = (p.hostname or "").lower()
    if not h:
        return False
    if p.scheme != "https":
        return False
    if h in ("localhost", "127.0.0.1", "host.docker.internal", "172.17.0.1", "0.0.0.0"):
        return False
    if h.endswith(
        (
            "openai.com",
            "azure.com",
            "anthropic.com",
            "groq.com",
            "together.xyz",
            "fireworks.ai",
            "mistral.ai",
            "cohere.com",
            "deepinfra.com",
        )
    ):
        return True
    # Cualquier otro HTTPS remoto: una sola URL (evita tocar 11434 por error)
    return True


def _parse_local_endpoint(url: str) -> tuple[str, str, int | None]:
    """scheme, host, port (Ollama por defecto 11434 en http hacia loopback)."""
    p = urlparse(url.strip())
    scheme = p.scheme or "http"
    host = (p.hostname or "127.0.0.1").lower()
    port = p.port
    if port is None and scheme == "http" and host in (
        "127.0.0.1",
        "localhost",
        "host.docker.internal",
        "172.17.0.1",
        "0.0.0.0",
    ):
        port = 11434
    return scheme, host.lower(), port


def _build_url(scheme: str, host: str, port: int | None) -> str:
    netloc = f"{host}:{port}" if port is not None else host
    return urlunparse((scheme, netloc, "", "", "", ""))


def _expand_candidates(primary: str, provider: str) -> list[str]:
    primary = primary.strip()
    if not primary:
        primary = "https://api.openai.com/v1"
    if _is_managed_cloud_api(primary):
        return [primary]
    if not _should_expand_hosts(primary, provider):
        return [primary]

    in_c = _running_in_container()
    scheme, host, port = _parse_local_endpoint(primary)

    hosts: list[str] = []
    for h in (host,):
        if h and h not in hosts:
            hosts.append(h)

    if in_c:
        if host in ("127.0.0.1", "localhost", "0.0.0.0"):
            for h in ("host.docker.internal", "172.17.0.1"):
                if h not in hosts:
                    hosts.append(h)
        if "127.0.0.1" not in hosts:
            hosts.append("127.0.0.1")
    else:
        if host == "127.0.0.1" and "localhost" not in hosts:
            hosts.append("localhost")
        elif host == "localhost" and "127.0.0.1" not in hosts:
            hosts.append("127.0.0.1")

    out: list[str] = []
    for h in hosts:
        u = _build_url(scheme, h, port)
        if u not in out:
            out.append(u)
    return out


async def resolve_llm_base_url_with_report(
    session: AsyncSession,
    *,
    probe_timeout: float = 3.0,
) -> tuple[str, dict[str, Any]]:
    """
    Devuelve (base_url_ganadora, informe) probando candidatos hasta el primer GET /v1/models OK.
    """
    settings = await get_all_settings(session)
    provider = (settings.get("llm_provider") or "").strip()
    primary = (
        llm_base_url_from_env()
        or (settings.get("llm_base_url") or "").strip()
        or "https://api.openai.com/v1"
    )

    cache_key = f"{primary}|{provider}|{int(_running_in_container())}"
    now = time.monotonic()
    if (
        _cache.get("key") == cache_key
        and isinstance(_cache.get("t"), (int, float))
        and now - float(_cache["t"]) < _CACHE_TTL_SEC
        and isinstance(_cache.get("url"), str)
    ):
        rep = dict(_cache.get("report") or {})
        rep["from_cache"] = True
        return str(_cache["url"]), rep

    candidates = _expand_candidates(primary, provider)
    report: dict[str, Any] = {
        "configured_primary": primary,
        "in_container": _running_in_container(),
        "candidates": [],
        "winner": None,
    }

    last_detail = ""
    for cand in candidates:
        pr = await probe_openai_compatible_models(cand, timeout=probe_timeout)
        report["candidates"].append({"tried": cand, **pr})
        if pr.get("ok"):
            report["winner"] = cand
            if cand.strip() != primary.strip():
                report["note"] = (
                    f"Se usó automáticamente {cand!r} (la URL configurada {primary!r} no respondió desde este entorno)."
                )
            _cache.clear()
            _cache.update(key=cache_key, url=cand, report=dict(report), t=now)
            return cand, report
        last_detail = str(pr.get("detail") or pr.get("error_type") or "")

    msg = (
        f"No se pudo conectar al LLM. Probado: {candidates!r}. Último error: {last_detail!s}. "
        "Si usas Ollama en el host con Docker, expón el puerto en 0.0.0.0 o usa "
        "`docker compose -f docker-compose.host.yml up` (ver README)."
    )
    raise httpx.ConnectError(msg)


async def resolve_llm_base_url(session: AsyncSession) -> str:
    url, _ = await resolve_llm_base_url_with_report(session)
    return url
