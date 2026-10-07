from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.services.rag import ingest_document

router = APIRouter(prefix="/documents", tags=["Documents"])
ALLOWED_EXTENSIONS = (".pdf", ".txt")
MAX_SIZE_BYTES = 5 * 1024 * 1024


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(file: UploadFile = File(...)):
    filename = file.filename or ""
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed")

    content = file.file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    try:
        chunks = ingest_document(filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"filename": filename, "chunks": chunks}
