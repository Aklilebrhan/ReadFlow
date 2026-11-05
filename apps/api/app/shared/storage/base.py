from abc import ABC, abstractmethod


class BaseStorageService(ABC):
    """Abstract interface for document file storage."""

    @abstractmethod
    async def save_file(self, path: str, content: bytes) -> str:
        """Saves file content to storage and returns the storage reference identifier/path."""
        pass

    @abstractmethod
    async def read_file(self, path: str) -> bytes:
        """Reads file bytes from storage."""
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Deletes file from storage."""
        pass

    @abstractmethod
    async def file_exists(self, path: str) -> bool:
        """Checks if file exists in storage."""
        pass
