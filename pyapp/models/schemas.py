from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TranslationResponse(BaseModel):
    original_text: str = Field(..., description="The original input text (Chinese or English).")
    translated_text: str = Field(..., description="The translated or corrected English text.")
    english_grammar: Optional[str] = Field(None, description="Grammar explanation for the English text.")
    japanese_text: Optional[str] = Field(None, description="Japanese translation.")
    hiragana_pronunciation: Optional[str] = Field(None, description="Hiragana pronunciation for the Japanese text.")
    japanese_grammar: Optional[str] = Field(None, description="Grammar explanation for the Japanese translation.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the translation was generated.")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to process.")
    include_grammar: bool = Field(False, description="Whether to include grammar explanations.")
