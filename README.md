# 🛍️ ShopSmart AI: Intelligent E-Commerce Platform

> **Domain**: E-Commerce & Retail  
> **Key Capabilities**: AI Semantic Search • Pairwise Cosine Recommendations • Conversational Shopping Assistant  
> **Infrastructure Ready**: Designed for Docker Containerization & Kubernetes (AKS) LoadBalancer Deployment

---

## 🌟 The 3 Core AI Features Explained Simply

### 1. 🔍 Search Optimization (Semantic AI Search)
* **What it does**: Allows customers to search using natural phrases (e.g., *"budget running shoes"*, *"fast laptop for programming"*).
* **How it works without API keys**: Uses **TF-IDF Vectorization & Cosine Similarity**. Instead of looking for exact character matches, the AI converts descriptions into numerical concept vectors and measures the cosine angle between the search query and products in the catalog.
* **Endpoint**: `GET /api/search?q={query}&category={category}&max_price={price}`

### 2. ✨ Recommendation Engine (Content-Based Filtering)
* **What it does**: Suggests 3 relevant items whenever a customer views a product (e.g., viewing a gaming laptop recommends an ergonomic mouse, gaming keyboard, and high-performance rig).
* **How it works without API keys**: Precomputes an $N \times N$ pairwise cosine similarity matrix across product feature representations (category, tags, description).
* **Endpoint**: `GET /api/recommend/{product_id}`

### 3. 💬 AI Shopping Chatbot (Autonomous Concierge)
* **What it does**: Conversational shopping assistant that handles:
  - **Natural Product Queries**: *"Show me headphones under $50"* (automatically extracts category and budget, runs semantic search, and presents options).
  - **Store Policies & FAQs**: 30-day return window, shipping speeds, warranty information.
* **How it works without API keys**: Built-in Natural Language Understanding (NLU) regex intent & budget extraction + local catalog retrieval (RAG).
* **Endpoint**: `POST /api/chat` with body `{"message": "..."}`

---

## 🚀 How to Run Locally

```bash
# 1. Move into the project directory
cd ecommerce-ai-platform

# 2. Run the server
python run_local.py
```

* Open your browser to: **`http://localhost:8000`**
* You will see the full interactive store with live search, category pills, "Find Similar" AI recommendations, and the floating AI Chatbot widget at the bottom right!

---

## 📁 Project Structure

```
ecommerce-ai-platform/
├── data/
│   └── products.json          # Catalog of 16 rich, multi-category products
├── app/
│   ├── __init__.py
│   ├── ai_search.py           # TF-IDF Semantic Search Engine
│   ├── ai_recommender.py      # Pairwise Cosine Similarity Recommender
│   ├── ai_chatbot.py          # Intent & Budget Extracting Chatbot (Zero API keys)
│   └── main.py                # FastAPI backend & REST API endpoints
├── static/
│   ├── index.html             # Sleek single-page E-Commerce web interface
│   ├── style.css              # Modern UI styling
│   └── app.js                 # Frontend interactions & API bindings
├── deployment.yaml            # Kubernetes Deployment manifest (Replicas: 2, Probes)
├── service.yaml               # Kubernetes LoadBalancer Service (Port 80 -> 8000)
├── Dockerfile                 # Docker container recipe
├── .dockerignore              # Docker ignore rules
├── requirements.txt           # Lightweight dependencies
├── test_app.py                # Verification test script for all 3 AI features
├── test_chatbot.py            # Chatbot test script
└── run_local.py               # Local server launcher
```
