import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import certifi

load_dotenv()

async def test_connection():
    mongo_url = os.getenv("MONGODB_URL")
    print(f"Testing connection to: {mongo_url.split('@')[-1]}") # Hide credentials
    
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
        # Force a connection to verify
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
