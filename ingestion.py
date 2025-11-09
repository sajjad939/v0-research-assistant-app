import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import PyPDF2
import io

@dataclass
class DocumentChunk:
    content: str
    chunk_id: int
    page_num: Optional[int] = None
    start_char: int = 0

class DocumentProcessor:
    """Handles document parsing, chunking, and metadata extraction."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def read_pdf(self, file_obj) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(file_obj)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")
    
    def extract_chunks(self, text: str, chunk_size: Optional[int] = None) -> List[DocumentChunk]:
        """Split text into overlapping chunks with metadata."""
        if chunk_size is None:
            chunk_size = self.chunk_size
        
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        current_size = 0
        chunk_id = 0
        
        for sentence in sentences:
            if current_size + len(sentence) > chunk_size and current_chunk:
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    chunk_id=chunk_id,
                    start_char=len("\n".join([c.content for c in chunks]))
                ))
                
                # Overlap: keep last 30% of chunk
                overlap_content = current_chunk[-int(chunk_size * 0.3):]
                current_chunk = overlap_content + " " + sentence
                current_size = len(current_chunk)
                chunk_id += 1
            else:
                current_chunk += " " + sentence
                current_size += len(sentence)
        
        if current_chunk.strip():
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                chunk_id=chunk_id,
                start_char=len("\n".join([c.content for c in chunks]))
            ))
        
        return chunks
    
    def parse_metadata(self, text: str, filename: str) -> Dict[str, str]:
        """Extract metadata from document."""
        metadata = {
            "filename": filename,
            "title": self._extract_title(text, filename),
            "authors": self._extract_authors(text),
            "year": self._extract_year(text),
            "datasets": self._extract_datasets(text),
            "metrics": self._extract_metrics(text),
            "word_count": len(text.split()),
            "chunk_count": len(self.extract_chunks(text))
        }
        return metadata
    
    def _extract_title(self, text: str, filename: str) -> str:
        """Extract or infer title."""
        lines = text.split('\n')
        if lines:
            return lines[0][:100] or filename.replace('.pdf', '').replace('.txt', '')
        return filename
    
    def _extract_authors(self, text: str) -> str:
        """Extract author names if present."""
        author_patterns = [
            r'(?:by|authors?|(?:written\s+)?by)\s+([^,\n]+(?:,\s*[^,\n]+)*)',
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+and\s+[A-Z][a-z]+\s+[A-Z][a-z]+)*)',
        ]
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return "Unknown"
    
    def _extract_year(self, text: str) -> str:
        """Extract publication year."""
        match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
        return match.group(1) if match else "Unknown"
    
    def _extract_datasets(self, text: str) -> str:
        """Extract mentioned datasets."""
        datasets = re.findall(r'\b(?:dataset|benchmark|corpus)\s*[:\-]?\s*([^\n,]+)', text, re.IGNORECASE)
        return "; ".join(datasets[:3]) if datasets else "None mentioned"
    
    def _extract_metrics(self, text: str) -> str:
        """Extract performance metrics."""
        metrics = re.findall(r'\b(?:accuracy|precision|recall|F1|RMSE|MAE|AUC|BLEU)\b[:\s=]+[\d.]+%?', text, re.IGNORECASE)
        return "; ".join(metrics[:3]) if metrics else "None mentioned"
