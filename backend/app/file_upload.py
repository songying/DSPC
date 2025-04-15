"""
Module for handling file uploads in the Privacy Data Protocol.
"""

import os
import uuid
from fastapi import UploadFile, HTTPException
from typing import Optional, List

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".csv", ".json", ".txt", ".xlsx", ".parquet"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

def ensure_upload_dir():
    """Ensure the upload directory exists."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def validate_file(file: UploadFile) -> bool:
    """
    Validate the uploaded file.
    
    Args:
        file: The uploaded file
        
    Returns:
        bool: True if the file is valid, False otherwise
    """
    if not file:
        return False
    
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return False
    
    return True

async def save_uploaded_file(file: UploadFile) -> Optional[str]:
    """
    Save an uploaded file to the uploads directory.
    
    Args:
        file: The uploaded file
        
    Returns:
        str: The path to the saved file, or None if the file could not be saved
    """
    if not validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file type. Allowed types: csv, json, txt, xlsx, parquet")
    
    ensure_upload_dir()
    
    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        contents = await file.read()
        
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024 * 1024)} MB")
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: The path to the file
        
    Returns:
        int: The size of the file in bytes
    """
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0

def delete_file(file_path: str) -> bool:
    """
    Delete a file.
    
    Args:
        file_path: The path to the file
        
    Returns:
        bool: True if the file was deleted, False otherwise
    """
    try:
        os.remove(file_path)
        return True
    except Exception:
        return False
