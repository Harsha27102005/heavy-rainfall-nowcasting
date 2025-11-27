# backend/app/services/notification_service.py
from app.schemas.prediction import WarningCreate
from app.database import sync_notifications_collection
from datetime import datetime
from app.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import requests

class NotificationService:
    def __init__(self):
        # SMTP settings
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Twilio settings
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Default admin contact (fallback)
        self.admin_email = os.getenv("ADMIN_EMAIL", "admin@nowcasting.com")
        self.admin_phone = os.getenv("ADMIN_PHONE")

    def get_admin_contact_info(self):
        """Get admin contact info from monitoring status or fallback to environment variables"""
        try:
            from app.database import sync_training_status_collection
            training_status = sync_training_status_collection.find_one({}, sort=[("started_at", -1)])
            
            if training_status and training_status.get("monitoring_status"):
                monitoring_status = training_status.get("monitoring_status", {})
                admin_email = monitoring_status.get("admin_email", self.admin_email)
                admin_phone = monitoring_status.get("admin_phone", self.admin_phone)
                return admin_email, admin_phone
        except Exception as e:
            print(f"Error getting admin contact info: {e}")
        
        return self.admin_email, self.admin_phone

    async def send_heavy_rainfall_warning(self, warning_data: WarningCreate):
        print(f"Attempting to send notification for Warning ID: {warning_data.cell_id}")
        
        # Get dynamic admin contact info
        admin_email, admin_phone = self.get_admin_contact_info()
        
        # 1. Store notification record in database
        db_notification = {
            "warning_id": warning_data.cell_id,
            "message": warning_data.message,
            "channel": "email_sms",
            "status": "pending",
            "timestamp": datetime.utcnow()
        }
        
        sync_notifications_collection.insert_one(db_notification)
        
        # 2. Send email notification
        notification_successful = False
        if settings.ENABLE_EMAIL_NOTIFICATIONS and self.smtp_username and self.smtp_password:
            try:
                await self._send_email_notification(warning_data, admin_email)
                notification_successful = True
                print(f"Email notification sent successfully for warning {warning_data.cell_id}")
            except Exception as e:
                print(f"Failed to send email: {e}")
                sync_notifications_collection.update_one(
                    {"warning_id": warning_data.cell_id},
                    {"$set": {"status": "failed_email"}}
                )
        
        # 3. Send SMS notification
        if settings.ENABLE_SMS_NOTIFICATIONS and self.twilio_account_sid and self.twilio_auth_token:
            try:
                await self._send_sms_notification(warning_data, admin_phone)
                notification_successful = True
                print(f"SMS notification sent successfully for warning {warning_data.cell_id}")
            except Exception as e:
                print(f"Failed to send SMS: {e}")
                sync_notifications_collection.update_one(
                    {"warning_id": warning_data.cell_id},
                    {"$set": {"status": "failed_sms"}}
                )
        
        # 4. Update notification status
        if notification_successful:
            sync_notifications_collection.update_one(
                {"warning_id": warning_data.cell_id},
                {"$set": {"status": "sent"}}
            )
        else:
            sync_notifications_collection.update_one(
                {"warning_id": warning_data.cell_id},
                {"$set": {"status": "failed_no_channel_enabled"}}
            )
        
        print(f"Notification record updated for warning {warning_data.cell_id}")

    async def _send_email_notification(self, warning_data: WarningCreate, admin_email: str):
        """Send email notification using SMTP"""
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = admin_email
        msg['Subject'] = "⚠️ HEAVY RAINFALL WARNING"
        
        body = f"""
        HEAVY RAINFALL WARNING
        
        Cell ID: {warning_data.cell_id}
        MCS Type: {warning_data.mcs_type}
        Forecast Time: {warning_data.forecast_time} minutes
        Predicted Top 10% Rain Rate: {warning_data.predicted_top_10_rain_rate} mm/h
        Predicted Timestamp: {warning_data.predicted_timestamp}
        Message: {warning_data.message}
        
        This warning was issued at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        
        Please take necessary precautions and monitor the situation.
        
        ---
        Heavy Rainfall Nowcasting System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)

    async def _send_sms_notification(self, warning_data: WarningCreate, admin_phone: str):
        """Send SMS notification using Twilio"""
        if not admin_phone:
            raise Exception("Admin phone number not configured")
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
        
        message = f"""⚠️ HEAVY RAINFALL WARNING
Cell: {warning_data.cell_id}
Type: {warning_data.mcs_type}
Rain Rate: {warning_data.predicted_top_10_rain_rate}mm/h
Time: {warning_data.forecast_time}min
{warning_data.message}"""
        
        data = {
            'From': self.twilio_phone_number,
            'To': admin_phone,
            'Body': message
        }
        
        response = requests.post(url, data=data, auth=(self.twilio_account_sid, self.twilio_auth_token))
        
        if response.status_code != 201:
            raise Exception(f"Twilio API error: {response.text}")

    async def send_training_completion_notification(self, training_status: dict):
        """Send notification when model training is completed"""
        admin_email, _ = self.get_admin_contact_info()
        
        if settings.ENABLE_EMAIL_NOTIFICATIONS and self.smtp_username and self.smtp_password:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.smtp_username
                msg['To'] = admin_email
                msg['Subject'] = "✅ Model Training Completed"

                body = f"""
                MODEL TRAINING COMPLETED
                
                Training started by: {training_status.get('started_by', 'Unknown')}
                Started at: {training_status.get('started_at', 'Unknown')}
                Radar data files: {training_status.get('radar_data_count', 0)}
                Labels files: {training_status.get('labels_data_count', 0)}
                
                The models are now ready for real-time monitoring.
                
                ---
                Heavy Rainfall Nowcasting System
                """

                msg.attach(MIMEText(body, 'plain'))

                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
                    
                print("Training completion email sent successfully")
            except Exception as e:
                print(f"Failed to send training completion email: {e}")

    async def send_monitoring_start_notification(self, monitoring_status: dict):
        """Send notification when real-time monitoring starts"""
        admin_email, _ = self.get_admin_contact_info()
        
        if settings.ENABLE_EMAIL_NOTIFICATIONS and self.smtp_username and self.smtp_password:
            try:
                msg = MIMEMultipart()
                msg['From'] = self.smtp_username
                msg['To'] = admin_email
                msg['Subject'] = "🚀 Real-time Monitoring Started"

                body = f"""
                REAL-TIME MONITORING STARTED
                
                Monitoring started by: {monitoring_status.get('started_by', 'Unknown')}
                Started at: {monitoring_status.get('started_at', 'Unknown')}
                Admin Email: {monitoring_status.get('admin_email', 'Not provided')}
                Admin Phone: {monitoring_status.get('admin_phone', 'Not provided')}
                
                The system is now actively monitoring for storm cells and heavy rainfall events.
                You will receive alerts via email and SMS when warnings are issued.
                
                ---
                Heavy Rainfall Nowcasting System
                """

                msg.attach(MIMEText(body, 'plain'))

                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
                    
                print("Monitoring start email sent successfully")
            except Exception as e:
                print(f"Failed to send monitoring start email: {e}")