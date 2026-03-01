from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr_service import perform_ocr

router = APIRouter()

@router.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    OCR endpoint to extract Sanskrit text from uploaded image.
    """
    try:
        image_bytes = await file.read()
        text = perform_ocr(image_bytes, primary_lang="san", fallback_lang="hin")
 # fallback Hindi
        return {"extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
