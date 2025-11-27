"""
Test Email Alert Script

This script sends a test heavy rainfall warning email to verify 
that the email notification system is working correctly.

Usage:
    python test_email_alert.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.notification_service import NotificationService
from app.schemas.prediction import WarningCreate
from datetime import datetime, timedelta, UTC

async def send_test_email():
    """Send a test heavy rainfall warning email"""
    
    print("=" * 60)
    print("🌧️  HEAVY RAINFALL ALERT - EMAIL TEST")
    print("=" * 60)
    print()
    
    # Create notification service
    notification_service = NotificationService()
    
    # Create test warning data
    test_warning = WarningCreate(
        cell_id="TEST_MUMBAI_001",
        mcs_type="MCC",
        forecast_time=30,
        predicted_timestamp=datetime.now(UTC) + timedelta(minutes=30),
        predicted_top10_mean_rr=250.5,  # Using alias name
        message="⚠️ Heavy rainfall predicted for Mumbai! Predicted Top 10% Mean Rain Rate: 250.5 mm/h",
        location_geojson={
            "type": "Polygon",
            "coordinates": [
                [
                    [72.7777, 18.9760],
                    [72.9777, 18.9760],
                    [72.9777, 19.1760],
                    [72.7777, 19.1760],
                    [72.7777, 18.9760]
                ]
            ]
        }
    )
    
    print("📧 Test Warning Details:")
    print(f"   Cell ID: {test_warning.cell_id}")
    print(f"   MCS Type: {test_warning.mcs_type}")
    print(f"   Forecast Time: {test_warning.forecast_time} minutes")
    print(f"   Predicted Rain Rate: 250.5 mm/h")
    print(f"   Expected At: {test_warning.predicted_timestamp}")
    print()
    
    print("📤 Sending test email...")
    
    try:
        # Send the email
        await notification_service.send_heavy_rainfall_warning(test_warning)
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Test email sent successfully!")
        print("=" * 60)
        print()
        print("📬 Check your email inbox (and spam folder)")
        print("   You should receive an email with:")
        print("   - Subject: ⚠️ Heavy Rainfall Warning - TEST_MUMBAI_001")
        print("   - Details about the predicted heavy rainfall")
        print("   - Location: Mumbai")
        print("   - Rain Rate: 250.5 mm/h")
        print()
        print("💡 If you don't receive the email:")
        print("   1. Check your spam/junk folder")
        print("   2. Verify SMTP settings in backend/.env")
        print("   3. Check that ENABLE_EMAIL_NOTIFICATIONS=true")
        print("   4. Review backend console for error messages")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR! Failed to send test email")
        print("=" * 60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check backend/.env has valid SMTP credentials")
        print("   2. Ensure ENABLE_EMAIL_NOTIFICATIONS=true")
        print("   3. For Gmail, use an App Password (not regular password)")
        print("   4. Check if SMTP server and port are correct")
        print()
        print("📝 Required .env settings:")
        print("   SMTP_SERVER=smtp.gmail.com")
        print("   SMTP_PORT=587")
        print("   SMTP_USERNAME=your-email@gmail.com")
        print("   SMTP_PASSWORD=your-app-password")
        print("   MAIL_FROM=your-email@gmail.com")
        print("   ENABLE_EMAIL_NOTIFICATIONS=true")
        print()
        return False
    
    return True

if __name__ == "__main__":
    print()
    print("🚀 Starting Email Alert Test...")
    print()
    
    # Run the async function
    success = asyncio.run(send_test_email())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
