from datetime import datetime, timezone
from typing import Optional

from pyapp.clients.openai_client import run_structured_chat
from pyapp.db import init_repository
from pyapp.models.schemas import TranslationResponse
from pyapp.repositories.sqlite_repo import TranslationRepository
from pyapp.settings import get_settings


class TranslatorService:
    """Business logic for translating and grammar-checking text."""

    def __init__(self, repository: TranslationRepository, model_name: Optional[str] = None):
        self.repository = repository
        self.model_name = model_name or get_settings().openai_model

    def translate_chinese(self, text: str, include_grammar: bool = False) -> TranslationResponse:
        prompt = self._build_chinese_prompt(text, include_grammar)
        ai_result = run_structured_chat(prompt, TranslationResponse)
        result = self._with_timestamp(ai_result)
        self.repository.save(result)
        return result

    def correct_english(self, text: str, include_grammar: bool = False) -> TranslationResponse:
        prompt = self._build_english_prompt(text, include_grammar)
        ai_result = run_structured_chat(prompt, TranslationResponse)
        result = self._with_timestamp(ai_result)
        self.repository.save(result)
        return result

    @staticmethod
    def _with_timestamp(result: TranslationResponse) -> TranslationResponse:
        """Stamp result with current UTC timestamp (ignore model-provided timestamps)."""
        return TranslationResponse(
            **result.model_dump(exclude={"timestamp"}),
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def _build_chinese_prompt(text: str, include_grammar: bool) -> str:
        grammar_clause = (
            "Provide English and Japanese grammar explanations."
            if include_grammar
            else "Skip grammar explanations unless they are critical."
        )
        return (
            f"Translate the following Chinese text to English and Japanese:\n{text}\n"
            f"Also provide Hiragana for the Japanese translation. {grammar_clause}"
        )

    @staticmethod
    def _build_english_prompt(text: str, include_grammar: bool) -> str:
        grammar_clause = (
            "Provide English and Japanese grammar explanations."
            if include_grammar
            else "Skip grammar explanations unless they are critical."
        )
        return (
            "Correct the grammar of the following English sentence and provide an explanation.\n"
            f"Original English: {text}\n"
            f"Also provide a Japanese translation and Hiragana pronunciation. {grammar_clause}"
        )


def get_service() -> TranslatorService:
    """Create a service with default dependencies."""
    repo = init_repository()
    return TranslatorService(repository=repo)
