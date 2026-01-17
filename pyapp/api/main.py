from fastapi import Depends, FastAPI, HTTPException, Query

from pyapp.api.internal_auth import require_internal_api_key
from pyapp.models.schemas import (
    TaskClaimRequest,
    TaskClaimResponse,
    TaskInput,
    TaskInputResponse,
    TaskPrepareResponse,
    TaskPublicResponse,
    TaskResultRequest,
    TaskResultResponse,
    TaskStatusResponse,
    TaskStatusUpdateRequest,
    TextRequest,
    TranslationResponse,
)
from pyapp.services.task_service import (
    HashMismatchError,
    TaskConflictError,
    TaskNotFoundError,
    TaskService,
    get_task_service,
)
from pyapp.services.translator import TranslatorService, get_service

app = FastAPI(title="AI Translator", version="0.1.0")


@app.post("/translate/chinese", response_model=TranslationResponse)
def translate_chinese(req: TextRequest, svc: TranslatorService = Depends(get_service)) -> TranslationResponse:
    return svc.translate_chinese(req.text, include_grammar=req.include_grammar)


@app.post("/correct/english", response_model=TranslationResponse)
def correct_english(req: TextRequest, svc: TranslatorService = Depends(get_service)) -> TranslationResponse:
    return svc.correct_english(req.text, include_grammar=req.include_grammar)


@app.post("/tasks/prepare", response_model=TaskPrepareResponse)
def prepare_task(payload: TaskInput, svc: TaskService = Depends(get_task_service)) -> TaskPrepareResponse:
    return svc.prepare(payload)


@app.post(
    "/tasks/claim",
    response_model=TaskClaimResponse,
    dependencies=[Depends(require_internal_api_key)],
)
def claim_task(req: TaskClaimRequest, svc: TaskService = Depends(get_task_service)) -> TaskClaimResponse:
    try:
        return svc.claim(req)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(exc)}) from exc
    except TaskConflictError as exc:
        raise HTTPException(status_code=409, detail={"code": "CONFLICT", "message": str(exc)}) from exc


@app.get(
    "/tasks/input/{input_hash}",
    response_model=TaskInputResponse,
    dependencies=[Depends(require_internal_api_key)],
)
def get_task_input(input_hash: str, svc: TaskService = Depends(get_task_service)) -> TaskInputResponse:
    try:
        return svc.get_input(input_hash)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(exc)}) from exc


@app.post(
    "/tasks/{task_id}/result",
    response_model=TaskResultResponse,
    dependencies=[Depends(require_internal_api_key)],
)
def submit_result(task_id: int, req: TaskResultRequest, svc: TaskService = Depends(get_task_service)) -> TaskResultResponse:
    try:
        return svc.store_result(task_id, req)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(exc)}) from exc
    except HashMismatchError as exc:
        raise HTTPException(status_code=409, detail={"code": "HASH_MISMATCH", "message": str(exc)}) from exc
    except TaskConflictError as exc:
        raise HTTPException(status_code=409, detail={"code": "CONFLICT", "message": str(exc)}) from exc


@app.post(
    "/tasks/{task_id}/status",
    response_model=TaskStatusResponse,
    dependencies=[Depends(require_internal_api_key)],
)
def update_task_status(
    task_id: int, req: TaskStatusUpdateRequest, svc: TaskService = Depends(get_task_service)
) -> TaskStatusResponse:
    try:
        return svc.update_status(task_id, req)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(exc)}) from exc


@app.get("/tasks/{task_id}", response_model=TaskPublicResponse)
def get_task(
    task_id: int,
    include_result: bool = Query(False, description="Include result payload when available."),
    svc: TaskService = Depends(get_task_service),
) -> TaskPublicResponse:
    try:
        return svc.get_public(task_id, include_result=include_result)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": str(exc)}) from exc


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
