import pytest
from app.modules.chunking.recursive_chunker import RecursiveCharacterChunker
from app.modules.chunking.sentence_chunker import SentenceBoundaryChunker
from app.modules.extraction.base import ExtractedDocument, ExtractedPage


def test_recursive_chunking():
    chunker = RecursiveCharacterChunker()
    pages = [
        ExtractedPage(
            page_number=1,
            text="First sentence about document retrieval. Second sentence discusses vector spaces. Third sentence addresses reranking.",
            headings=["Overview"]
        ),
        ExtractedPage(
            page_number=2,
            text="Fourth sentence starts page two. Fifth sentence explains citations. Sixth sentence validates answers.",
            headings=["Methodology"]
        )
    ]
    extracted = ExtractedDocument(
        raw_text="Full text",
        pages=pages,
        page_count=2,
        word_count=30
    )

    chunks = chunker.chunk_document(extracted, chunk_size=80, chunk_overlap=20)
    assert len(chunks) >= 2

    # Verify metadata preservation
    assert chunks[0].page_number == 1
    assert chunks[0].section_title == "Overview"
    assert chunks[-1].page_number == 2
    assert chunks[-1].section_title == "Methodology"


def test_sentence_chunking():
    chunker = SentenceBoundaryChunker()
    pages = [
        ExtractedPage(
            page_number=1,
            text="This is sentence one. This is sentence two. This is sentence three.",
            headings=["Section A"]
        )
    ]
    extracted = ExtractedDocument(raw_text="", pages=pages, page_count=1, word_count=12)

    chunks = chunker.chunk_document(extracted, chunk_size=45, chunk_overlap=15)
    assert len(chunks) >= 2
    # Check that sentences aren't chopped in the middle
    for chunk in chunks:
        assert chunk.text.endswith(".")
