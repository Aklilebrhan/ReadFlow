import shutil
import subprocess
from typing import Optional
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class OCREngine:
    """OCR fallback engine for scanned PDFs or raster pages."""

    def __init__(self):
        self.tesseract_cmd = shutil.which("tesseract")
        self.enabled = settings.OCR_ENABLED and self.tesseract_cmd is not None

    def ocr_image_bytes(self, image_bytes: bytes) -> str:
        """Performs optical character recognition on raw image bytes."""
        if not self.enabled:
            logger.info("OCR requested, but Tesseract binary is not installed on system. Using fallback notice.")
            return "[OCR text extraction unavailable: Tesseract engine not found in environment PATH]"

        try:
            process = subprocess.Popen(
                [self.tesseract_cmd, "stdin", "stdout", "--oem", "1", "-l", "eng"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=image_bytes)
            if process.returncode == 0:
                return stdout.decode("utf-8", errors="ignore").strip()
            else:
                logger.warning("OCR process error: %s", stderr.decode("utf-8", errors="ignore"))
                return ""
        except Exception as e:
            logger.error("OCR execution failed: %s", str(e))
            return ""


ocr_engine = OCREngine()
