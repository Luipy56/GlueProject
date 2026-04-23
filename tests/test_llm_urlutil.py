from app.llm.urlutil import normalize_openai_compatible_base_url


def test_ollama_host_gets_v1_suffix() -> None:
    assert normalize_openai_compatible_base_url("http://127.0.0.1:11434") == "http://127.0.0.1:11434/v1"


def test_preserves_existing_v1() -> None:
    assert normalize_openai_compatible_base_url("http://host:11434/v1") == "http://host:11434/v1"


def test_openai_default() -> None:
    assert normalize_openai_compatible_base_url("https://api.openai.com/v1") == "https://api.openai.com/v1"


def test_openai_missing_v1() -> None:
    assert normalize_openai_compatible_base_url("https://api.openai.com") == "https://api.openai.com/v1"
