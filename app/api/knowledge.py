import uuid
import re
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.schemas.knowledge import DocumentResponse, KnowledgeQueryRequest
from app.database.repositories.document_repo import DocumentRepository
from app.services.rag.service import rag_service
from app.logging_config import logger

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

SAFE_FILENAME_RE = re.compile(r'[^a-zA-Z0-9_\-\.]')

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Document file is required.")
        
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Sanitize filename
    clean_name = SAFE_FILENAME_RE.sub('_', Path(file.filename).name)
    save_filename = f"{uuid.uuid4().hex[:8]}_{clean_name}"
    dest_path = settings.UPLOAD_DIR / save_filename

    content = await file.read()
    file_size = len(content)
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE_MB}MB)."
        )

    try:
        dest_path.write_bytes(content)
        doc = DocumentRepository.create_document(
            filename=clean_name,
            file_path=str(dest_path),
            file_size=file_size,
            file_type=ext,
            status="processing"
        )
        
        # Process and chunk document
        success = rag_service.process_document(doc["id"], dest_path)
        doc_updated = DocumentRepository.get_document(doc["id"])
        return doc_updated or doc
    except Exception as e:
        logger.error("Error uploading document: %s", e)
        dest_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents():
    return DocumentRepository.list_documents()

@router.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    doc = DocumentRepository.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    # Remove file from disk
    try:
        p = Path(doc["file_path"])
        if p.exists():
            p.unlink(missing_ok=True)
    except Exception as e:
        logger.warning("Could not delete file from disk: %s", e)

    DocumentRepository.delete_document(doc_id)
    return {"status": "deleted", "id": doc_id}

@router.post("/query")
def query_knowledge_base(payload: KnowledgeQueryRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    result = rag_service.query_knowledge(query)
    return {"query": query, "context": result}
