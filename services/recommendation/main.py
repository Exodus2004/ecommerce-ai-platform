"""
Microservice 3: AI Recommendation Service
Computes pairwise cosine similarity matrix to recommend alternatives and lifestyle companions.
Port: 8003
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
try:
    from ai_recommender import AIRecommender
except ImportError:
    from services.recommendation.ai_recommender import AIRecommender

CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8001")
FALLBACK_DATA = os.path.join(Path(__file__).resolve().parent, "products.json")

app = FastAPI(
    title="ShopSmart AI Recommendation Microservice",
    description="Content-Based Filtering Recommendation Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender: Optional[AIRecommender] = None


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
    global recommender
    products = load_products()
    if products:
        recommender = AIRecommender(products)


@app.get("/")
def root():
    return {
        "service": "AI Recommendation Microservice",
        "status": "running",
        "port": 8003,
        "available_endpoints": ["/recommend/{id}", "/health"],
        "web_storefront": "http://localhost:8000"
    }


@app.get("/health")
@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "recommendation-service",
        "port": 8003,
        "indexed_products": len(recommender.products) if recommender else 0
    }


@app.get("/recommend")
@app.get("/api/recommend")
def recommend_info():
    return {
        "service": "ShopSmart AI Recommendation Microservice",
        "port": 8003,
        "usage": "Pass a product ID in the path to get content-based recommendations.",
        "example": "http://localhost:8003/recommend/1"
    }


@app.get("/recommend/{product_id}")
@app.get("/api/recommend/{product_id}")
def get_recommendations(product_id: int):
    global recommender
    if not recommender:
        products = load_products()
        recommender = AIRecommender(products)

    recs = recommender.get_recommendations(product_id=product_id, top_n=3)
    return {
        "product_id": product_id,
        "total_recommendations": len(recs),
        "recommendations": recs
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
