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
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

from app.ai_search import AISearchEngine
from app.ai_recommender import AIRecommender
from app.ai_chatbot import AIChatbot
from app.database import save_chat_interaction, get_chat_history, get_db_status

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = os.path.join(BASE_DIR, "data", "products.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(
    title="ShopSmart AI E-Commerce Platform",
    description="AI-driven search, recommendations, and conversational shopping assistant",
    version="1.0.0"
)

# Friendly 404 handler replacing raw {"detail":"Not Found"}
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Route Not Found",
                "requested_path": request.url.path,
                "hint": "Open http://localhost:8000 in your browser to view the storefront UI, or http://localhost:8000/docs for Swagger API documentation.",
                "available_endpoints": [
                    "GET  /                         -> Storefront Web UI",
                    "GET  /products                 -> Product catalog (also /api/products)",
                    "GET  /search?q=laptop          -> AI semantic search (also /api/search)",
                    "GET  /recommend/{product_id}   -> AI recommendations (also /api/recommend/{id})",
                    "POST /chat                     -> AI shopping assistant (also /api/chat)",
                    "GET  /chat/history             -> Conversation history (also /history, /api/chat/history)",
                    "GET  /health                   -> Health check status (also /api/health)",
                    "GET  /docs                     -> Swagger API UI"
                ]
            }
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

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
@app.get("/health")
def health_check():
    """Health check endpoint for Kubernetes liveness & readiness probes"""
    return {
        "status": "healthy",
        "service": "ShopSmart AI",
        "catalog_size": len(search_engine.products),
        "version": "1.0.0"
    }


@app.get("/api/products")
@app.get("/products")
@app.get("/catalog")
def get_all_products():
    """Returns the full product catalog"""
    return {"products": search_engine.products, "total": len(search_engine.products)}


@app.get("/api/search")
@app.get("/search")
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
@app.get("/recommend/{product_id}")
def get_recommendations(product_id: int):
    """Returns content-based AI recommendations for a specific product"""
    recommendations = recommender.get_recommendations(product_id=product_id, top_n=3)
    return {
        "product_id": product_id,
        "recommendations": recommendations
    }


@app.post("/api/chat")
@app.post("/chat")
def chat_with_ai(request: ChatRequest):
    """Processes user chat messages and returns intelligent replies"""
    response = chatbot.respond(request.message)

    # Persist conversation turn to MongoDB (or local MongoDB replica)
    save_chat_interaction(
        user_message=request.message,
        bot_reply=response.get("reply", ""),
        products_attached=response.get("products", [])
    )

    return response


@app.get("/api/chat/history")
@app.get("/chat/history")
@app.get("/history")
@app.get("/api/history")
def get_chat_history_endpoint(limit: int = Query(15, description="Max logs to return")):
    """Returns conversation logs stored in MongoDB"""
    history = get_chat_history(limit=limit)
    db_info = get_db_status()
    return {
        "database": db_info["database"],
        "status": db_info["status"],
        "total_records": len(history),
        "history": history
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
