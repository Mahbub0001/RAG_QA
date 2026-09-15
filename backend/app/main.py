import os
import tempfile
import uuid

from fastapi import FastAPI, UploadFile, HTTPException, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .ingestion import ingest_pdf
from .rag_chain import ask as ask_rag

class AskRequest(BaseModel):
    question: str
    collection: str | None = None
    k: int | None = None

app = FastAPI(title="PDF Question Answering API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...), collection:str|None =Form(None)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Create a temporary file to store the uploaded PDF
    temp_file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.pdf")
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())

    try:
        ingest_pdf(temp_file_path, collection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(temp_file_path)

    return {"message": "PDF ingested successfully."}

@app.post("/ask")
def ask(req: AskRequest):
    try:
        return ask_rag(collection= req.collection or "pdf_doc",
                       question=req.question,
                       k=req.k or 4)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))