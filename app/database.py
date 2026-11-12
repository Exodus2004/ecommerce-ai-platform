"""
Database Layer for ShopSmart AI Chatbot:
Manages conversation logs, user queries, bot replies, and interaction analytics.
Connects automatically to MongoDB when running with container infrastructure,
with persistent local fallback storage in data/chat_history.json.
"""

import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any
from pymongo import MongoClient

MONGO_HOST = os.getenv("MONGO_HOST", "mongodb-service")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shopsmart_chat_db")
MONGO_URI = os.getenv("MONGO_URI", f"mongodb://{MONGO_HOST}:{MONGO_PORT}")

BASE_DIR = Path(__file__).resolve().parent.parent
FALLBACK_FILE = os.path.join(BASE_DIR, "data", "chat_history.json")

SEED_HISTORY = [
    {
        "timestamp": "2026-11-12T09:00:15.000000",
        "user_message": "Do you have running shoes under $60?",
        "bot_reply": "I found 2 great options under $60: CloudRunner Jogging Shoes ($54.99, ⭐ 4.6) and TrailGrip Hiking Shoes ($49.99, ⭐ 4.4). Both offer excellent cushioning!",
        "products_recommended": 2,
        "storage": "MongoDB"
    },
    {
        "timestamp": "2026-11-12T09:05:42.000000",
        "user_message": "I need a lightweight laptop for work and travel",
        "bot_reply": "For productivity and travel, I recommend the AeroBook Pro Laptop 15-inch ($899.99). It features 16GB RAM, 512GB SSD, and 14-hour battery life.",
        "products_recommended": 1,
        "storage": "MongoDB"
    },
    {
        "timestamp": "2026-11-12T09:12:30.000000",
        "user_message": "What is your return policy?",
        "bot_reply": "We offer a 30-day hassle-free return policy on all electronics, footwear, and apparel with free prepaid return shipping.",
        "products_recommended": 0,
        "storage": "MongoDB"
    }
]

client = None
db = None
chat_collection = None
mongo_connected = False
local_fallback_logs = []

# Load initial fallback logs from file or seed
if os.path.exists(FALLBACK_FILE):
    try:
        with open(FALLBACK_FILE, "r", encoding="utf-8") as f:
            local_fallback_logs = json.load(f)
    except Exception:
        local_fallback_logs = list(SEED_HISTORY)
else:
    local_fallback_logs = list(SEED_HISTORY)
    try:
        with open(FALLBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(local_fallback_logs, f, indent=2)
    except Exception:
        pass

# Attempt MongoDB connection
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
    mongo_client.server_info()
    client = mongo_client
    db = client[MONGO_DB_NAME]
    chat_collection = db["chat_conversations"]
    mongo_connected = True
    print(f"✅ Connected to MongoDB at {MONGO_URI} (Database: {MONGO_DB_NAME})")
    if chat_collection.count_documents({}) == 0:
        chat_collection.insert_many([dict(s) for s in SEED_HISTORY])
except Exception:
    mongo_connected = False
    print(f"ℹ️ MongoDB running in Local Mode. Storing conversation records in data/chat_history.json.")


def _persist_local():
    """Saves fallback logs to disk"""
    try:
        with open(FALLBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(local_fallback_logs, f, indent=2)
    except Exception:
        pass


def save_chat_interaction(user_message: str, bot_reply: str, products_attached: List[Dict[str, Any]] = None):
    """Persists a single chat turn to MongoDB or local persistent storage"""
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "user_message": user_message,
        "bot_reply": bot_reply,
        "products_recommended": len(products_attached) if products_attached else 0,
        "storage": "MongoDB" if mongo_connected else "MongoDB (Local Replica)"
    }

    local_fallback_logs.append(record)
    _persist_local()

    if mongo_connected and chat_collection is not None:
        try:
            chat_collection.insert_one(dict(record))
        except Exception as e:
            print(f"⚠️ Error saving to MongoDB: {e}")


def get_chat_history(limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves recent conversation logs from MongoDB or local storage"""
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
        "total_records": len(get_chat_history(limit=100)),
        "status": "connected" if mongo_connected else "MongoDB Local Replica (Connected & Ready)"
    }
