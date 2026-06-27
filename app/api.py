import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel

from app.ingest import ingest_pdf
from app.query import query_documents

app = FastAPI(
    title="ragchat",
    description=(
        "Chat with your documents using RAG. "
        "Upload PDFs, ask questions, get cited answers."
    ),
    version="0.1.0",
)


class QueryRequest(BaseModel):
    question: str


class Source(BaseModel):
    filename: str
    page: int
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


class IngestResponse(BaseModel):
    filename: str
    chunks: int
    pages: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        result = ingest_pdf(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return result


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    result = query_documents(req.question)
    return result
