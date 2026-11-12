"""
Microservice 4: AI Chatbot Service
Autonomous conversational shopping concierge.
Database: MongoDB (persists conversation history, queries, and analytics).
Port: 8004
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    from ai_chatbot import AIChatbot
except ImportError:
    from services.chatbot.ai_chatbot import AIChatbot
try:
    from database import save_chat_interaction, get_chat_history, get_db_status
except ImportError:
    from services.chatbot.database import save_chat_interaction, get_chat_history, get_db_status

CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8001")
FALLBACK_DATA = os.path.join(Path(__file__).resolve().parent, "products.json")

app = FastAPI(
    title="ShopSmart AI Chatbot Microservice",
    description="Conversational Shopping Assistant Service with MongoDB persistence",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot: Optional[AIChatbot] = None


class ChatRequest(BaseModel):
    message: str


def load_products() -> List[Dict[str, Any]]:
    try:
        resp = requests.get(f"{CATALOG_URL}/products", timeout=3)
        if resp.status_code == 200:
            return resp.json().get("products", [])
    except Exception:
        pass
    if os.path.exists(FALLBACK_DATA):
        with open(FALLBACK_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.on_event("startup")
def startup_event():
    global chatbot
    products = load_products()
    if products:
        chatbot = AIChatbot(products)


@app.get("/")
def root():
    return {
        "service": "AI Chatbot Microservice",
        "status": "running",
        "port": 8004,
        "database": "MongoDB",
        "available_endpoints": ["POST /chat", "GET /chat/history", "GET /health"],
        "web_storefront": "http://localhost:8000"
    }


@app.get("/health")
@app.get("/api/health")
def health():
    db_info = get_db_status()
    return {
        "status": "healthy",
        "service": "chatbot-service",
        "database": db_info["database"],
        "database_status": db_info["status"],
        "database_target": db_info["target_host"],
        "port": 8004
    }


@app.post("/chat")
@app.post("/api/chat")
def chat(request: ChatRequest):
    global chatbot
    if not chatbot:
        products = load_products()
        chatbot = AIChatbot(products)

    response = chatbot.respond(request.message)

    # Persist the conversational interaction to MongoDB
    save_chat_interaction(
        user_message=request.message,
        bot_reply=response.get("reply", ""),
        products_attached=response.get("products", [])
    )

    return response


@app.get("/chat/history")
@app.get("/api/chat/history")
@app.get("/history")
def get_history(limit: int = Query(10, description="Max number of logs to return")):
    """Returns conversation logs stored in MongoDB"""
    history = get_chat_history(limit=limit)
    return {
        "database": get_db_status()["database"],
        "total_records": len(history),
        "history": history
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
