from abc import ABC, abstractmethod
from typing import BinaryIO

class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, file_data: BinaryIO, filename: str, folder: str = "") -> str:
        """Upload a file to the storage and return its access URL/path."""
        pass

    @abstractmethod
    async def download_file(self, filepath: str) -> bytes:
        """Download and return the bytes of a stored file."""
        pass

    @abstractmethod
    async def delete_file(self, filepath: str) -> bool:
        """Delete a file from the storage system."""
        pass
