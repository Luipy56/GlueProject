"""Heuristics on raw LLM text (chat message body) — not the user's curl /generate prompt."""

# Substrings often seen when a model refuses "live browsing" or "scraping" even though
# our pipeline only sends pre-fetched snippets (no live navigation).
_REFUSAL_NEEDLES = (
    "no tengo la capacidad de navegar",
    "no tengo la capacidad de acceder",
    "no puedo navegar",
    "no puedo acceder a sitios web",
    "no puedo acceder a internet",
    "no tengo acceso a internet en tiempo real",
    "no tengo acceso a la web en tiempo real",
    "navegar en tiempo real",
    "sitios web externos",
    "web scraping",
    "funciones de web scraping",
    "cannot browse the internet",
    "can't browse the internet",
    "cannot browse websites",
    "cannot access the internet",
    "do not have the ability to browse",
    "don't have the ability to browse",
    "i cannot browse",
    "i can't browse",
    "unable to browse",
    "unable to access external websites",
    "i do not have live web access",
    "i don't have live web access",
)


def llm_raw_text_suggests_refusal(raw_text: str) -> bool:
    if not raw_text or not raw_text.strip():
        return False
    t = raw_text.lower()
    return any(n in t for n in _REFUSAL_NEEDLES)
