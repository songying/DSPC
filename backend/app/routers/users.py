from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from typing import List, Dict, Any
from eth_account.messages import encode_defunct
from web3 import Web3

from ..models import User, UserCreate, UserResponse, Token, WalletLoginRequest
from ..database import db
from ..auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from ..blockchain import blockchain_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    existing_user = db.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    wallet = blockchain_service.create_wallet()
    
    hashed_password = get_password_hash(user.password)
    
    user_data = user.dict()
    user_data["password"] = hashed_password
    user_data["wallet_address"] = wallet["address"]
    user_data["created_at"] = datetime.now()
    
    created_user = db.create_user(user_data)
    
    response_user = created_user.copy()
    response_user.pop("password", None)
    
    return response_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me/wallet", response_model=UserResponse)
async def update_wallet_address(wallet_address: str, current_user: User = Depends(get_current_active_user)):
    user_id = current_user.id
    updated_user = db.update_user(user_id, {"wallet_address": wallet_address})
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user.pop("password", None)
    
    return updated_user

@router.post("/wallet-login", response_model=Token)
async def login_with_wallet(wallet_data: WalletLoginRequest):
    try:
        message = wallet_data.message
        signature = wallet_data.signature
        wallet_address = wallet_data.wallet_address
        
        is_valid = blockchain_service.verify_signature(message, signature, wallet_address)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.get_user_by_wallet_address(wallet_address)
        
        if not user:
            username = f"{wallet_address}"
            email = f"wallet_{wallet_address[:8]}@example.com"  # Placeholder email
            
            existing_user = db.get_user_by_username(username)
            if existing_user:
                username = f"{wallet_address}_{int(datetime.now().timestamp())}"
            
            import secrets
            password = secrets.token_hex(16)
            hashed_password = get_password_hash(password)
            
            user_data = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "wallet_address": wallet_address,
                "created_at": datetime.now()
            }
            
            user = db.create_user(user_data)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
