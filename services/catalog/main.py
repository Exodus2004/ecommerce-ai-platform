"""
Microservice 1: Product Catalog Service
Manages product inventory, categories, price queries, and product details.
Port: 8001
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DATA_PATH = os.path.join(Path(__file__).resolve().parent, "products.json")

app = FastAPI(
    title="ShopSmart Catalog Microservice",
    description="Manages product inventory, metadata, and catalog queries",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load catalog data
with open(DATA_PATH, "r", encoding="utf-8") as f:
    PRODUCTS: List[Dict[str, Any]] = json.load(f)

PRODUCT_MAP = {p["id"]: p for p in PRODUCTS}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "catalog-service",
        "port": 8001,
        "total_products": len(PRODUCTS)
    }


@app.get("/products")
def get_products(category: Optional[str] = None):
    if category and category.lower() != "all":
        filtered = [p for p in PRODUCTS if p["category"].lower() == category.lower()]
        return {"total": len(filtered), "products": filtered}
    return {"total": len(PRODUCTS), "products": PRODUCTS}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    if product_id not in PRODUCT_MAP:
        raise HTTPException(status_code=404, detail="Product not found")
    return PRODUCT_MAP[product_id]


@app.get("/categories")
def get_categories():
    categories = sorted(list(set(p["category"] for p in PRODUCTS)))
    return {"categories": categories}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
