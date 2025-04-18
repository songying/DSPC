"""
Datasets router for the Privacy Data Protocol with MongoDB and blockchain integration.
This module handles dataset creation, retrieval, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime
import uuid
import random

from ..auth import get_current_user
from ..mongodb import (
    store_dataset, 
    update_dataset_contract, 
    store_contract_info, 
    get_dataset, 
    get_datasets, 
    count_datasets
)
from ..file_storage import save_dataset_file, save_text_data
from ..blockchain_contract import deploy_dataset_contract

router = APIRouter(
    prefix="/api/datasets",
    tags=["datasets"],
    responses={404: {"description": "Not found"}},
)

@router.post("")
async def create_dataset(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    file: Optional[UploadFile] = File(None),
    text_data: Optional[str] = Form(None),
    privacy_options: List[str] = Form([]),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new dataset with MongoDB and blockchain integration
    """
    try:
        owner_address = current_user["wallet_address"]
        file_path = None
        file_size = "0 MB"
        file_index = ""
        records = 0
        
        if file and file.filename:
            file_path, file_size, file_index = await save_dataset_file(file, owner_address)
            records = random.randint(10000, 1000000)  # In a real system, this would be calculated
        elif text_data:
            file_path, file_size, file_index = save_text_data(text_data, owner_address)
            records = len(text_data.splitlines())
        else:
            raise HTTPException(status_code=400, detail="Either file or text data must be provided")
        
        dataset_id = store_dataset(
            name=name,
            description=description,
            price=price,
            owner=owner_address,
            privacy_options=privacy_options,
            file_path=file_path,
            file_size=file_size,
            records=records,
            category="Custom Dataset"
        )
        
        private_key = os.environ.get("ETHEREUM_PRIVATE_KEY", "0x0000000000000000000000000000000000000000000000000000000000000001")
        
        try:
            contract_address, tx_hash = deploy_dataset_contract(
                private_key=private_key,
                name=name,
                description=description,
                price_eth=price,
                file_index=file_index,
                privacy_options=privacy_options,
                record_count=records
            )
            
            update_dataset_contract(dataset_id, contract_address)
            
            store_contract_info(
                dataset_id=dataset_id,
                contract_address=contract_address,
                transaction_hash=tx_hash,
                file_index=file_index,
                metadata={
                    "name": name,
                    "description": description,
                    "price": price,
                    "privacy_options": privacy_options,
                    "records": records
                }
            )
        except Exception as e:
            print(f"Contract deployment failed: {str(e)}")
        
        dataset = get_dataset(dataset_id)
        
        return dataset
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating dataset: {str(e)}")

@router.get("")
async def get_all_datasets(
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1, le=100),
    owner: Optional[str] = None
):
    """
    Get all datasets with pagination
    """
    skip = (page - 1) * limit
    datasets_list = get_datasets(owner=owner, limit=limit, skip=skip)
    total = count_datasets(owner=owner)
    
    return {
        "datasets": datasets_list,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit  # Ceiling division
    }

@router.get("/{dataset_id}")
async def get_dataset_by_id(dataset_id: str):
    """
    Get a dataset by ID
    """
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    return dataset

@router.get("/user/{user_id}")
async def get_user_datasets(
    user_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1, le=100)
):
    """
    Get datasets owned by a user
    """
    skip = (page - 1) * limit
    datasets_list = get_datasets(owner=user_id, limit=limit, skip=skip)
    total = count_datasets(owner=user_id)
    
    return {
        "datasets": datasets_list,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit  # Ceiling division
    }
