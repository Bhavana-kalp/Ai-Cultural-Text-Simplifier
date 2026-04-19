from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from app.services.fill_blanks_service import generate_fill_in_blanks

router = APIRouter()


class FillBlanksRequest(BaseModel):
    sanskrit_text: str
    glossary: List[Dict]
    num_blanks: int = 4


@router.post("/fill-blanks")
def fill_blanks_endpoint(req: FillBlanksRequest):
    result = generate_fill_in_blanks(
        req.sanskrit_text,
        req.glossary,
        req.num_blanks
    )
    return result