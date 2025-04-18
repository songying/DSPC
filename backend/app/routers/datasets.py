from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import List, Optional
from datetime import datetime
import shutil
import os
from pathlib import Path

from ..models import Dataset, DatasetCreate, User, DataType
from ..database import db
from ..auth import get_current_active_user
from ..blockchain import blockchain_service
from ..crypto import crypto_service

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Dataset)
async def create_dataset(
    name: str = Form(...),
    description: str = Form(...),
    data_type: str = Form(...),
    price: float = Form(...),
    terms_of_use: str = Form(...),
    supports_homomorphic: bool = Form(False),
    supports_zk_proof: bool = Form(False),
    supports_third_party: bool = Form(False),
    file_name: str = Form(None),
    file_type: str = Form(None),
    file_size: int = Form(None),
    encryption_key: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_id = f"{datetime.now().timestamp()}-{file.filename}"
    file_path = upload_dir / file_id
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    if not encryption_key:
        encryption_key = crypto_service.generate_key()
    
    data_hash = crypto_service.hash_data(str(file_content))
    
    dataset_data = {
        "name": name,
        "description": description,
        "data_type": data_type,
        "price": price,
        "terms_of_use": terms_of_use,
        "supports_homomorphic": supports_homomorphic,
        "supports_zk_proof": supports_zk_proof,
        "supports_third_party": supports_third_party,
        "file_name": file_name or file.filename,
        "file_type": file_type or file.content_type,
        "file_size": file_size or os.path.getsize(file_path),
        "encrypted_data": str(file_path),  # Store the file path instead of the content
        "owner_id": current_user.id,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    created_dataset = db.create_dataset(dataset_data)
    
    if blockchain_service.is_connected() and current_user.wallet_address:
        dummy_private_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
        
        tx_hash = blockchain_service.register_dataset(
            created_dataset["id"],
            data_hash,
            price,
            current_user.wallet_address,
            dummy_private_key
        )
        
        if tx_hash:
            db.update_dataset(created_dataset["id"], {"blockchain_tx": tx_hash})
    
    return created_dataset

@router.get("/", response_model=List[Dataset])
async def list_datasets(data_type: Optional[str] = None, current_user: User = Depends(get_current_active_user)):
    datasets = db.get_available_datasets()
    
    if data_type:
        datasets = [d for d in datasets if d["data_type"] == data_type]
    
    return datasets

@router.get("/my", response_model=List[Dataset])
async def list_my_datasets(current_user: User = Depends(get_current_active_user)):
    datasets = db.get_datasets_by_owner(current_user.id)
    return datasets

@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str, current_user: User = Depends(get_current_active_user)):
    dataset = db.get_dataset(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return dataset

@router.put("/{dataset_id}", response_model=Dataset)
async def update_dataset(dataset_id: str, dataset_update: dict, current_user: User = Depends(get_current_active_user)):
    dataset = db.get_dataset(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    if dataset["owner_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this dataset"
        )
    
    dataset_update["updated_at"] = datetime.now()
    updated_dataset = db.update_dataset(dataset_id, dataset_update)
    
    return updated_dataset

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(dataset_id: str, current_user: User = Depends(get_current_active_user)):
    dataset = db.get_dataset(dataset_id)
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    if dataset["owner_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this dataset"
        )
    
    db.update_dataset(dataset_id, {"is_available": False})
    
    return None
