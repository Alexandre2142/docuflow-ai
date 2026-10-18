"""Environment-backed configuration. The default mode makes no external calls."""
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    llm_provider: str = "mock"
    max_document_chars: int = 50_000

    @classmethod
    def from_env(cls) -> "Settings":
        provider = os.getenv("DOCUFLOW_LLM_PROVIDER", "mock").strip().lower()
        if provider != "mock":
            raise ValueError(
                "This MVP only supports DOCUFLOW_LLM_PROVIDER=mock. "
                "External providers are intentionally not implemented."
            )
        try:
            max_chars = int(os.getenv("DOCUFLOW_MAX_DOCUMENT_CHARS", "50000"))
        except ValueError as exc:
            raise ValueError("DOCUFLOW_MAX_DOCUMENT_CHARS must be an integer.") from exc
        if max_chars < 1:
            raise ValueError("DOCUFLOW_MAX_DOCUMENT_CHARS must be positive.")
        return cls(llm_provider=provider, max_document_chars=max_chars)

settings = Settings.from_env()
