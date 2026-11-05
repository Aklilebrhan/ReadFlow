import pytest
import pymupdf as fitz
from app.modules.extraction.pdf_extractor import PDFExtractor
from app.modules.extraction.text_extractor import TextExtractor
from app.modules.extraction.factory import get_extractor_for_file
from app.core.exceptions import UnsupportedFormatError


@pytest.mark.asyncio
async def test_pdf_extraction():
    # Create an in-memory PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "ReadFlow AI Architecture\n\nThis document describes the modern retrieval augmented generation pipeline.")
    pdf_bytes = doc.tobytes()
    doc.close()

    extractor = PDFExtractor()
    extracted = await extractor.extract(pdf_bytes, "test_paper.pdf")

    assert extracted.page_count == 1
    assert "ReadFlow AI Architecture" in extracted.raw_text
    assert extracted.word_count > 5
    assert len(extracted.pages) == 1
    assert extracted.pages[0].page_number == 1


@pytest.mark.asyncio
async def test_markdown_extraction():
    content = "# Introduction\n\nReadFlow provides document intelligence.\n\n# Chapter 2\n\nChunking preserves context."
    raw_bytes = content.encode("utf-8")

    extractor = TextExtractor()
    extracted = await extractor.extract(raw_bytes, "notes.md")

    assert extracted.page_count >= 1
    assert "document intelligence" in extracted.raw_text
    assert "Introduction" in extracted.pages[0].headings or "Chapter 2" in extracted.pages[0].headings


def test_factory_extractor():
    pdf_ext = get_extractor_for_file("research.pdf")
    assert isinstance(pdf_ext, PDFExtractor)

    md_ext = get_extractor_for_file("readme.md")
    assert isinstance(md_ext, TextExtractor)

    with pytest.raises(UnsupportedFormatError):
        get_extractor_for_file("archive.zip")
