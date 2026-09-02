from pathlib import Path
from typing import List, Dict, Any, Optional
from app.services.rag.parser import extract_text_from_file
from app.services.rag.chunker import chunk_text
from app.database.repositories.document_repo import DocumentRepository
from app.logging_config import logger

class RAGService:
    @staticmethod
    def process_document(doc_id: str, file_path: Path) -> bool:
        try:
            text = extract_text_from_file(file_path)
            if not text.strip():
                DocumentRepository.update_status(doc_id, "failed", "File contains no readable text.")
                return False
                
            chunks = chunk_text(text, chunk_size=400, overlap=60)
            if not chunks:
                DocumentRepository.update_status(doc_id, "failed", "Could not generate chunks from text.")
                return False
                
            DocumentRepository.add_chunks(doc_id, chunks)
            DocumentRepository.update_status(doc_id, "ready")
            logger.info("Processed doc %s: %d chunks created", doc_id, len(chunks))
            return True
        except Exception as e:
            logger.error("Error processing document %s: %s", doc_id, e)
            DocumentRepository.update_status(doc_id, "failed", str(e))
            return False

    @staticmethod
    def query_knowledge(query: str, limit: int = 4) -> str:
        results = DocumentRepository.search_chunks(query, limit=limit)
        if not results:
            return ""
        
        context_parts = []
        for r in results:
            context_parts.append(f"Source [{r['filename']}]:\n{r['content']}")
        return "\n\n---\n\n".join(context_parts)

rag_service = RAGService()
