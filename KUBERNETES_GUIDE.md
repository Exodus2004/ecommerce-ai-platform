# 🚢 Kubernetes Polyglot Microservices Deployment Guide

> **Project**: ShopSmart AI E-Commerce Platform  
> **Topology**: 5 Microservices + 2 Databases (**PostgreSQL** & **MongoDB**), Public LoadBalancer

---

## 🏗️ Kubernetes Cluster Topology

```
                      [ External Internet Traffic ]
                                  │
                                  ▼ (HTTP Port 80)
                ┌───────────────────────────────────┐
                │ Kubernetes Service (LoadBalancer) │
                │ Name: api-gateway-service         │
                └─────────────────┬─────────────────┘
                                  │ (targetPort: 8000)
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
      [ Pod: api-gateway-1 ]            [ Pod: api-gateway-2 ]
                 │
                 ├──► http://catalog-service:8001         (ClusterIP) ──► postgres-service:5432
                 ├──► http://search-service:8002          (ClusterIP)
                 ├──► http://recommendation-service:8003  (ClusterIP)
                 └──► http://chatbot-service:8004         (ClusterIP) ──► mongodb-service:27017
```

---

## 🚀 Deployment Commands

### Step 1: Deploy Everything (Databases + Microservices)

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

### Step 2: Verify Running Pods

```bash
kubectl get pods
```

**Expected Output:**
```text
NAME                                             READY   STATUS    RESTARTS   AGE
postgres-deployment-55d8869ff9-p44qk             1/1     Running   0          45s
mongodb-deployment-7bb9d4797d-z88v1              1/1     Running   0          45s
api-gateway-deployment-7bb9d4797d-6l9fx          1/1     Running   0          30s
api-gateway-deployment-7bb9d4797d-mpxj8          1/1     Running   0          30s
catalog-service-deployment-859846d5c6-c9w42      1/1     Running   0          30s
catalog-service-deployment-859846d5c6-q2r11      1/1     Running   0          30s
search-service-deployment-55d8869ff9-7gjk3       1/1     Running   0          30s
search-service-deployment-55d8869ff9-w991z       1/1     Running   0          30s
recommendation-service-deployment-74f4b9c9f4-x7  1/1     Running   0          30s
recommendation-service-deployment-74f4b9c9f4-zp  1/1     Running   0          30s
chatbot-service-deployment-64d898bfcb-81k2m      1/1     Running   0          30s
chatbot-service-deployment-64d898bfcb-pt99a      1/1     Running   0          30s
```

---

### Step 3: Verify Services

```bash
kubectl get svc
```

**Expected Output:**
```text
NAME                     TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
api-gateway-service      LoadBalancer   10.0.182.45    20.124.50.80    80:31250/TCP   45s
postgres-service         ClusterIP      10.0.182.50    <none>          5432/TCP       45s
mongodb-service          ClusterIP      10.0.182.51    <none>          27017/TCP      45s
catalog-service          ClusterIP      10.0.182.46    <none>          8001/TCP       45s
search-service           ClusterIP      10.0.182.47    <none>          8002/TCP       45s
recommendation-service   ClusterIP      10.0.182.48    <none>          8003/TCP       45s
chatbot-service          ClusterIP      10.0.182.49    <none>          8004/TCP       45s
```

---

## 🎯 Questions Your Instructor Will Ask About Databases & Architecture

### 1. "Why did you use PostgreSQL for Catalog and MongoDB for Chatbot?" (Polyglot Persistence)
> **Answer**:  
> *"Sir, this is the enterprise **Polyglot Persistence Pattern**.*  
> *1. **PostgreSQL** was chosen for the **Catalog Service** because product inventory and pricing require strict relational schemas, ACID transaction guarantees, and structured indexing.*  
> *2. **MongoDB** was chosen for the **Chatbot Service** because user conversations and interaction analytics are **semi-structured JSON documents** with varying message sizes and metadata that benefit from a schema-less NoSQL document store."*

### 2. "How do the microservices connect to PostgreSQL and MongoDB in Kubernetes?"
> **Answer**:  
> *"Through **Kubernetes Service DNS Discovery**. The Catalog Service connects using the environment variable `POSTGRES_HOST=postgres-service:5432`. The Chatbot Service connects using `MONGO_HOST=mongodb-service:27017`."*

### 3. "Are the databases exposed to the public internet?"
> **Answer**:  
> *"No, sir! For security best practices, both PostgreSQL and MongoDB are configured as **ClusterIP Services**. They are completely invisible to the outside internet and can only be accessed privately by our authorized microservices within the cluster. Only the **API Gateway** is exposed publicly via `type: LoadBalancer` on Port 80."*
