"""
Insert Test Warnings into Database

This script inserts test warning data into MongoDB so it appears
on the frontend Dashboard.

Usage:
    python insert_test_warnings.py
"""

import sys
import os
from datetime import datetime, timedelta, UTC

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import sync_warnings_collection, sync_predictions_collection

def insert_test_warnings():
    """Insert test warnings into the database"""
    
    print("=" * 60)
    print("📊 INSERTING TEST WARNINGS INTO DATABASE")
    print("=" * 60)
    print()
    
    # Test warnings for different cities
    test_warnings = [
        {
            "cell_id": "MUMBAI_CRITICAL_001",
            "mcs_type": "MCC",
            "forecast_time": 30,
            "predicted_timestamp": datetime.now(UTC) + timedelta(minutes=30),
            "predicted_top_10_rain_rate": 250.5,
            "message": "⚠️ CRITICAL: Heavy rainfall predicted for Mumbai! Predicted Top 10% Mean Rain Rate: 250.5 mm/h",
            "location_geojson": {
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
            },
            "is_active": True,
            "issued_at": datetime.now(UTC),
            "impact_risk": "High",
            "severity": "Critical"
        },
        {
            "cell_id": "DELHI_SEVERE_002",
            "mcs_type": "SLD",
            "forecast_time": 60,
            "predicted_timestamp": datetime.now(UTC) + timedelta(minutes=60),
            "predicted_top_10_rain_rate": 195.3,
            "message": "⚠️ SEVERE: Heavy rainfall predicted for Delhi! Predicted Top 10% Mean Rain Rate: 195.3 mm/h",
            "location_geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [77.0, 28.4],
                        [77.4, 28.4],
                        [77.4, 28.8],
                        [77.0, 28.8],
                        [77.0, 28.4]
                    ]
                ]
            },
            "is_active": True,
            "issued_at": datetime.now(UTC),
            "impact_risk": "High",
            "severity": "Severe"
        },
        {
            "cell_id": "KOLKATA_MODERATE_003",
            "mcs_type": "CC",
            "forecast_time": 30,
            "predicted_timestamp": datetime.now(UTC) + timedelta(minutes=30),
            "predicted_top_10_rain_rate": 165.8,
            "message": "⚠️ MODERATE: Heavy rainfall predicted for Kolkata! Predicted Top 10% Mean Rain Rate: 165.8 mm/h",
            "location_geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [88.2, 22.4],
                        [88.5, 22.4],
                        [88.5, 22.7],
                        [88.2, 22.7],
                        [88.2, 22.4]
                    ]
                ]
            },
            "is_active": True,
            "issued_at": datetime.now(UTC),
            "impact_risk": "Medium",
            "severity": "Moderate"
        }
    ]
    
    print("📝 Inserting warnings into database...")
    print()
    
    inserted_count = 0
    for warning in test_warnings:
        try:
            result = sync_warnings_collection.insert_one(warning)
            inserted_count += 1
            print(f"✅ Inserted: {warning['cell_id']}")
            print(f"   Location: {warning['message'].split('for ')[1].split('!')[0]}")
            print(f"   Rain Rate: {warning['predicted_top_10_rain_rate']} mm/h")
            print(f"   Severity: {warning['severity']}")
            print(f"   ID: {result.inserted_id}")
            print()
        except Exception as e:
            print(f"❌ Failed to insert {warning['cell_id']}: {e}")
            print()
    
    print("=" * 60)
    print(f"✅ SUCCESS! Inserted {inserted_count} warnings")
    print("=" * 60)
    print()
    print("🌐 Check the frontend Dashboard:")
    print("   1. Go to http://localhost:3000")
    print("   2. Navigate to Dashboard")
    print("   3. You should see the warnings displayed on the map")
    print()
    print("📊 Warnings inserted:")
    print("   - Mumbai (Critical) - 250.5 mm/h")
    print("   - Delhi (Severe) - 195.3 mm/h")
    print("   - Kolkata (Moderate) - 165.8 mm/h")
    print()
    
    # Also insert some predictions for the dashboard
    print("📈 Inserting test predictions...")
    test_predictions = [
        {
            "cell_id": "MUMBAI_CRITICAL_001",
            "mcs_type": "MCC",
            "forecast_time": 30,
            "predicted_timestamp": datetime.now(UTC) + timedelta(minutes=30),
            "predicted_mean_rain_rate": 185.5,
            "predicted_top_10_rain_rate": 250.5,
            "prediction_made_at": datetime.now(UTC),
            "impact_risk": "High"
        },
        {
            "cell_id": "DELHI_SEVERE_002",
            "mcs_type": "SLD",
            "forecast_time": 60,
            "predicted_timestamp": datetime.now(UTC) + timedelta(minutes=60),
            "predicted_mean_rain_rate": 155.2,
            "predicted_top_10_rain_rate": 195.3,
            "prediction_made_at": datetime.now(UTC),
            "impact_risk": "High"
        },
        {
            "cell_id": "KOLKATA_MODERATE_003",
            "mcs_type": "CC",
            "forecast_time": 30,
            "predicted_timestamp": datetime.now(UTC) + timedelta(minutes=30),
            "predicted_mean_rain_rate": 125.8,
            "predicted_top_10_rain_rate": 165.8,
            "prediction_made_at": datetime.now(UTC),
            "impact_risk": "Medium"
        }
    ]
    
    pred_count = 0
    for pred in test_predictions:
        try:
            sync_predictions_collection.insert_one(pred)
            pred_count += 1
        except Exception as e:
            print(f"Failed to insert prediction: {e}")
    
    print(f"✅ Inserted {pred_count} predictions")
    print()
    print("🎉 All test data inserted successfully!")
    print()

if __name__ == "__main__":
    print()
    print("🚀 Starting Database Insert...")
    print()
    
    insert_test_warnings()
    
    print("✨ Done! Refresh your frontend to see the warnings.")
    print()
