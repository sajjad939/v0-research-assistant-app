import pytest
from ingestion import DocumentProcessor

def test_chunk_extraction():
    """Test document chunking."""
    processor = DocumentProcessor(chunk_size=100, overlap=20)
    
    text = "This is a test. " * 20  # Create repetitive text
    chunks = processor.extract_chunks(text)
    
    assert len(chunks) > 1
    assert all(len(c.content) > 0 for c in chunks)

def test_metadata_extraction():
    """Test metadata parsing."""
    processor = DocumentProcessor()
    
    sample_text = """
    Deep Learning in 2023
    By Smith and Johnson
    Year: 2023
    """
    
    metadata = processor.parse_metadata(sample_text, "test.txt")
    
    assert metadata["year"] == "2023"
    assert metadata["filename"] == "test.txt"
    assert metadata["word_count"] > 0

def test_title_extraction():
    """Test title extraction."""
    processor = DocumentProcessor()
    
    text = "Research on Machine Learning Algorithms\nThis is the content."
    title = processor._extract_title(text, "doc.txt")
    
    assert title == "Research on Machine Learning Algorithms"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
