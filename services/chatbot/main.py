"""
Microservice 4: AI Chatbot Service
Autonomous conversational shopping concierge.
Port: 8004
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
try:
    from ai_chatbot import AIChatbot
except ImportError:
    from services.chatbot.ai_chatbot import AIChatbot

CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8001")
FALLBACK_DATA = os.path.join(Path(__file__).resolve().parent, "products.json")

app = FastAPI(
    title="ShopSmart AI Chatbot Microservice",
    description="Conversational Shopping Assistant Service",
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


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "chatbot-service",
        "port": 8004
    }


@app.post("/chat")
def chat(request: ChatRequest):
    global chatbot
    if not chatbot:
        products = load_products()
        chatbot = AIChatbot(products)

    response = chatbot.respond(request.message)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
