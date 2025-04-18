"""
File storage system for the Privacy Data Protocol.
This module handles storing and retrieving dataset files from the filesystem.
"""

import os
import uuid
import shutil
from typing import Optional, Tuple
from fastapi import UploadFile
import hashlib

STORAGE_DIR = os.environ.get("STORAGE_DIR", "dataset_files")
os.makedirs(STORAGE_DIR, exist_ok=True)

def generate_file_index(file_path: str, owner_address: str) -> str:
    """
    Generate a unique file index based on file content and owner address
    
    Args:
        file_path: Path to the file
        owner_address: Owner's wallet address
        
    Returns:
        Unique file index
    """
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    combined = f"{file_hash}:{owner_address}:{uuid.uuid4()}"
    return hashlib.sha256(combined.encode()).hexdigest()

async def save_dataset_file(file: UploadFile, owner_address: str) -> Tuple[str, str, str]:
    """
    Save a dataset file to the filesystem
    
    Args:
        file: Uploaded file
        owner_address: Owner's wallet address
        
    Returns:
        Tuple containing (file_path, file_size, file_index)
    """
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".dat"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(STORAGE_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    file_size_str = f"{file_size:.2f} MB"
    
    file_index = generate_file_index(file_path, owner_address)
    
    return file_path, file_size_str, file_index

def save_text_data(data: str, owner_address: str) -> Tuple[str, str, str]:
    """
    Save text data as a file
    
    Args:
        data: Text data to save
        owner_address: Owner's wallet address
        
    Returns:
        Tuple containing (file_path, file_size, file_index)
    """
    unique_filename = f"{uuid.uuid4()}.txt"
    file_path = os.path.join(STORAGE_DIR, unique_filename)
    
    with open(file_path, "w") as f:
        f.write(data)
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    file_size_str = f"{file_size:.2f} MB"
    
    file_index = generate_file_index(file_path, owner_address)
    
    return file_path, file_size_str, file_index

def get_dataset_file(file_path: str) -> Optional[str]:
    """
    Get the content of a dataset file
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content or None if file not found
    """
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "r") as f:
        return f.read()

def delete_dataset_file(file_path: str) -> bool:
    """
    Delete a dataset file
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except:
        return False

def copy_dataset_file(source_path: str, destination_path: str) -> bool:
    """
    Copy a dataset file
    
    Args:
        source_path: Path to the source file
        destination_path: Path to the destination file
        
    Returns:
        True if copy was successful, False otherwise
    """
    try:
        shutil.copy2(source_path, destination_path)
        return True
    except:
        return False
