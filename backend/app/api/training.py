# backend/app/api/training.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
from typing import List, Dict
import pandas as pd
import numpy as np
from PIL import Image
import io
import asyncio
from app.database import sync_datasets_collection, sync_training_status_collection
from app.api.auth import get_current_admin_user
from app.services.ml_service import MLModelService
from app.config import settings
from pydantic import BaseModel
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

TRAINING_DATA_DIR = "training_data"
ALLOWED_EXTENSIONS = {
    "radar_data": [".csv", ".xlsx", ".xls", ".json", ".npy"],
    "labels": [".csv", ".xlsx", ".xls", ".json"]
}

def ensure_training_dir():
    os.makedirs(TRAINING_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(TRAINING_DATA_DIR, "radar_data"), exist_ok=True)
    os.makedirs(os.path.join(TRAINING_DATA_DIR, "labels"), exist_ok=True)

def validate_file_extension(filename: str, file_type: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, [])

async def run_real_training(training_id: str):
    """Runs the real model training in the background."""
    try:
        ml_service = MLModelService()
        
        radar_data = list(sync_datasets_collection.find({"file_type": "radar_training_data"}))
        labels_data = list(sync_datasets_collection.find({"file_type": "training_labels"}))
        
        radar_paths = [doc["file_path"] for doc in radar_data]
        labels_paths = [doc["file_path"] for doc in labels_data]
        
        ml_service.train_models(radar_paths, labels_paths)
        
        sync_training_status_collection.update_one(
            {"_id": ObjectId(training_id)},
            {"$set": {"status": "completed", "completed_at": datetime.utcnow()}}
        )
        print(f"Training {training_id} completed!")
    except Exception as e:
        print(f"Training {training_id} failed: {e}")
        sync_training_status_collection.update_one(
            {"_id": ObjectId(training_id)},
            {"$set": {"status": "failed", "completed_at": datetime.utcnow(), "error_message": str(e)}}
        )

@router.post("/upload-radar-data")
async def upload_radar_training_data(
    file: UploadFile = File(...),
    current_user = Depends(get_current_admin_user)
):
    """Upload radar data for model training"""
    ensure_training_dir()
    
    if not validate_file_extension(file.filename, "radar_data"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: CSV, Excel, JSON, NPY"
        )
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"radar_{timestamp}_{file.filename}"
    file_path = os.path.join(TRAINING_DATA_DIR, "radar_data", filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    dataset_doc = {
        "filename": filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_type": "radar_training_data",
        "uploaded_by": current_user["email"],
        "uploaded_at": datetime.utcnow(),
        "file_size": os.path.getsize(file_path),
        "status": "uploaded"
    }
    
    result = sync_datasets_collection.insert_one(dataset_doc)
    
    return JSONResponse({
        "message": "Radar training data uploaded successfully",
        "dataset_id": str(result.inserted_id),
        "filename": filename
    })

@router.post("/upload-labels")
async def upload_training_labels(
    file: UploadFile = File(...),
    current_user = Depends(get_current_admin_user)
):
    """Upload training labels for model training"""
    ensure_training_dir()
    
    if not validate_file_extension(file.filename, "labels"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: CSV, Excel, JSON"
        )
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"labels_{timestamp}_{file.filename}"
    file_path = os.path.join(TRAINING_DATA_DIR, "labels", filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    dataset_doc = {
        "filename": filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_type": "training_labels",
        "uploaded_by": current_user["email"],
        "uploaded_at": datetime.utcnow(),
        "file_size": os.path.getsize(file_path),
        "status": "uploaded"
    }
    
    result = sync_datasets_collection.insert_one(dataset_doc)
    
    return JSONResponse({
        "message": "Training labels uploaded successfully",
        "dataset_id": str(result.inserted_id),
        "filename": filename
    })

@router.post("/start-training")
async def start_model_training(
    current_user = Depends(get_current_admin_user)
):
    """Start the model training process"""
    radar_data = list(sync_datasets_collection.find({"file_type": "radar_training_data"}))
    labels_data = list(sync_datasets_collection.find({"file_type": "training_labels"}))
    
    if not radar_data or not labels_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training data not found. Please upload radar data and labels first."
        )
    
    training_status = {
        "status": "training",
        "started_at": datetime.utcnow(),
        "started_by": current_user["email"],
        "radar_data_count": len(radar_data),
        "labels_data_count": len(labels_data)
    }
    
    sync_training_status_collection.delete_many({})
    result = sync_training_status_collection.insert_one(training_status)
    
    asyncio.create_task(run_real_training(str(result.inserted_id)))
    
    return JSONResponse({
        "message": "Model training started",
        "training_id": str(result.inserted_id),
        "status": "training"
    })

@router.get("/training-status")
async def get_training_status(
    current_user = Depends(get_current_admin_user)
):
    """Get the current training status"""
    status_doc = sync_training_status_collection.find_one({}, sort=[("started_at", -1)])
    
    if not status_doc:
        return JSONResponse({
            "status": "not_started",
            "message": "No training has been started"
        })
    
    status_doc["id"] = str(status_doc["_id"])
    del status_doc["_id"]
    return status_doc

@router.get("/training-data-status")
async def get_training_data_status(
    current_user = Depends(get_current_admin_user)
):
    """Check if training data is available"""
    radar_data = list(sync_datasets_collection.find({"file_type": "radar_training_data"}))
    labels_data = list(sync_datasets_collection.find({"file_type": "training_labels"}))
    
    return JSONResponse({
        "radar_data_available": len(radar_data) > 0,
        "labels_data_available": len(labels_data) > 0,
        "radar_data_count": len(radar_data),
        "labels_data_count": len(labels_data),
        "ready_for_training": len(radar_data) > 0 and len(labels_data) > 0
    })

class MonitoringRequest(BaseModel):
    admin_email: str
    admin_phone: str

@router.post("/start-monitoring")
async def start_real_time_monitoring(
    monitoring_request: MonitoringRequest,
    current_user = Depends(get_current_admin_user)
):
    """Start real-time storm cell monitoring"""
    training_status = sync_training_status_collection.find_one({}, sort=[("started_at", -1)])
    
    if not training_status or training_status.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Models not trained yet. Please complete training first."
        )
    
    monitoring_status = {
        "status": "monitoring",
        "started_at": datetime.utcnow(),
        "started_by": current_user["email"],
        "admin_email": monitoring_request.admin_email,
        "admin_phone": monitoring_request.admin_phone
    }
    
    sync_training_status_collection.update_one(
        {"_id": ObjectId(training_status["_id"])},
        {"$set": {"monitoring_status": monitoring_status}}
    )
    
    try:
        from app.services.notification_service import NotificationService
        notification_service = NotificationService()
        await notification_service.send_monitoring_start_notification(monitoring_status)
    except Exception as e:
        print(f"Failed to send monitoring start notification: {e}")
    
    return JSONResponse({
        "message": "Real-time monitoring started",
        "status": "monitoring",
        "admin_email": monitoring_request.admin_email,
        "admin_phone": monitoring_request.admin_phone
    }) 

@router.delete("/delete-dataset/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    current_user = Depends(get_current_admin_user)
):
    """Delete an uploaded dataset"""
    try:
        dataset = sync_datasets_collection.find_one({"_id": ObjectId(dataset_id)})
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        try:
            if os.path.exists(dataset["file_path"]):
                os.remove(dataset["file_path"])
                logger.info(f"Deleted file: {dataset['file_path']}")
        except Exception as e:
            logger.warning(f"Failed to delete file {dataset['file_path']}: {e}")
        
        result = sync_datasets_collection.delete_one({"_id": ObjectId(dataset_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete dataset from database"
            )
        
        return JSONResponse({
            "message": "Dataset deleted successfully",
            "dataset_id": dataset_id,
            "filename": dataset["filename"]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dataset {dataset_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataset: {str(e)}"
        )

@router.get("/datasets", response_model=List[Dict])
async def get_uploaded_datasets(
    current_user = Depends(get_current_admin_user)
):
    """Get list of uploaded datasets"""
    try:
        datasets = list(sync_datasets_collection.find({
            "uploaded_by": current_user["email"]
        }).sort("uploaded_at", -1))
        
        for dataset in datasets:
            dataset["id"] = str(dataset["_id"])
            del dataset["_id"]
        
        return datasets
        
    except Exception as e:
        logger.error(f"Error fetching datasets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch datasets"
        )