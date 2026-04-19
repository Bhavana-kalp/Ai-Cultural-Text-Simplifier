from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from app.services.mcq_service import generate_mcqs

router = APIRouter()


class MCQRequest(BaseModel):
    glossary: List[Dict]
    num_questions: int = 5


@router.post("/mcq")
def generate_mcq_endpoint(req: MCQRequest):
    mcqs = generate_mcqs(req.glossary, req.num_questions)
    return {"mcqs": mcqs}