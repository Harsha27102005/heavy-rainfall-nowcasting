"""
Clear Test Warnings from Database

This script removes the test warnings from MongoDB.

Usage:
    python clear_test_warnings.py
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import sync_warnings_collection, sync_predictions_collection

def clear_test_warnings():
    """Clear test warnings from the database"""
    
    print("=" * 60)
    print("🗑️  CLEARING TEST WARNINGS")
    print("=" * 60)
    print()
    
    # Test warning cell IDs
    test_cell_ids = [
        "MUMBAI_CRITICAL_001",
        "DELHI_SEVERE_002",
        "KOLKATA_MODERATE_003",
        "TEST_MUMBAI_001"  # From email test
    ]
    
    print("🔍 Deleting test warnings...")
    result = sync_warnings_collection.delete_many({
        "cell_id": {"$in": test_cell_ids}
    })
    print(f"✅ Deleted {result.deleted_count} warnings")
    print()
    
    print("🔍 Deleting test predictions...")
    pred_result = sync_predictions_collection.delete_many({
        "cell_id": {"$in": test_cell_ids}
    })
    print(f"✅ Deleted {pred_result.deleted_count} predictions")
    print()
    
    print("=" * 60)
    print("✅ SUCCESS! Test data cleared")
    print("=" * 60)
    print()
    print("🌐 Refresh your Dashboard:")
    print("   - Alert banner should disappear")
    print("   - Active Alerts should show 'No active alerts'")
    print("   - Map should be clear")
    print()

if __name__ == "__main__":
    print()
    print("🚀 Starting cleanup...")
    print()
    
    clear_test_warnings()
    
    print("✨ Done! Refresh your frontend.")
    print()
