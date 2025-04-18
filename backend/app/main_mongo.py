"""
Main application for the Privacy Data Protocol with MongoDB and blockchain integration.
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json

from .auth import get_current_user
from .mongodb import init_db
from .routers import datasets_mongo

app = FastAPI(title="Privacy Data Protocol API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

app.include_router(datasets_mongo.router)

static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return {"message": "Privacy Data Protocol API is running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/users/me")
def get_current_user_info(current_user = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
