# 🚢 Kubernetes 5-Microservices Deployment Guide

> **Project**: ShopSmart AI E-Commerce Platform  
> **Topology**: 5 Distinct Microservices, 10 Pod Replicas, Public LoadBalancer

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
                 ├──► http://catalog-service:8001         (ClusterIP)
                 ├──► http://search-service:8002          (ClusterIP)
                 ├──► http://recommendation-service:8003  (ClusterIP)
                 └──► http://chatbot-service:8004         (ClusterIP)
```

---

## 🚀 Deployment Commands

### Step 1: Deploy All 5 Microservices (10 Pods)

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

### Step 2: Verify Pods

```bash
kubectl get pods
```

**Expected Output:**
```text
NAME                                             READY   STATUS    RESTARTS   AGE
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

### Step 3: Verify the 5 Services

```bash
kubectl get svc
```

**Expected Output:**
```text
NAME                     TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
api-gateway-service      LoadBalancer   10.0.182.45    20.124.50.80    80:31250/TCP   45s
catalog-service          ClusterIP      10.0.182.46    <none>          8001/TCP       45s
search-service           ClusterIP      10.0.182.47    <none>          8002/TCP       45s
recommendation-service   ClusterIP      10.0.182.48    <none>          8003/TCP       45s
chatbot-service          ClusterIP      10.0.182.49    <none>          8004/TCP       45s
```

* Navigate to: **`http://20.124.50.80`** *(or whatever `EXTERNAL-IP` Azure assigns)*.

---

## 🎯 4 Questions Your Instructor Will Ask & How to Answer

### 1. "How do your microservices communicate with each other in Kubernetes?"
> **Answer**: *"Sir, they communicate using **Kubernetes CoreDNS Service Discovery**. The API Gateway accesses downstream services using internal DNS names: `http://catalog-service:8001`, `http://search-service:8002`, `http://recommendation-service:8003`, and `http://chatbot-service:8004`."*

### 2. "Why is only the API Gateway a LoadBalancer while the others are ClusterIP?"
> **Answer**: *"For **Security & Cloud Cost Optimization**. Internal services (Catalog, AI Search, Recommender, Chatbot) should never be directly exposed to the public internet. By keeping them as `ClusterIP`, they are completely isolated inside the private cluster network. Only the API Gateway is exposed via `LoadBalancer` on port 80 to accept customer web requests."*

### 3. "How does scaling work if AI Search gets high traffic?"
> **Answer**: *"Because each service is an independent microservice, we can scale `search-service-deployment` from 2 pods up to 20 pods independently using an HPA (Horizontal Pod Autoscaler) without wasting money scaling the Catalog or Chatbot services!"*

### 4. "How do you monitor the health of all 5 microservices?"
> **Answer**: *"Our API Gateway exposes an aggregated health check endpoint at `/api/health`. When queried, it performs parallel health probes across all 4 downstream services and returns an overall cluster status report."*
