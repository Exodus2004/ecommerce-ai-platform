"""
Main FastAPI Application:
Exposes REST endpoints for:
1. Product Listing
2. AI Semantic Search
3. AI Recommendations
4. AI Chatbot
5. Health Check for Kubernetes Probes
"""

import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.ai_search import AISearchEngine
from app.ai_recommender import AIRecommender
from app.ai_chatbot import AIChatbot

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = os.path.join(BASE_DIR, "data", "products.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="ShopSmart AI E-Commerce Platform",
    description="AI-driven search, recommendations, and conversational shopping assistant",
    version="1.0.0"
)

# Mount static frontend assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize AI engines
search_engine = AISearchEngine(data_path=DATA_PATH)
recommender = AIRecommender(data_path=DATA_PATH)
chatbot = AIChatbot(search_engine=search_engine, recommender=recommender)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def serve_home():
    """Serves the interactive web interface"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/health")
def health_check():
    """Health check endpoint for Kubernetes liveness & readiness probes"""
    return {
        "status": "healthy",
        "service": "ShopSmart AI",
        "catalog_size": len(search_engine.products),
        "version": "1.0.0"
    }


@app.get("/api/products")
def get_all_products():
    """Returns the full product catalog"""
    return {"products": search_engine.products, "total": len(search_engine.products)}


@app.get("/api/search")
def search_products(
    q: str = Query("", description="Search query string"),
    category: str = Query("all", description="Product category filter"),
    max_price: Optional[float] = Query(None, description="Maximum budget filter"),
    min_rating: Optional[float] = Query(None, description="Minimum star rating")
):
    """Executes AI-powered semantic search with filters"""
    results = search_engine.search(
        query=q,
        category=category,
        max_price=max_price,
        min_rating=min_rating
    )
    return {
        "query": q,
        "category": category,
        "total_matches": len(results),
        "results": results
    }


@app.get("/api/recommend/{product_id}")
def get_recommendations(product_id: int):
    """Returns content-based AI recommendations for a specific product"""
    recommendations = recommender.get_recommendations(product_id=product_id, top_n=3)
    return {
        "product_id": product_id,
        "recommendations": recommendations
    }


@app.post("/api/chat")
def chat_with_ai(request: ChatRequest):
    """Processes user chat messages and returns intelligent replies"""
    response = chatbot.respond(request.message)
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
