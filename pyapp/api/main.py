from fastapi import Depends, FastAPI

from pyapp.models.schemas import TextRequest, TranslationResponse
from pyapp.services.translator import TranslatorService, get_service

app = FastAPI(title="AI Translator", version="0.1.0")


@app.post("/translate/chinese", response_model=TranslationResponse)
def translate_chinese(req: TextRequest, svc: TranslatorService = Depends(get_service)) -> TranslationResponse:
    return svc.translate_chinese(req.text, include_grammar=req.include_grammar)


@app.post("/correct/english", response_model=TranslationResponse)
def correct_english(req: TextRequest, svc: TranslatorService = Depends(get_service)) -> TranslationResponse:
    return svc.correct_english(req.text, include_grammar=req.include_grammar)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

