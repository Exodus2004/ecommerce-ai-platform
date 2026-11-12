"""
Microservice 5: API Gateway & Reverse Proxy
Serves the web storefront and routes incoming traffic to internal microservices.
Exposed externally via Kubernetes LoadBalancer on Port 80 (targetPort: 8000).
"""

import os
from pathlib import Path
from typing import Optional
import httpx
from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

# Microservice Discovery URLs (Kubernetes Service DNS / Localhost)
CATALOG_URL = os.getenv("CATALOG_SERVICE_URL", "http://127.0.0.1:8001")
SEARCH_URL = os.getenv("SEARCH_SERVICE_URL", "http://127.0.0.1:8002")
RECOMMENDATION_URL = os.getenv("RECOMMENDATION_SERVICE_URL", "http://127.0.0.1:8003")
CHATBOT_URL = os.getenv("CHATBOT_SERVICE_URL", "http://127.0.0.1:8004")

STATIC_DIR = os.path.join(Path(__file__).resolve().parent, "static")

app = FastAPI(
    title="ShopSmart AI - API Gateway Microservice",
    description="Edge API Gateway and Reverse Proxy routing traffic to 4 internal microservices",
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
                    "GET  /chat/history             -> MongoDB conversation history (also /history, /api/chat/history)",
                    "GET  /health                   -> Cluster health check (also /api/health)",
                    "GET  /docs                     -> Swagger API UI"
                ]
            }
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Mount static web frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ChatPayload(BaseModel):
    message: str


@app.get("/")
def serve_home():
    """Serves the interactive E-Commerce web interface"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/health")
@app.get("/health")
async def health_check():
    """
    Cluster Health Probe:
    Aggregates health status across all 5 microservices in the architecture.
    """
    services_status = {}
    async with httpx.AsyncClient(timeout=2.0) as client:
        # Check Catalog
        try:
            r = await client.get(f"{CATALOG_URL}/health")
            services_status["catalog_service"] = "healthy" if r.status_code == 200 else "degraded"
        except Exception:
            services_status["catalog_service"] = "offline"

        # Check Search
        try:
            r = await client.get(f"{SEARCH_URL}/health")
            services_status["search_service"] = "healthy" if r.status_code == 200 else "degraded"
        except Exception:
            services_status["search_service"] = "offline"

        # Check Recommendation
        try:
            r = await client.get(f"{RECOMMENDATION_URL}/health")
            services_status["recommendation_service"] = "healthy" if r.status_code == 200 else "degraded"
        except Exception:
            services_status["recommendation_service"] = "offline"

        # Check Chatbot
        try:
            r = await client.get(f"{CHATBOT_URL}/health")
            services_status["chatbot_service"] = "healthy" if r.status_code == 200 else "degraded"
        except Exception:
            services_status["chatbot_service"] = "offline"

    all_ok = all(v == "healthy" for v in services_status.values())
    return {
        "gateway": "healthy",
        "overall_cluster_status": "healthy" if all_ok else "partially_degraded",
        "microservices": services_status
    }


# Route 1: Proxy to Catalog Microservice
@app.get("/api/products")
@app.get("/products")
@app.get("/catalog")
async def get_products(category: Optional[str] = None):
    url = f"{CATALOG_URL}/products"
    if category and category.lower() != "all":
        url += f"?category={category}"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(url)
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Catalog microservice unavailable: {str(e)}")


# Route 2: Proxy to AI Search Optimization Microservice
@app.get("/api/search")
@app.get("/search")
async def search_products(
    q: str = Query("", description="Search query string"),
    category: str = Query("all", description="Product category filter"),
    max_price: Optional[float] = Query(None, description="Maximum budget filter"),
    min_rating: Optional[float] = Query(None, description="Minimum star rating")
):
    params = {"q": q, "category": category}
    if max_price is not None:
        params["max_price"] = max_price
    if min_rating is not None:
        params["min_rating"] = min_rating

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{SEARCH_URL}/search", params=params)
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Search microservice unavailable: {str(e)}")


# Route 3: Proxy to AI Recommendation Microservice
@app.get("/api/recommend/{product_id}")
@app.get("/recommend/{product_id}")
async def get_recommendations(product_id: int):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{RECOMMENDATION_URL}/recommend/{product_id}")
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Recommendation microservice unavailable: {str(e)}")


# Route 4: Proxy to AI Chatbot Microservice
@app.post("/api/chat")
@app.post("/chat")
async def chat_with_ai(payload: ChatPayload):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(f"{CHATBOT_URL}/chat", json={"message": payload.message})
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Chatbot microservice unavailable: {str(e)}")


# Route 5: View Chatbot History Stored in MongoDB
@app.get("/api/chat/history")
@app.get("/chat/history")
@app.get("/history")
@app.get("/api/history")
async def get_chat_history(limit: int = Query(10)):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{CHATBOT_URL}/chat/history?limit={limit}")
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Chatbot microservice unavailable: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
