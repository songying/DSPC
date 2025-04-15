from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

class DataType(str, Enum):
    PERSONAL = "personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    BEHAVIORAL = "behavioral"
    OTHER = "other"

class ComputationType(str, Enum):
    ANALYSIS = "analysis"
    MACHINE_LEARNING = "machine_learning"
    STATISTICAL = "statistical"
    CUSTOM = "custom"

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    password: str
    wallet_address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True
        
class UserResponse(UserBase):
    id: str
    wallet_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class DatasetBase(BaseModel):
    name: str
    description: str
    data_type: DataType
    price: float
    terms_of_use: str
    supports_homomorphic: bool = False
    supports_zk_proof: bool = False
    supports_third_party: bool = False
    
class DatasetCreate(DatasetBase):
    encrypted_data: str
    encryption_key: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None

class Dataset(DatasetBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_available: bool = True
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    
    class Config:
        orm_mode = True

class ComputationRequestBase(BaseModel):
    dataset_id: str
    computation_type: ComputationType
    algorithm_details: Dict[str, Any]
    
class ComputationRequestCreate(ComputationRequestBase):
    pass

class ComputationRequest(ComputationRequestBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    transaction_hash: Optional[str] = None
    result_hash: Optional[str] = None
    
    class Config:
        orm_mode = True

class ComputationResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    computation_id: str
    encrypted_result: str
    result_hash: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class WalletLoginRequest(BaseModel):
    wallet_address: str
    message: str
    signature: str
