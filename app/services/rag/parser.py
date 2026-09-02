from pathlib import Path
from typing import Optional
from app.logging_config import logger

def extract_text_from_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    
    if ext in [".txt", ".md", ".markdown"]:
        try:
            return file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.error("Error reading text file %s: %s", file_path, e)
            raise ValueError(f"Could not read text file: {e}")
            
    elif ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n\n".join(pages_text)
        except Exception as e:
            logger.error("Error reading PDF file %s: %s", file_path, e)
            raise ValueError(f"Failed to extract text from PDF: {e}")
            
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only PDF, TXT, and Markdown are supported.")
