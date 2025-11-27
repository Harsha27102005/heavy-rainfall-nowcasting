# backend/app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.config import settings

# MongoDB client for async operations
async_client = AsyncIOMotorClient(settings.MONGODB_URL)
database = async_client[settings.MONGODB_DB_NAME]
db = database

async def get_db():
    return db

# MongoDB client for sync operations
sync_client = MongoClient(settings.MONGODB_URL)
sync_database = sync_client[settings.MONGODB_DB_NAME]

# Collections
users_collection = database.users
predictions_collection = database.predictions
warnings_collection = database.warnings
notifications_collection = database.notifications
datasets_collection = database.datasets
training_status_collection = database.training_status # Can keep for backward compatibility or migrate to models
storm_cells_collection = database.storm_cells
models_collection = database.models
variable_importance_collection = database.variable_importance
crowdsource_reports_collection = database.crowdsource_reports

# Sync collections
sync_users_collection = sync_database.users
sync_predictions_collection = sync_database.predictions
sync_warnings_collection = sync_database.warnings
sync_notifications_collection = sync_database.notifications
sync_datasets_collection = sync_database.datasets
sync_training_status_collection = sync_database.training_status
sync_storm_cells_collection = sync_database.storm_cells
sync_models_collection = sync_database.models
sync_variable_importance_collection = sync_database.variable_importance