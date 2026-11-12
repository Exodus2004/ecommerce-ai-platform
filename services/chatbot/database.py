"""
Database Layer for AI Chatbot Microservice:
Uses MongoDB to persist conversation logs, user queries, bot replies, and interaction analytics.
Features automatic connection to MongoDB in Kubernetes, with local in-memory fallback.
"""

import os
import datetime
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

MONGO_HOST = os.getenv("MONGO_HOST", "mongodb-service")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shopsmart_chat_db")
MONGO_URI = os.getenv("MONGO_URI", f"mongodb://{MONGO_HOST}:{MONGO_PORT}")

client = None
db = None
chat_collection = None
mongo_connected = False
local_fallback_logs = []

try:
    # 2-second timeout to check if MongoDB is live
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    mongo_client.server_info()  # Forces a call to verify connection
    client = mongo_client
    db = client[MONGO_DB_NAME]
    chat_collection = db["chat_conversations"]
    mongo_connected = True
    print(f"✅ Connected to MongoDB at {MONGO_URI} (Database: {MONGO_DB_NAME})")
except Exception:
    mongo_connected = False
    print(f"ℹ️ MongoDB not reachable at {MONGO_URI}. Using in-memory fallback (MongoDB-Ready).")


def save_chat_interaction(user_message: str, bot_reply: str, products_attached: List[Dict[str, Any]] = None):
    """Persists a single chat turn to MongoDB"""
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "user_message": user_message,
        "bot_reply": bot_reply,
        "products_recommended": len(products_attached) if products_attached else 0,
        "storage": "MongoDB" if mongo_connected else "Local-Memory"
    }

    if mongo_connected and chat_collection is not None:
        try:
            chat_collection.insert_one(record)
        except Exception as e:
            print(f"⚠️ Error saving to MongoDB: {e}")
            local_fallback_logs.append(record)
    else:
        local_fallback_logs.append(record)


def get_chat_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieves recent conversation logs from MongoDB"""
    if mongo_connected and chat_collection is not None:
        try:
            cursor = chat_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
            return list(cursor)
        except Exception:
            return list(reversed(local_fallback_logs[-limit:]))
    return list(reversed(local_fallback_logs[-limit:]))


def get_db_status() -> Dict[str, Any]:
    return {
        "database": "MongoDB",
        "target_host": MONGO_HOST,
        "connected": mongo_connected,
        "database_name": MONGO_DB_NAME,
        "status": "connected" if mongo_connected else "Local Dev Mode (MongoDB Ready)"
    }
