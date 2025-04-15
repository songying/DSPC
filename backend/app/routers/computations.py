from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import ComputationRequest, ComputationRequestCreate, ComputationResult, User, Dataset
from ..database import db
from ..auth import get_current_active_user
from ..blockchain import blockchain_service
from ..crypto import crypto_service

router = APIRouter(
    prefix="/computations",
    tags=["computations"],
    responses={404: {"description": "Not found"}},
)

@router.post("/request", response_model=ComputationRequest)
async def request_computation(request: ComputationRequestCreate, current_user: User = Depends(get_current_active_user)):
    dataset = db.get_dataset(request.dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    if not dataset.get("is_available", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset is not available for computation"
        )
    
    request_data = request.dict()
    request_data["requester_id"] = current_user.id
    request_data["status"] = "pending"
    request_data["created_at"] = datetime.now()
    request_data["updated_at"] = datetime.now()
    
    created_request = db.create_computation_request(request_data)
    
    if blockchain_service.is_connected() and current_user.wallet_address:
        dummy_private_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
        
        tx_hash = blockchain_service.request_computation(
            request.dataset_id,
            created_request["id"],
            request.computation_type,
            current_user.wallet_address,
            dummy_private_key,
            dataset["price"]
        )
        
        if tx_hash:
            db.update_computation_request(created_request["id"], {
                "transaction_hash": tx_hash,
                "status": "processing"
            })
            created_request["transaction_hash"] = tx_hash
            created_request["status"] = "processing"
    
    return created_request

@router.get("/my-requests", response_model=List[ComputationRequest])
async def list_my_computation_requests(current_user: User = Depends(get_current_active_user)):
    requests = db.get_computation_requests_by_requester(current_user.id)
    return requests

@router.get("/dataset/{dataset_id}", response_model=List[ComputationRequest])
async def list_dataset_computation_requests(dataset_id: str, current_user: User = Depends(get_current_active_user)):
    dataset = db.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    if dataset["owner_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view computation requests for this dataset"
        )
    
    requests = db.get_computation_requests_by_dataset(dataset_id)
    return requests

@router.get("/{request_id}", response_model=ComputationRequest)
async def get_computation_request(request_id: str, current_user: User = Depends(get_current_active_user)):
    request = db.get_computation_request(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computation request not found"
        )
    
    dataset = db.get_dataset(request["dataset_id"])
    if request["requester_id"] != current_user.id and dataset["owner_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this computation request"
        )
    
    return request

@router.post("/{request_id}/process", response_model=ComputationResult)
async def process_computation(
    request_id: str, 
    result_data: Dict[str, Any], 
    current_user: User = Depends(get_current_active_user)
):
    request = db.get_computation_request(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computation request not found"
        )
    
    dataset = db.get_dataset(request["dataset_id"])
    
    if dataset["owner_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to process this computation request"
        )
    
    if request["status"] not in ["pending", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Computation request is in {request['status']} state and cannot be processed"
        )
    
    result_hash = crypto_service.hash_data(str(result_data.get("encrypted_result", "")))
    
    result = {
        "computation_id": request_id,
        "encrypted_result": result_data.get("encrypted_result", ""),
        "result_hash": result_hash,
        "created_at": datetime.now()
    }
    
    created_result = db.create_computation_result(result)
    
    db.update_computation_request(request_id, {
        "status": "completed",
        "result_hash": result_hash,
        "updated_at": datetime.now()
    })
    
    if blockchain_service.is_connected() and current_user.wallet_address:
        dummy_private_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
        
        tx_hash = blockchain_service.submit_computation_result(
            request_id,
            result_hash,
            current_user.wallet_address,
            dummy_private_key
        )
        
        if tx_hash:
            db.update_computation_request(request_id, {"result_transaction_hash": tx_hash})
    
    return created_result

@router.get("/{request_id}/result", response_model=ComputationResult)
async def get_computation_result(request_id: str, current_user: User = Depends(get_current_active_user)):
    request = db.get_computation_request(request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computation request not found"
        )
    
    dataset = db.get_dataset(request["dataset_id"])
    if request["requester_id"] != current_user.id and dataset["owner_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this computation result"
        )
    
    result = db.get_computation_result_by_computation(request_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Computation result not found"
        )
    
    return result
