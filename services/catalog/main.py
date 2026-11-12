"""
Microservice 1: Product Catalog Service
Manages product inventory, categories, price queries, and product details.
Database: PostgreSQL (with automatic schema initialization & seeding).
Port: 8001
"""

from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
try:
    from database import init_db, get_all_products, get_product_by_id, get_all_categories, db_type, POSTGRES_HOST
except ImportError:
    from services.catalog.database import init_db, get_all_products, get_product_by_id, get_all_categories, db_type, POSTGRES_HOST

app = FastAPI(
    title="ShopSmart Catalog Microservice",
    description="Manages product inventory using PostgreSQL database",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health")
def health():
    products = get_all_products()
    return {
        "status": "healthy",
        "service": "catalog-service",
        "database": db_type,
        "database_target": POSTGRES_HOST,
        "port": 8001,
        "total_products": len(products)
    }


@app.get("/products")
def get_products(category: Optional[str] = None):
    products = get_all_products(category=category)
    return {"total": len(products), "products": products, "database": db_type}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    prod = get_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@app.get("/categories")
def get_categories():
    categories = get_all_categories()
    return {"categories": categories}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
