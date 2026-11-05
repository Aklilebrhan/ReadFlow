import os
import aiofiles
from app.core.config import settings
from app.core.exceptions import StorageError
from app.shared.storage.base import BaseStorageService
from app.core.logging import get_logger

logger = get_logger(__name__)


class LocalStorageService(BaseStorageService):
    """Local filesystem storage implementation."""

    def __init__(self, base_path: str = None):
        self.base_path = os.path.abspath(base_path or settings.LOCAL_STORAGE_PATH)
        os.makedirs(self.base_path, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        # Sanitize and resolve within base_path
        clean_path = os.path.normpath(path).lstrip("/\\")
        return os.path.join(self.base_path, clean_path)

    async def save_file(self, path: str, content: bytes) -> str:
        try:
            full_path = self._resolve_path(path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(content)
            logger.info("File saved to local storage: %s", full_path)
            return path
        except Exception as e:
            logger.error("Failed to save file %s: %s", path, str(e))
            raise StorageError(f"Failed to save file: {str(e)}")

    async def read_file(self, path: str) -> bytes:
        try:
            full_path = self._resolve_path(path)
            if not os.path.exists(full_path):
                raise StorageError(f"File not found: {path}")
            with open(full_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error("Failed to read file %s: %s", path, str(e))
            raise StorageError(f"Failed to read file: {str(e)}")

    async def delete_file(self, path: str) -> bool:
        try:
            full_path = self._resolve_path(path)
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info("File removed from local storage: %s", full_path)
                return True
            return False
        except Exception as e:
            logger.error("Failed to delete file %s: %s", path, str(e))
            raise StorageError(f"Failed to delete file: {str(e)}")

    async def file_exists(self, path: str) -> bool:
        full_path = self._resolve_path(path)
        return os.path.exists(full_path)
