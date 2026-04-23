import pytest


@pytest.mark.parametrize(
    ("primary", "provider", "in_container", "must_contain"),
    [
        ("https://api.openai.com/v1", "openai_compatible", True, ["https://api.openai.com/v1"]),
        ("http://127.0.0.1:11434", "openai_compatible", True, ["host.docker.internal:11434"]),
        ("http://127.0.0.1:11434", "openai_compatible", False, ["localhost:11434"]),
    ],
)
def test_expand_candidates_order(
    primary: str,
    provider: str,
    in_container: bool,
    must_contain: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.llm import resolver as r

    monkeypatch.setattr(r, "_running_in_container", lambda: in_container)
    from app.llm.resolver import _expand_candidates

    cands = _expand_candidates(primary, provider)
    joined = " ".join(cands)
    for frag in must_contain:
        assert frag in joined


def test_lan_ollama_not_polluted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.llm.resolver._running_in_container", lambda: True)
    from app.llm.resolver import _expand_candidates

    c = _expand_candidates("http://192.168.88.10:11434", "ollama")
    assert c == ["http://192.168.88.10:11434"]
