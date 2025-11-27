from fastapi.testclient import TestClient
from app.main import app
import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

client = TestClient(app)

def test_create_report():
    print("Testing create report...")
    response = client.post(
        "/crowdsource/report",
        json={
            "location": "Test Location",
            "intensity": "heavy",
            "description": "This is a test report from verification script."
        }
    )
    
    if response.status_code == 201:
        print("✅ Report created successfully!")
        print("Response:", response.json())
    else:
        print("❌ Failed to create report.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())

if __name__ == "__main__":
    test_create_report()
