# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi_mail import ConnectionConfig, FastMail

from app.api import nowcasting, warnings, auth, training, crowdsource # Import your API routers
from app.config import settings
from app.services.ml_service import MLModelService
from app.services.notification_service import NotificationService
from app.services.data_ingestion_service import DataIngestionService
from app.tasks.scheduler import start_scheduler, stop_scheduler # For background task scheduling

from app.email_conf import conf # Import from dedicated config file

# Initialize services globally
ml_service_instance = MLModelService()
notification_service_instance = NotificationService()
data_ingestion_service_instance = DataIngestionService(
    ml_service=ml_service_instance,
    notification_service=notification_service_instance
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models, start background scheduler
    print("Application startup initiated...")
    
    ml_service_instance.load_models() # Load all ML models into memory

    # Start background data ingestion/nowcasting scheduler
    start_scheduler(data_ingestion_service_instance, ml_service_instance)

    print("Application startup complete. Scheduler running.")
    yield # Application runs

    # Shutdown: Clean up resources
    stop_scheduler() # Stop background scheduler
    print("Application shutdown complete.")

app = FastAPI(
    title="Heavy Rainfall Nowcasting API",
    description="API for real-time heavy rainfall nowcasting, storm cell prediction, and early warnings.",
    version="1.0.0",
    lifespan=lifespan # Use lifespan to manage startup/shutdown tasks
)

# Configure CORS middleware
origins = [
    "http://localhost:3000",  # Your React frontend's local development address
    # Add your Netlify URL here once deployed, e.g., "https://your-nowcasting-app.netlify.app"
    # For production, be more specific with origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(nowcasting.router, prefix="/nowcast", tags=["Nowcasting"])
app.include_router(warnings.router, prefix="/warnings", tags=["Warnings"])
app.include_router(training.router, prefix="/training", tags=["Model Training"])
app.include_router(crowdsource.router, prefix="/crowdsource", tags=["Crowdsourcing"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Heavy Rainfall Nowcasting API! Access /docs for API documentation."}