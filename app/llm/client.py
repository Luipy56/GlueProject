import json
import re
from typing import Any

import httpx

from app.llm.urlutil import normalize_openai_compatible_base_url


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        return json.loads(m.group(0))
    raise ValueError("Model did not return valid JSON")


async def chat_completion_json(
    *,
    base_url: str,
    api_key: str,
    model: str,
    temperature: float,
    messages: list[dict[str, str]],
) -> tuple[dict[str, Any], str]:
    """OpenAI-compatible chat completions.

    Returns ``(parsed_json_object, raw_message_text)`` where *raw_message_text* is the
    assistant message body before JSON extraction (for diagnostics / refusal heuristics).
    """
    root = normalize_openai_compatible_base_url(base_url)
    url = root.rstrip("/") + "/chat/completions"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    # Many OpenAI-compatible servers support json mode; Ollama may not.
    payload_json_mode = {**payload, "response_format": {"type": "json_object"}}

    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, headers=headers, json=payload_json_mode)
        if r.status_code == 400 and "response_format" in r.text.lower():
            r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    content = data["choices"][0]["message"]["content"]
    if isinstance(content, list):
        # Rare multimodal shape
        text = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    else:
        text = str(content)
    return _extract_json_object(text), text
