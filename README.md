# 🛍️ ShopSmart AI: 5-Microservices + Polyglot Persistence (PostgreSQL & MongoDB)

> **Architecture**: Distributed Cloud-Native Microservices with **Polyglot Persistence**  
> **Databases**: **PostgreSQL** (Relational ACID for Catalog) & **MongoDB** (NoSQL Documents for Chatbot History)  
> **Infrastructure**: Kubernetes (AKS / Minikube) with Public LoadBalancer & Internal ClusterIP DNS  
> **AI Engines**: TF-IDF Semantic Search • Cosine Recommendation Matrix • Conversational Shopping Assistant

---

## 🏗️ The Polyglot Microservices Architecture

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
│ (ClusterIP:8001) │   │   filtering      │   │   companions     │              │ (ClusterIP:8004) │
└────────┬─────────┘   └──────────────────┘   └──────────────────┘              └────────┬─────────┘
         │                                                                               │
         ▼ (TCP :5432)                                                                   ▼ (TCP :27017)
┌──────────────────────────┐                                                    ┌──────────────────────────┐
│ 🐘 POSTGRESQL DATABASE   │                                                    │ 🍃 MONGODB DATABASE      │
│ (Relational ACID Storage)│                                                    │ (NoSQL Document Store)   │
│ • Table: `products`      │                                                    │ • Coll: `conversations`  │
│ (ClusterIP:5432)         │                                                    │ (ClusterIP:27017)        │
└──────────────────────────┘                                                    └──────────────────────────┘
```

---

## 📋 Microservices & Database Directory

| # | Component Name | Technology | Port | Kubernetes Service Type | Key Role in Architecture |
| :-: | :--- | :--- | :-: | :--- | :--- |
| **1** | **`api-gateway`** | FastAPI + Static HTML/CSS/JS | **8000** | **LoadBalancer (Port 80)** | Front door reverse proxy routing traffic |
| **2** | **`catalog-service`** | Python + SQLAlchemy | **8001** | **ClusterIP** | Product inventory & category management |
| **3** | **`search-service`** | Scikit-Learn TF-IDF | **8002** | **ClusterIP** | Vector-based semantic search & ranking |
| **4** | **`recommendation-service`**| Scikit-Learn Cosine Sim | **8003** | **ClusterIP** | Pairwise similarity matrix recommendations |
| **5** | **`chatbot-service`** | Python NLU + PyMongo | **8004** | **ClusterIP** | Conversational concierge & policy queries |
| **🐘**| **`postgres-service`**| **PostgreSQL 15** | **5432** | **ClusterIP** | Relational ACID storage for products |
| **🍃**| **`mongodb-service`** | **MongoDB 6.0** | **27017**| **ClusterIP** | Document store for chat logs & analytics |

---

## 🎯 Why This Polyglot Architecture is Best Practice:

1. **PostgreSQL for Catalog**:  
   Products have strict schemas (Price, Category, Rating, Stock). PostgreSQL provides **ACID transactions and relational indexing**, ensuring accurate pricing and inventory.
2. **MongoDB for Chatbot History**:  
   Conversations are **semi-structured, dynamic JSON documents** with varying message lengths, timestamps, session IDs, and recommendation payloads. MongoDB provides effortless document storage and fast analytics.

---

## 🚀 How to Run Locally

```bash
cd ecommerce-ai-platform
python run_all_services.py
```

* Open your browser to: **`http://localhost:8000`**
* Check the live 5-service health status: **`http://localhost:8000/api/health`**
* View conversation logs from MongoDB: **`http://localhost:8000/api/chat/history`**

---

## 🚢 Kubernetes Deployment Manifests (Root Directory)

* **`deployment.yaml`**: Contains Deployments for:
  - `postgres-deployment` (PostgreSQL Database)
  - `mongodb-deployment` (MongoDB Database)
  - 5 Microservices (Gateway, Catalog, Search, Recommendation, Chatbot) with 2 replicas each!
* **`service.yaml`**: Contains Services for all components (`api-gateway-service` as `type: LoadBalancer`, and 6 internal `type: ClusterIP` services).

```bash
# Deploy all databases and microservices with one command:
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check running pods (Databases + 10 Microservice pods):
kubectl get pods

# Get the Public LoadBalancer IP:
kubectl get svc api-gateway-service
```
