"""
Microservice 2: AI Search Optimization Service
Provides semantic vector search with TF-IDF and Cosine Similarity.
Port: 8002
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
try:
    from ai_search import AISearchEngine
except ImportError:
    from services.search.ai_search import AISearchEngine

CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8001")
FALLBACK_DATA = os.path.join(Path(__file__).resolve().parent, "products.json")

app = FastAPI(
    title="ShopSmart AI Search Microservice",
    description="Vector-based semantic search and ranking engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

search_engine: Optional[AISearchEngine] = None


def load_products() -> List[Dict[str, Any]]:
    # Try fetching from Catalog Microservice
    try:
        resp = requests.get(f"{CATALOG_URL}/products", timeout=3)
        if resp.status_code == 200:
            return resp.json().get("products", [])
    except Exception:
        pass
    # Fallback to local file if catalog microservice is booting
    if os.path.exists(FALLBACK_DATA):
        with open(FALLBACK_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.on_event("startup")
def startup_event():
    global search_engine
    products = load_products()
    if products:
        search_engine = AISearchEngine(products)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "search-service",
        "port": 8002,
        "indexed_products": len(search_engine.products) if search_engine else 0
    }


@app.get("/search")
def search(
    q: str = Query("", description="Query string"),
    category: str = Query("all", description="Category filter"),
    max_price: Optional[float] = Query(None, description="Max budget"),
    min_rating: Optional[float] = Query(None, description="Min star rating")
):
    global search_engine
    if not search_engine:
        products = load_products()
        search_engine = AISearchEngine(products)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
