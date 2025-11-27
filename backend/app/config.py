# backend/app/config.py
import os
from dotenv import load_dotenv
from pydantic import EmailStr

# Load environment variables from .env file
load_dotenv()

class Settings:
    # MongoDB Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "nowcasting_db")
    
    # Security (for JWT in auth)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_super_secret_key_change_me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email settings for OTP
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "Heavy Rainfall Nowcasting")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"

    # ML Model Paths
    ML_MODELS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml_models")

    # Heavy Rainfall Threshold
    HEAVY_RAINFALL_THRESHOLD_MM_H: float = float(os.getenv("HEAVY_RAINFALL_THRESHOLD_MM_H", "30.0")) # From paper [cite: 330]

    # MCS Types for models
    MCS_TYPES = ["CC", "MCC", "SLD", "SLP", "MSL", "ALL"]
    MCS_TYPES_REGRESSION = ["CC", "MSL"] # Based on paper's regression analysis [cite: 113]

    # Variables used in models (for reference in service)
    RADAR_VARIABLES = [
        "Rmj", "Rmn", "Theta", "MeanZ", "Area", "Volume", "Top", "Base",
        "MaxZ", "MaxZhg", "AvgVIL", "MaxVIL", "U", "V", "Direction",
        "MeanRR_prev", "Top10%_prev" # 'prev' to distinguish from current output
    ] # From paper, Table I [cite: 108]

    TOPOGRAPHIC_VARIABLES = [
        "dist_to_sea", "elevation", "aspect", "roughness", "slope"
    ] # From paper [cite: 133]

    # Notification Settings
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "False").lower() == "true"
    ENABLE_SMS_NOTIFICATIONS: bool = os.getenv("ENABLE_SMS_NOTIFICATIONS", "False").lower() == "true"
    # API keys for notification services would go here as well, e.g., TWILIO_ACCOUNT_SID

    # Dummy path for initial radar data (will be replaced by live ingestion)
    LATEST_RADAR_DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "dummy_radar_composite.npy")

    # [cite_start]Variable Transformations as per paper Table I [cite: 108]
    VARIABLE_TRANSFORMATIONS = {
        "Rmj": {"multiply": 100, "log_transform": True},
        "Rmn": {"multiply": 100, "log_transform": True},
        "Theta": {"multiply": 100, "log_transform": False},
        "MeanZ": {"multiply": 100, "log_transform": True},
        "Area": {"multiply": 10, "log_transform": True},
        "Volume": {"multiply": 10, "log_transform": True},
        "Top": {"multiply": 100, "log_transform": False},
        "Base": {"multiply": 100, "log_transform": False},
        "MaxZ": {"multiply": 100, "log_transform": True},
        "MaxZhg": {"multiply": 100, "log_transform": False},
        "AvgVIL": {"multiply": 100000, "log_transform": True},
        "MaxVIL": {"multiply": 100000, "log_transform": True},
        "U": {"multiply": 100000, "log_transform": False},
        "V": {"multiply": 100000, "log_transform": False},
        "Direction": {"multiply": 100000, "log_transform": False},
        # [cite_start]Output variables also transformed in paper [cite: 108]
        "MeanRR": {"multiply": 100, "log_transform": True},
        "Top10%": {"multiply": 100, "log_transform": True},
    }


settings = Settings()