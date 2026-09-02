import re
from typing import List

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []
    
    words = text.split(' ')
    if len(words) <= chunk_size:
        return [text]
        
    chunks = []
    start = 0
    step = max(1, chunk_size - overlap)
    
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(words):
            break
        start += step
        
    return chunks
