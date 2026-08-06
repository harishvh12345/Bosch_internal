import os
import shutil
from typing import BinaryIO
from app.core.config import settings
from app.interfaces.storage import StorageService

class LocalStorageService(StorageService):
    async def upload_file(self, file_data: BinaryIO, filename: str, folder: str = "") -> str:
        # Determine destination folder
        dest_dir = settings.UPLOAD_DIR
        if folder:
            dest_dir = dest_dir / folder
            
        os.makedirs(dest_dir, exist_ok=True)
        
        # Clean up filename to prevent folder traversal
        safe_filename = os.path.basename(filename)
        dest_path = dest_dir / safe_filename
        
        # Write bytes
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file_data, buffer)
            
        # Return path relative to project root or direct local path
        return str(dest_path)

    async def download_file(self, filepath: str) -> bytes:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, "rb") as file:
            return file.read()

    async def delete_file(self, filepath: str) -> bool:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

local_storage = LocalStorageService()
