class LlmExtractionEmptyError(RuntimeError):
    """HTML yielded listing candidates but the LLM produced no valid normalized rows."""

    def __init__(self, message: str, *, raw_snippet: str = "") -> None:
        super().__init__(message)
        self.raw_snippet = raw_snippet
