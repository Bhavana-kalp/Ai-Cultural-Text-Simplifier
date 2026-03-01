# backend/app/routes/translate.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.translate_service import preprocess_sanskrit_text, translate_text_to_hindi

router = APIRouter()

class TranslateRequest(BaseModel):
    text: str

class TranslateResponse(BaseModel):
    preprocessed_text: str
    hindi: str
    raw_response: dict = None

@router.post("/translate", response_model=TranslateResponse)
def translate_endpoint(req: TranslateRequest):
    """
    Accepts JSON: {"text": "<sanskrit_text>"}
    Returns: preprocessed text and translated Hindi text.
    """
    try:
        pre = preprocess_sanskrit_text(req.text)
        hindi, raw = translate_text_to_hindi(pre)
        return {"preprocessed_text": pre, "hindi": hindi, "raw_response": raw}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
