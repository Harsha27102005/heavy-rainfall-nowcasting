# backend/app/tasks/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.data_ingestion_service import DataIngestionService
from app.services.ml_service import MLModelService
from app.services.notification_service import NotificationService
import asyncio
from datetime import datetime

# Initialize services globally or pass during scheduler start
ml_service = None
notification_service = None
data_ingestion_service = None
scheduler = None

def start_scheduler(data_ingestion_svc_instance: DataIngestionService, ml_svc_instance: MLModelService):
    """
    Starts the APScheduler to run the data ingestion and nowcasting process periodically.
    """
    global ml_service, notification_service, data_ingestion_service, scheduler
    ml_service = ml_svc_instance
    notification_service = NotificationService() # Re-initialize if needed, or pass from main
    data_ingestion_service = data_ingestion_svc_instance # Pass the instance from main.py

    if scheduler is None:
        scheduler = AsyncIOScheduler()
        # [cite_start]Schedule the task to run every 10 minutes, as per radar data temporal resolution [cite: 78]
        scheduler.add_job(
            data_ingestion_service.process_new_radar_data,
            'interval',
            minutes=10,
            id='nowcasting_job',
            next_run_time=datetime.now() # Run immediately on startup
        )
        scheduler.start()
        print("Background nowcasting scheduler started. Job will run every 10 minutes.")
    else:
        print("Scheduler already running.")

# You might also want a function to stop the scheduler on app shutdown
def stop_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown()
        print("Background nowcasting scheduler stopped.")