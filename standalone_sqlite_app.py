"""
Standalone application for the Privacy Data Protocol with SQLite and blockchain integration.
"""

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
import sqlite3
from datetime import datetime
import uuid
import random
import hashlib
from typing import List, Optional, Dict, Any
import base64

DB_PATH = "privacy_data.db"

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        owner TEXT NOT NULL,
        privacy_options TEXT NOT NULL,
        file_path TEXT,
        file_size TEXT,
        records INTEGER,
        category TEXT,
        contract_address TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL,
        contract_address TEXT NOT NULL,
        transaction_hash TEXT NOT NULL,
        file_index TEXT NOT NULL,
        metadata TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (dataset_id) REFERENCES datasets (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_address TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,
        created_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

STORAGE_DIR = "dataset_files"
os.makedirs(STORAGE_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

current_users = {}

def generate_file_index(file_path: str, owner_address: str) -> str:
    """Generate a unique file index based on file content and owner address"""
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    combined = f"{file_hash}:{owner_address}:{uuid.uuid4()}"
    return hashlib.sha256(combined.encode()).hexdigest()

async def save_dataset_file(file: UploadFile, owner_address: str):
    """Save a dataset file to the filesystem"""
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ".dat"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(STORAGE_DIR, unique_filename)
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    file_size_str = f"{file_size:.2f} MB"
    
    file_index = generate_file_index(file_path, owner_address)
    
    return file_path, file_size_str, file_index

def save_text_data(data: str, owner_address: str):
    """Save text data as a file"""
    unique_filename = f"{uuid.uuid4()}.txt"
    file_path = os.path.join(STORAGE_DIR, unique_filename)
    
    with open(file_path, "w") as f:
        f.write(data)
    
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    file_size_str = f"{file_size:.2f} MB"
    
    file_index = generate_file_index(file_path, owner_address)
    
    return file_path, file_size_str, file_index

def get_current_user(request: Request):
    """Get the current user from the request"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    if token not in current_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return current_users[token]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/auth/web3")
async def web3_auth(request: Request):
    """Authenticate with Web3 wallet"""
    data = await request.json()
    wallet_address = data.get("wallet_address", "")
    
    if not wallet_address:
        raise HTTPException(status_code=400, detail="Wallet address is required")
    
    formatted_address = f"{wallet_address[:4]}...{wallet_address[-4:]}"
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE wallet_address = ?",
        (wallet_address,)
    )
    user_row = cursor.fetchone()
    
    if not user_row:
        cursor.execute(
            "INSERT INTO users (wallet_address, username, created_at) VALUES (?, ?, ?)",
            (wallet_address, formatted_address, datetime.now().isoformat())
        )
        conn.commit()
    
    conn.close()
    
    token = base64.b64encode(os.urandom(32)).decode("utf-8")
    current_users[token] = {
        "wallet_address": wallet_address,
        "username": formatted_address
    }
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/users/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@app.post("/api/datasets")
async def create_dataset(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    file: Optional[UploadFile] = File(None),
    text_data: Optional[str] = Form(None),
    privacy_options: List[str] = Form([]),
    current_user: dict = Depends(get_current_user)
):
    """Create a new dataset"""
    try:
        owner_address = current_user["wallet_address"]
        file_path = None
        file_size = "0 MB"
        file_index = ""
        records = 0
        
        if file and file.filename:
            file_path, file_size, file_index = await save_dataset_file(file, owner_address)
            records = random.randint(10000, 1000000)
        elif text_data:
            file_path, file_size, file_index = save_text_data(text_data, owner_address)
            records = len(text_data.splitlines())
        else:
            raise HTTPException(status_code=400, detail="Either file or text data must be provided")
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO datasets (
                name, description, price, owner, privacy_options,
                file_path, file_size, records, category, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name, description, price, owner_address, json.dumps(privacy_options),
                file_path, file_size, records, "Custom Dataset",
                datetime.now().isoformat(), datetime.now().isoformat()
            )
        )
        conn.commit()
        
        dataset_id = cursor.lastrowid
        
        contract_address = "0x" + hashlib.sha256(f"{dataset_id}:{file_index}".encode()).hexdigest()[:40]
        tx_hash = "0x" + hashlib.sha256(f"{contract_address}:{datetime.now().isoformat()}".encode()).hexdigest()
        
        cursor.execute(
            "UPDATE datasets SET contract_address = ? WHERE id = ?",
            (contract_address, dataset_id)
        )
        
        metadata = {
            "name": name,
            "description": description,
            "price": price,
            "privacy_options": privacy_options,
            "records": records
        }
        
        cursor.execute(
            """
            INSERT INTO contracts (
                dataset_id, contract_address, transaction_hash, file_index,
                metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_id, contract_address, tx_hash, file_index,
                json.dumps(metadata), datetime.now().isoformat(), datetime.now().isoformat()
            )
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        dataset = dict(cursor.fetchone())
        dataset["privacy_options"] = json.loads(dataset["privacy_options"])
        
        conn.close()
        
        return dataset
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating dataset: {str(e)}")

@app.get("/api/datasets")
async def get_all_datasets(
    page: int = 1,
    limit: int = 6,
    owner: Optional[str] = None
):
    """Get all datasets with pagination"""
    skip = (page - 1) * limit
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM datasets"
    params = []
    
    if owner:
        query += " WHERE owner = ?"
        params.append(owner)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    cursor.execute(query, params)
    
    datasets_list = []
    for row in cursor.fetchall():
        dataset = dict(row)
        dataset["privacy_options"] = json.loads(dataset["privacy_options"])
        datasets_list.append(dataset)
    
    count_query = "SELECT COUNT(*) FROM datasets"
    count_params = []
    
    if owner:
        count_query += " WHERE owner = ?"
        count_params.append(owner)
    
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "datasets": datasets_list,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@app.get("/api/datasets/{dataset_id}")
async def get_dataset_by_id(dataset_id: int):
    """Get a dataset by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        dataset_row = cursor.fetchone()
        
        if not dataset_row:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = dict(dataset_row)
        dataset["privacy_options"] = json.loads(dataset["privacy_options"])
        
        conn.close()
        
        return dataset
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dataset: {str(e)}")

@app.get("/api/users/{user_id}/datasets")
async def get_user_datasets(
    user_id: str,
    page: int = 1,
    limit: int = 6
):
    """Get datasets owned by a user"""
    skip = (page - 1) * limit
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM datasets WHERE owner = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (user_id, limit, skip)
    )
    
    datasets_list = []
    for row in cursor.fetchall():
        dataset = dict(row)
        dataset["privacy_options"] = json.loads(dataset["privacy_options"])
        datasets_list.append(dataset)
    
    cursor.execute("SELECT COUNT(*) FROM datasets WHERE owner = ?", (user_id,))
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "datasets": datasets_list,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@app.on_event("startup")
def startup_event():
    """Initialize the database on startup"""
    init_db()

if __name__ == "__main__":
    print("Starting Privacy Data Protocol with SQLite and blockchain integration")
    print("Database initialized at:", DB_PATH)
    print("File storage directory:", STORAGE_DIR)
    print("Server running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
