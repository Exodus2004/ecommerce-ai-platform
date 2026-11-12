# 🛍️ ShopSmart AI: 5-Microservice E-Commerce Architecture

> **Architecture**: Distributed Cloud-Native Microservices (5 Independent Services)  
> **Infrastructure**: Kubernetes (AKS / Minikube) with Public LoadBalancer & Internal ClusterIP DNS  
> **AI Engines**: TF-IDF Semantic Search • Cosine Recommendation Matrix • Conversational Shopping Assistant

---

## 🏗️ The 5 Microservices Architecture

```
                                [ External Internet User ]
                                            │
                                            ▼ (Public Port 80)
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. API GATEWAY & FRONTEND MICROSERVICE  (Kubernetes Type: LoadBalancer)                 │
│    • Port: 80 -> 8000                                                                  │
│    • Serves the single-page HTML/CSS/JS frontend storefront                            │
│    • Acts as Reverse Proxy routing traffic to the 4 internal microservices             │
└────────┬──────────────────────┬──────────────────────┬─────────────────────────────────┘
         │                      │                      │                                 │
         │ (HTTP :8001)         │ (HTTP :8002)         │ (HTTP :8003)                    │ (HTTP :8004)
         ▼                      ▼                      ▼                                 ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐              ┌──────────────────┐
│ 2. CATALOG       │   │ 3. AI SEARCH     │   │ 4. AI RECOMMENDER│              │ 5. AI CHATBOT    │
│    SERVICE       │   │    OPTIMIZATION  │   │    SERVICE       │              │    SERVICE       │
│                  │   │    SERVICE       │   │                  │              │                  │
│ • Inventory,     │   │ • TF-IDF Vector  │   │ • Pairwise       │              │ • Multi-Tier NLU │
│   prices, and    │   │   semantic search│   │   cosine matrix  │              │   intent parsing │
│   metadata       │   │ • Dynamic budget │   │ • Alternatives & │              │ • Store policies │
│                  │   │   filtering      │   │   companions     │              │ • Product cards  │
│ (ClusterIP:8001) │   │ (ClusterIP:8002) │   │ (ClusterIP:8003) │              │ (ClusterIP:8004) │
└──────────────────┘   └──────────────────┘   └──────────────────┘              └──────────────────┘
```

---

## 📋 Microservices Directory

| # | Microservice Name | Folder | Port | Kubernetes Service Type | Key Functionality |
| :-: | :--- | :--- | :-: | :--- | :--- |
| **1** | **`api-gateway`** | `services/gateway/` | **8000** | **LoadBalancer (Port 80)** | Serves Web Storefront & routes API calls |
| **2** | **`catalog-service`** | `services/catalog/` | **8001** | **ClusterIP** | Product inventory & category management |
| **3** | **`search-service`** | `services/search/` | **8002** | **ClusterIP** | TF-IDF Vector Search & relevance ranking |
| **4** | **`recommendation-service`** | `services/recommendation/` | **8003** | **ClusterIP** | Pairwise Cosine Matrix recommendations |
| **5** | **`chatbot-service`** | `services/chatbot/` | **8004** | **ClusterIP** | Conversational concierge & policy queries |

---

## 🚀 How to Run Locally (All 5 Services in 1 Command!)

```bash
cd ecommerce-ai-platform
python run_all_services.py
```

* Open your browser to: **`http://localhost:8000`**
* Check the live 5-service health status: **`http://localhost:8000/api/health`**
  ```json
  {
    "gateway": "healthy",
    "overall_cluster_status": "healthy",
    "microservices": {
      "catalog_service": "healthy",
      "search_service": "healthy",
      "recommendation_service": "healthy",
      "chatbot_service": "healthy"
    }
  }
  ```

---

## 🚢 Kubernetes Deployment Manifests (Root Directory)

* **`deployment.yaml`**: Contains Deployments for all **5 microservices** (2 replicas each = 10 high-availability pods total).
* **`service.yaml`**: Contains Services for all **5 microservices** (`api-gateway-service` as `type: LoadBalancer`, and 4 internal `type: ClusterIP` services).

```bash
# Deploy all 5 microservices to Kubernetes
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check all 10 running pods
kubectl get pods

# Get the Public LoadBalancer IP
kubectl get svc api-gateway-service
```
