import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from .logs import logger

load_dotenv()

CONNECTION_STRING = os.getenv('MONGO_URI')
client = AsyncIOMotorClient(CONNECTION_STRING)
db = client["sample_paper_db"]
logger.debug("Database Initialized")