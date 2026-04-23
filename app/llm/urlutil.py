"""Normalize LLM base URLs for OpenAI-compatible chat completions."""


def normalize_openai_compatible_base_url(base_url: str) -> str:
    """
    Ensure the base ends with /v1 so that .../chat/completions resolves correctly.

    Ollama expects http://host:11434/v1/chat/completions; users often paste
    http://host:11434 without the /v1 suffix.
    """
    u = base_url.strip().rstrip("/")
    if not u:
        return u
    lower = u.lower()
    if lower.endswith("/v1"):
        return u
    # Already a full completions path (unusual as "base")
    if lower.endswith("/chat/completions") or lower.endswith("/completions"):
        return u
    return f"{u}/v1"
