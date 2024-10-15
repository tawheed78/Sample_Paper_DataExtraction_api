from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CONNECTION_STRING = os.getenv('MONGO_URI')

client = AsyncIOMotorClient(CONNECTION_STRING)
db = client["sample_paper_db"]
if client:
    print("******MongoDB connection successful.******")
else:
    print("connection failed!")