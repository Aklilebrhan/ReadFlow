import os
from app.core.exceptions import UnsupportedFormatError
from app.modules.extraction.base import BaseExtractor
from app.modules.extraction.pdf_extractor import PDFExtractor
from app.modules.extraction.docx_extractor import DocxExtractor
from app.modules.extraction.text_extractor import TextExtractor


def get_extractor_for_file(filename: str) -> BaseExtractor:
    """Factory selecting the appropriate document extractor based on file extension."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return PDFExtractor()
    elif ext in [".docx", ".doc"]:
        return DocxExtractor()
    elif ext in [".txt", ".md", ".markdown"]:
        return TextExtractor()
    else:
        raise UnsupportedFormatError(
            f"Unsupported file format '{ext}'. ReadFlow supports PDF (.pdf), Word (.docx), Markdown (.md), and Text (.txt) files."
        )
