# backend/app/routes/simplify.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.simplify_service import simplify_with_glossary

router = APIRouter()

class SimplifyRequest(BaseModel):
    sanskrit: str
    hindi: str

class SimplifyResponse(BaseModel):
    simplified_hindi: str
    glossary: list

@router.post("/simplify", response_model=SimplifyResponse)
def simplify_endpoint(req: SimplifyRequest):
    """
    Accept Sanskrit + translated Hindi, return simplified Hindi + glossary.
    """
    try:
        result = simplify_with_glossary(req.sanskrit, req.hindi)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
