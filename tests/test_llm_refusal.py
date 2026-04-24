from app.llm.refusal import llm_raw_text_suggests_refusal


def test_refusal_detects_spanish_browsing_refusal() -> None:
    raw = "Como modelo de lenguaje, no tengo la capacidad de navegar en sitios web externos"
    assert llm_raw_text_suggests_refusal(raw) is True


def test_refusal_detects_english() -> None:
    assert llm_raw_text_suggests_refusal("I cannot browse the internet for you.") is True


def test_refusal_negative_on_json_like() -> None:
    body = '{"listings":[{"url":"https://x.com/inmueble/1/","title":"A"}]}'
    assert llm_raw_text_suggests_refusal(body) is False


def test_refusal_empty() -> None:
    assert llm_raw_text_suggests_refusal("") is False
