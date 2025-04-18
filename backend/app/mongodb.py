"""
MongoDB integration for the Privacy Data Protocol.
This module handles the connection to MongoDB and provides functions for storing and retrieving data.
"""

import os
import pymongo
from datetime import datetime
from typing import Dict, List, Optional, Any

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB_NAME", "privacy_data_protocol")

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]

datasets_collection = db["datasets"]
contracts_collection = db["contracts"]
users_collection = db["users"]
computations_collection = db["computations"]

def init_db():
    """Initialize database with indexes"""
    datasets_collection.create_index("owner")
    datasets_collection.create_index("contract_address")
    contracts_collection.create_index("dataset_id")
    users_collection.create_index("wallet_address", unique=True)
    computations_collection.create_index("dataset_id")
    computations_collection.create_index("requester")

def store_dataset(
    name: str,
    description: str,
    price: float,
    owner: str,
    privacy_options: List[str],
    file_path: str,
    file_size: str,
    records: int,
    category: str,
    contract_address: Optional[str] = None
) -> str:
    """
    Store dataset information in MongoDB
    
    Args:
        name: Dataset name
        description: Dataset description
        price: Dataset price in ETH
        owner: Owner's wallet address
        privacy_options: List of privacy options
        file_path: Path to the dataset file
        file_size: Size of the dataset file
        records: Number of records in the dataset
        category: Dataset category
        contract_address: Ethereum smart contract address
        
    Returns:
        The ID of the inserted dataset
    """
    dataset = {
        "name": name,
        "description": description,
        "price": price,
        "owner": owner,
        "privacy_options": privacy_options,
        "file_path": file_path,
        "file_size": file_size,
        "records": records,
        "category": category,
        "contract_address": contract_address,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    result = datasets_collection.insert_one(dataset)
    return str(result.inserted_id)

def update_dataset_contract(dataset_id: str, contract_address: str) -> bool:
    """
    Update dataset with contract address
    
    Args:
        dataset_id: MongoDB ID of the dataset
        contract_address: Ethereum smart contract address
        
    Returns:
        True if update was successful, False otherwise
    """
    result = datasets_collection.update_one(
        {"_id": pymongo.ObjectId(dataset_id)},
        {"$set": {
            "contract_address": contract_address,
            "updated_at": datetime.now().isoformat()
        }}
    )
    
    return result.modified_count > 0

def store_contract_info(
    dataset_id: str,
    contract_address: str,
    transaction_hash: str,
    file_index: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Store smart contract information in MongoDB
    
    Args:
        dataset_id: MongoDB ID of the dataset
        contract_address: Ethereum smart contract address
        transaction_hash: Transaction hash of contract deployment
        file_index: Index of the file in the contract
        metadata: Additional metadata about the contract
        
    Returns:
        The ID of the inserted contract info
    """
    contract_info = {
        "dataset_id": dataset_id,
        "contract_address": contract_address,
        "transaction_hash": transaction_hash,
        "file_index": file_index,
        "metadata": metadata,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    result = contracts_collection.insert_one(contract_info)
    return str(result.inserted_id)

def get_dataset(dataset_id: str) -> Optional[Dict[str, Any]]:
    """
    Get dataset by ID
    
    Args:
        dataset_id: MongoDB ID of the dataset
        
    Returns:
        Dataset information or None if not found
    """
    try:
        dataset = datasets_collection.find_one({"_id": pymongo.ObjectId(dataset_id)})
        if dataset:
            dataset["_id"] = str(dataset["_id"])
        return dataset
    except:
        return None

def get_datasets(owner: Optional[str] = None, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
    """
    Get datasets, optionally filtered by owner
    
    Args:
        owner: Owner's wallet address
        limit: Maximum number of datasets to return
        skip: Number of datasets to skip (for pagination)
        
    Returns:
        List of datasets
    """
    query = {}
    if owner:
        query["owner"] = owner
    
    cursor = datasets_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    
    datasets = []
    for dataset in cursor:
        dataset["_id"] = str(dataset["_id"])
        datasets.append(dataset)
    
    return datasets

def get_contract_info(contract_address: str) -> Optional[Dict[str, Any]]:
    """
    Get contract information by contract address
    
    Args:
        contract_address: Ethereum smart contract address
        
    Returns:
        Contract information or None if not found
    """
    contract_info = contracts_collection.find_one({"contract_address": contract_address})
    if contract_info:
        contract_info["_id"] = str(contract_info["_id"])
    return contract_info

def get_dataset_by_contract(contract_address: str) -> Optional[Dict[str, Any]]:
    """
    Get dataset by contract address
    
    Args:
        contract_address: Ethereum smart contract address
        
    Returns:
        Dataset information or None if not found
    """
    dataset = datasets_collection.find_one({"contract_address": contract_address})
    if dataset:
        dataset["_id"] = str(dataset["_id"])
    return dataset

def count_datasets(owner: Optional[str] = None) -> int:
    """
    Count datasets, optionally filtered by owner
    
    Args:
        owner: Owner's wallet address
        
    Returns:
        Number of datasets
    """
    query = {}
    if owner:
        query["owner"] = owner
    
    return datasets_collection.count_documents(query)
