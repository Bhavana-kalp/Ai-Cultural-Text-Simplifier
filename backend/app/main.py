from fastapi import FastAPI
from app.routes import text
from fastapi.middleware.cors import CORSMiddleware
from app.routes import translate
from app.routes import simplify
app = FastAPI(title="Sanskrit Text Simplifier Backend")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501","http://localhost:3000"],  # Streamlit / React dev hosts
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# include OCR routes
app.include_router(simplify.router, prefix="/api", tags=["Simplify"])
app.include_router(text.router, prefix="/api", tags=["OCR"])
app.include_router(translate.router, prefix="/api", tags=["Translate"])
@app.get("/")
def root():
    return {"message": "Sanskrit Simplifier Backend Running!"}
