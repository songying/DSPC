"""
Analytics Router for Privacy Data Protocol

This module provides API endpoints for privacy-preserving analytics on browser history data.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import json
from typing import Dict, Any, List, Optional
import time

from ..auth import get_current_user
from ..models import User
from ..homomorphic_encryption import PrivacyPreservingComputation
from ..data_generator import generate_small_test_dataset

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

analysis_results = {}
analysis_status = {}

@router.post("/generate-dataset")
async def generate_dataset(
    background_tasks: BackgroundTasks,
    num_users: int = 100,
    events_per_user: int = 1000,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a synthetic browser history dataset for testing.
    
    This is a long-running task that will be executed in the background.
    """
    task_id = f"dataset_gen_{int(time.time())}"
    analysis_status[task_id] = {
        "status": "running",
        "message": f"Generating dataset with {num_users} users and {events_per_user} events per user",
        "progress": 0,
        "user_id": current_user.id
    }
    
    def generate_dataset_task():
        try:
            analysis_status[task_id]["message"] = "Starting dataset generation..."
            analysis_status[task_id]["progress"] = 10
            
            dataset = generate_small_test_dataset(
                num_users=num_users,
                events_per_user=events_per_user
            )
            
            analysis_status[task_id]["status"] = "completed"
            analysis_status[task_id]["message"] = "Dataset generation completed"
            analysis_status[task_id]["progress"] = 100
            analysis_status[task_id]["result"] = {
                "dataset_path": "browser_history_test_dataset.json",
                "num_users": num_users,
                "total_events": num_users * events_per_user,
                "date_range": dataset["metadata"]["date_range"]
            }
        except Exception as e:
            analysis_status[task_id]["status"] = "failed"
            analysis_status[task_id]["message"] = f"Dataset generation failed: {str(e)}"
            analysis_status[task_id]["progress"] = 0
    
    background_tasks.add_task(generate_dataset_task)
    
    return {
        "task_id": task_id,
        "status": "running",
        "message": f"Dataset generation started for {num_users} users"
    }

@router.post("/run-analysis")
async def run_analysis(
    background_tasks: BackgroundTasks,
    sample_size: int = 100,
    dataset_path: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Run privacy-preserving analysis on browser history data.
    
    This is a long-running task that will be executed in the background.
    """
    task_id = f"analysis_{int(time.time())}"
    analysis_status[task_id] = {
        "status": "running",
        "message": f"Starting analysis with sample size {sample_size}",
        "progress": 0,
        "user_id": current_user.id
    }
    
    def run_analysis_task():
        try:
            analysis_status[task_id]["message"] = "Initializing privacy-preserving computation..."
            analysis_status[task_id]["progress"] = 10
            
            dataset_file = dataset_path or "browser_history_test_dataset.json"
            
            if not os.path.exists(dataset_file):
                analysis_status[task_id]["message"] = "Dataset not found, generating a small test dataset..."
                analysis_status[task_id]["progress"] = 20
                generate_small_test_dataset(num_users=sample_size, events_per_user=1000)
            
            analysis_status[task_id]["message"] = "Running privacy-preserving analysis..."
            analysis_status[task_id]["progress"] = 30
            
            computation = PrivacyPreservingComputation(dataset_file)
            results = computation.run_full_analysis(sample_size=sample_size)
            
            analysis_status[task_id]["message"] = "Generating visualizations..."
            analysis_status[task_id]["progress"] = 70
            
            from ..visualize_results import create_visualizations
            visualization_files = create_visualizations(results)
            
            analysis_results[task_id] = results
            
            analysis_status[task_id]["status"] = "completed"
            analysis_status[task_id]["message"] = "Analysis completed successfully"
            analysis_status[task_id]["progress"] = 100
            analysis_status[task_id]["visualization_files"] = visualization_files
        except Exception as e:
            analysis_status[task_id]["status"] = "failed"
            analysis_status[task_id]["message"] = f"Analysis failed: {str(e)}"
            analysis_status[task_id]["progress"] = 0
    
    background_tasks.add_task(run_analysis_task)
    
    return {
        "task_id": task_id,
        "status": "running",
        "message": f"Analysis started with sample size {sample_size}"
    }

@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of a background task."""
    if task_id not in analysis_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if analysis_status[task_id]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    
    return analysis_status[task_id]

@router.get("/results/{task_id}")
async def get_analysis_results(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the results of a completed analysis task."""
    if task_id not in analysis_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if analysis_status[task_id]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these results")
    
    if analysis_status[task_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not yet completed")
    
    if task_id in analysis_results:
        return analysis_results[task_id]
    else:
        raise HTTPException(status_code=404, detail="Results not found")

@router.get("/visualization/{task_id}/{filename}")
async def get_visualization(
    task_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Get a visualization file from a completed analysis task."""
    if task_id not in analysis_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if analysis_status[task_id]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these visualizations")
    
    if analysis_status[task_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not yet completed")
    
    if "visualization_files" not in analysis_status[task_id]:
        raise HTTPException(status_code=404, detail="Visualization files not found")
    
    for file_path in analysis_status[task_id]["visualization_files"]:
        if os.path.basename(file_path) == filename:
            return FileResponse(file_path)
    
    raise HTTPException(status_code=404, detail="Visualization file not found")

@router.get("/available-visualizations/{task_id}")
async def get_available_visualizations(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a list of available visualization files for a completed analysis task."""
    if task_id not in analysis_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if analysis_status[task_id]["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these visualizations")
    
    if analysis_status[task_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis is not yet completed")
    
    if "visualization_files" not in analysis_status[task_id]:
        raise HTTPException(status_code=404, detail="Visualization files not found")
    
    return {
        "visualization_files": [
            {
                "filename": os.path.basename(file_path),
                "url": f"/analytics/visualization/{task_id}/{os.path.basename(file_path)}"
            }
            for file_path in analysis_status[task_id]["visualization_files"]
        ]
    }
