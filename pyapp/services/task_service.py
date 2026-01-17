import json
from typing import Optional, Tuple

from pyapp.models.schemas import (
    TaskClaimRequest,
    TaskClaimResponse,
    TaskInput,
    TaskInputResponse,
    TaskPrepareResponse,
    TaskPublicResponse,
    TaskResultPayload,
    TaskResultRequest,
    TaskResultResponse,
    TaskStatusResponse,
    TaskStatusUpdateRequest,
)
from pyapp.db import init_task_repository
from pyapp.repositories.task_repo import TaskRepository
from pyapp.utils.hash_utils import hash_payload
from pyapp.utils.time_utils import format_utc_timestamp, parse_utc_timestamp, utc_now


class TaskNotFoundError(Exception):
    pass


class TaskConflictError(Exception):
    pass


class HashMismatchError(Exception):
    pass


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def prepare(self, payload: TaskInput) -> TaskPrepareResponse:
        data = payload.model_dump()
        input_hash, canonical = hash_payload(data)
        existing = self.repository.get_by_input_hash(input_hash)
        if existing:
            return TaskPrepareResponse(
                input_hash=input_hash,
                input_ref=input_hash,
                prepared_at=existing["created_at"],
                deduped=True,
            )

        prepared_at = format_utc_timestamp(utc_now())
        self.repository.insert_prepared(input_hash, canonical, prepared_at)
        return TaskPrepareResponse(
            input_hash=input_hash,
            input_ref=input_hash,
            prepared_at=prepared_at,
            deduped=False,
        )

    def claim(self, req: TaskClaimRequest) -> TaskClaimResponse:
        row = self.repository.get_by_input_hash(req.input_hash)
        if not row:
            raise TaskNotFoundError("input_hash not found")
        if row["task_id"] is not None and row["task_id"] != req.task_id:
            raise TaskConflictError("input_hash already bound to a different task_id")

        existing_task = self.repository.get_by_task_id(req.task_id)
        if existing_task and existing_task["input_hash"] != req.input_hash:
            raise TaskConflictError("task_id already bound to a different input_hash")

        updated_at = format_utc_timestamp(utc_now())
        self.repository.update_claim(
            task_id=req.task_id,
            input_hash=req.input_hash,
            requester=req.requester,
            model=req.model,
            fee=req.fee,
            chain_id=req.chain_id,
            tx_hash=req.tx_hash,
            block_number=req.block_number,
            timestamp=updated_at,
        )
        return TaskClaimResponse(
            task_id=req.task_id,
            status="created",
            updated_at=updated_at,
        )

    def get_input(self, input_hash: str) -> TaskInputResponse:
        row = self.repository.get_by_input_hash(input_hash)
        if not row:
            raise TaskNotFoundError("input_hash not found")
        payload = json.loads(row["input_payload"])
        return TaskInputResponse(
            input_hash=input_hash,
            input_payload=TaskInput(**payload),
            prepared_at=row["created_at"],
        )

    def store_result(self, task_id: int, req: TaskResultRequest) -> TaskResultResponse:
        row = self.repository.get_by_task_id(task_id)
        if not row:
            raise TaskNotFoundError("task_id not found")

        result_hash, canonical = self._hash_result_payload(req.result_payload)
        if req.result_hash and req.result_hash != result_hash:
            raise HashMismatchError("result_hash mismatch")
        if row["result_hash"] and row["result_hash"] != result_hash:
            raise TaskConflictError("task already has a different result_hash")

        completed_at = format_utc_timestamp(utc_now())
        if not row["result_hash"]:
            self.repository.update_result(
                task_id=task_id,
                result_hash=result_hash,
                result_payload=canonical,
                timestamp=completed_at,
            )
        else:
            completed_at = row["updated_at"]

        return TaskResultResponse(
            task_id=task_id,
            result_hash=result_hash,
            status="completed",
            completed_at=completed_at,
        )

    def update_status(self, task_id: int, req: TaskStatusUpdateRequest) -> TaskStatusResponse:
        row = self.repository.get_by_task_id(task_id)
        if not row:
            raise TaskNotFoundError("task_id not found")
        updated_at = format_utc_timestamp(utc_now())
        self.repository.update_status(
            task_id=task_id,
            status=req.status,
            tx_hash=req.tx_hash,
            block_number=req.block_number,
            timestamp=updated_at,
        )
        return TaskStatusResponse(
            task_id=task_id,
            status=req.status,
            updated_at=updated_at,
        )

    def get_public(self, task_id: int, include_result: bool) -> TaskPublicResponse:
        row = self.repository.get_by_task_id(task_id)
        if not row:
            raise TaskNotFoundError("task_id not found")
        result_payload = None
        if include_result and row["result_payload"]:
            payload = json.loads(row["result_payload"])
            result_payload = TaskResultPayload(**payload)
        return TaskPublicResponse(
            task_id=task_id,
            status=row["status"],
            input_hash=row["input_hash"],
            result_hash=row["result_hash"],
            result=result_payload,
        )

    @staticmethod
    def _hash_result_payload(payload: TaskResultPayload) -> Tuple[str, str]:
        data = payload.model_dump()
        normalized_ts = format_utc_timestamp(parse_utc_timestamp(data["timestamp"]))
        data["timestamp"] = normalized_ts
        return hash_payload(data)


def get_task_service() -> TaskService:
    return TaskService(repository=init_task_repository())
