from app.core.config import settings
from app.shared.storage.base import BaseStorageService
from app.shared.storage.local import LocalStorageService
from app.shared.storage.s3 import S3StorageService

_storage_instance: BaseStorageService = None


def get_storage_service() -> BaseStorageService:
    """Factory returns singleton storage instance based on configuration."""
    global _storage_instance
    if _storage_instance is None:
        if settings.STORAGE_PROVIDER == "s3":
            _storage_instance = S3StorageService()
        else:
            _storage_instance = LocalStorageService()
    return _storage_instance
