from typing import Optional, Type

from openai import OpenAI
from pydantic import BaseModel

from pyapp.settings import get_settings

_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Return a singleton OpenAI client configured from settings."""
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set in environment or .env file.")
        _client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            http_client=None,
        )
    return _client


def run_structured_chat(prompt: str, response_model: Type[BaseModel]) -> BaseModel:
    """Call OpenAI chat completion API and parse into the given Pydantic model."""
    settings = get_settings()
    client = get_openai_client()
    completion = client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "Translate the given text and explain the grammar"},
            {"role": "user", "content": prompt},
        ],
        response_format=response_model,
    )
    return completion.choices[0].message.parsed
