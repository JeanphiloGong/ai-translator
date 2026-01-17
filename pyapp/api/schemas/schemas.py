from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TranslationResponse(BaseModel):
    original_text: str = Field(..., description="The original input text (Chinese or English).")
    translated_text: str = Field(..., description="The translated or corrected English text.")
    english_grammar: Optional[str] = Field(None, description="Grammar explanation for the English text.")
    japanese_text: Optional[str] = Field(None, description="Japanese translation.")
    hiragana_pronunciation: Optional[str] = Field(None, description="Hiragana pronunciation for the Japanese text.")
    japanese_grammar: Optional[str] = Field(None, description="Grammar explanation for the Japanese translation.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the translation was generated.")


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to process.")
    include_grammar: bool = Field(False, description="Whether to include grammar explanations.")


class TaskInput(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to process.")
    mode: Literal["translate-zh", "correct-en"] = Field(..., description="Task mode.")
    include_grammar: bool = Field(False, description="Whether to include grammar explanations.")


class TaskPrepareResponse(BaseModel):
    input_hash: str = Field(..., description="Keccak256 hash of the canonical input payload.")
    input_ref: str = Field(..., description="Opaque reference to the prepared input.")
    prepared_at: str = Field(..., description="RFC3339 UTC timestamp for the prepared input.")
    deduped: bool = Field(..., description="True if the input already existed.")


class TaskClaimRequest(BaseModel):
    task_id: int = Field(..., description="On-chain task id.")
    input_hash: str = Field(..., description="Prepared input hash.")
    requester: Optional[str] = Field(None, description="On-chain requester address.")
    model: Optional[str] = Field(None, description="Requested model or mode.")
    fee: Optional[str] = Field(None, description="Fee paid on-chain.")
    chain_id: Optional[int] = Field(None, description="Chain id for the task.")
    tx_hash: Optional[str] = Field(None, description="Transaction hash.")
    block_number: Optional[int] = Field(None, description="Block number.")


class TaskClaimResponse(BaseModel):
    task_id: int = Field(..., description="On-chain task id.")
    status: str = Field(..., description="Task status.")
    updated_at: str = Field(..., description="RFC3339 UTC timestamp for the update.")


class TaskInputResponse(BaseModel):
    input_hash: str = Field(..., description="Prepared input hash.")
    input_payload: TaskInput
    prepared_at: str = Field(..., description="RFC3339 UTC timestamp for the prepared input.")


class TaskResultPayload(BaseModel):
    original_text: str = Field(..., description="The original input text.")
    translated_text: str = Field(..., description="The translated or corrected English text.")
    english_grammar: Optional[str] = Field(None, description="Grammar explanation for the English text.")
    japanese_text: Optional[str] = Field(None, description="Japanese translation.")
    hiragana_pronunciation: Optional[str] = Field(None, description="Hiragana pronunciation for the Japanese text.")
    japanese_grammar: Optional[str] = Field(None, description="Grammar explanation for the Japanese translation.")
    timestamp: str = Field(..., description="RFC3339 UTC timestamp without fractional seconds.")


class TaskResultRequest(BaseModel):
    result_payload: TaskResultPayload
    result_hash: Optional[str] = Field(None, description="Optional result hash for verification.")


class TaskResultResponse(BaseModel):
    task_id: int = Field(..., description="On-chain task id.")
    result_hash: str = Field(..., description="Keccak256 hash of the canonical result payload.")
    status: str = Field(..., description="Task status.")
    completed_at: str = Field(..., description="RFC3339 UTC timestamp for completion.")


class TaskStatusUpdateRequest(BaseModel):
    status: Literal["refunded", "failed"] = Field(..., description="New task status.")
    tx_hash: Optional[str] = Field(None, description="Transaction hash.")
    block_number: Optional[int] = Field(None, description="Block number.")


class TaskStatusResponse(BaseModel):
    task_id: int = Field(..., description="On-chain task id.")
    status: str = Field(..., description="Task status.")
    updated_at: str = Field(..., description="RFC3339 UTC timestamp for the update.")


class TaskPublicResponse(BaseModel):
    task_id: int = Field(..., description="On-chain task id.")
    status: str = Field(..., description="Task status.")
    input_hash: str = Field(..., description="Prepared input hash.")
    result_hash: Optional[str] = Field(None, description="Result hash.")
    result: Optional[TaskResultPayload] = None
