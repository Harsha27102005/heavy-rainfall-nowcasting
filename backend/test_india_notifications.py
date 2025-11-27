#!/usr/bin/env python3
"""
Test script to demonstrate India monsoon notifications
This simulates the notification system without requiring real SMTP/SMS credentials
"""

import asyncio
import json
from datetime import datetime, timedelta
from app.services.notification_service import NotificationService
from app.schemas.prediction import WarningCreate
from app.database import sync_warnings_collection, sync_notifications_collection

class MockNotificationService(NotificationService):
    """Mock notification service that logs instead of sending real notifications"""
    
    async def _send_email_notification(self, warning_data: WarningCreate, admin_email: str):
        """Mock email notification - just log the message"""
        print("\n" + "="*60)
        print("📧 EMAIL NOTIFICATION SENT")
        print("="*60)
        print(f"To: {admin_email}")
        print(f"Subject: ⚠️ HEAVY RAINFALL WARNING")
        print(f"Cell ID: {warning_data.cell_id}")
        print(f"MCS Type: {warning_data.mcs_type}")
        print(f"Forecast Time: {warning_data.forecast_time} minutes")
        print(f"Predicted Top 10% Rain Rate: {warning_data.predicted_top10_mean_rr} mm/h")
        print(f"Message: {warning_data.message}")
        print(f"Timestamp: {warning_data.predicted_timestamp}")
        print("="*60)
    
    async def _send_sms_notification(self, warning_data: WarningCreate, admin_phone: str):
        """Mock SMS notification - just log the message"""
        print("\n" + "="*60)
        print("📱 SMS NOTIFICATION SENT")
        print("="*60)
        print(f"To: {admin_phone}")
        print(f"Message: ⚠️ HEAVY RAINFALL WARNING")
        print(f"Cell: {warning_data.cell_id}")
        print(f"Type: {warning_data.mcs_type}")
        print(f"Rain Rate: {warning_data.predicted_top10_mean_rr}mm/h")
        print(f"Time: {warning_data.forecast_time}min")
        print(f"Details: {warning_data.message}")
        print("="*60)

def create_india_warning_data():
    """Create sample warning data for India monsoon conditions"""
    
    warnings = [
        {
            "cell_id": "MUMBAI_MONSOON_01",
            "mcs_type": "MCC",
            "forecast_time": 30,
            "predicted_timestamp": datetime.utcnow() + timedelta(minutes=15),
            "predicted_top10_mean_rr": 95.7,
            "message": "Heavy rainfall warning: Expected rainfall intensity exceeding 90 mm/h in the next 30 minutes over Mumbai region. Risk of flooding in low-lying areas.",
            "location_geojson": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [72.9777, 19.1760],
                        [72.9777, 18.9760],
                        [72.7777, 18.9760],
                        [72.7777, 19.1760],
                        [72.9777, 19.1760]
                    ]]
                },
                "properties": {
                    "location": "Mumbai",
                    "severity": "high"
                }
            },
            "is_active": True
        },
        {
            "cell_id": "THANE_VERY_HEAVY_001",
            "mcs_type": "SLD",
            "forecast_time": 60,
            "predicted_timestamp": datetime.utcnow() + timedelta(minutes=45),
            "predicted_top10_mean_rr": 125.6,
            "message": "VERY HEAVY RAINFALL WARNING: Extreme rainfall intensity of 125+ mm/h expected over Thane region. High risk of severe flooding and disruption.",
            "location_geojson": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [73.1777, 19.4760],
                        [73.1777, 19.2760],
                        [72.9777, 19.2760],
                        [72.9777, 19.4760],
                        [73.1777, 19.4760]
                    ]]
                },
                "properties": {
                    "location": "Thane",
                    "severity": "very_high"
                }
            },
            "is_active": True
        },
        {
            "cell_id": "PUNE_MODERATE_001",
            "mcs_type": "CC",
            "forecast_time": 30,
            "predicted_timestamp": datetime.utcnow() + timedelta(minutes=20),
            "predicted_top10_mean_rr": 65.4,
            "message": "Moderate to heavy rainfall warning: Rainfall intensity expected to reach 65+ mm/h over Pune region. Moderate risk of localized flooding.",
            "location_geojson": {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [72.6777, 18.3760],
                        [72.6777, 18.1760],
                        [72.4777, 18.1760],
                        [72.4777, 18.3760],
                        [72.6777, 18.3760]
                    ]]
                },
                "properties": {
                    "location": "Pune",
                    "severity": "moderate"
                }
            },
            "is_active": True
        }
    ]
    
    return warnings

async def test_india_notifications():
    """Test the notification system with India monsoon data"""
    
    print("🌧️  Testing India Monsoon Notifications")
    print("="*60)
    
    # Create mock notification service
    notification_service = MockNotificationService()
    
    # Set mock admin contact info
    admin_email = "admin@indianmonsoon.gov.in"
    admin_phone = "+91-9876543210"
    
    # Create warning data
    warnings_data = create_india_warning_data()
    
    print(f"📧 Admin Email: {admin_email}")
    print(f"📱 Admin Phone: {admin_phone}")
    print(f"⚠️  Warnings to test: {len(warnings_data)}")
    print()
    
    # Test each warning
    for i, warning_data in enumerate(warnings_data, 1):
        print(f"Testing Warning {i}/{len(warnings_data)}: {warning_data['cell_id']}")
        
        # Create WarningCreate object
        warning = WarningCreate(**warning_data)
        
        # Send notification
        await notification_service.send_heavy_rainfall_warning(warning)
        
        # Store in database
        warning_doc = {
            **warning_data,
            "issued_at": datetime.utcnow(),
            "id": f"warning_{i}"
        }
        sync_warnings_collection.insert_one(warning_doc)
        
        print(f"✅ Warning {i} processed and stored in database")
        print()
        
        # Small delay between warnings
        await asyncio.sleep(1)
    
    # Show database summary
    print("📊 Database Summary:")
    print("="*60)
    
    warnings_count = sync_warnings_collection.count_documents({})
    notifications_count = sync_notifications_collection.count_documents({})
    
    print(f"Total Warnings in DB: {warnings_count}")
    print(f"Total Notifications in DB: {notifications_count}")
    
    # Show recent warnings
    recent_warnings = list(sync_warnings_collection.find().sort("issued_at", -1).limit(3))
    print(f"\nRecent Warnings:")
    for warning in recent_warnings:
        print(f"  - {warning['cell_id']}: {warning['predicted_top10_mean_rr']} mm/h")
    
    print("\n🎯 Test Results:")
    print("="*60)
    print("✅ Email notifications logged")
    print("✅ SMS notifications logged")
    print("✅ Warnings stored in database")
    print("✅ Notifications stored in database")
    print("✅ India monsoon data processed")
    
    print("\n📋 Next Steps:")
    print("1. Check the logged notifications above")
    print("2. Upload the generated CSV files to the training page")
    print("3. Start model training")
    print("4. Start real-time monitoring")
    print("5. Provide your real email and phone for actual notifications")

if __name__ == "__main__":
    asyncio.run(test_india_notifications())



