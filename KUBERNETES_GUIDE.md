# 🚢 Kubernetes Deployment Guide: ShopSmart AI

> **Goal**: Step-by-step instructions to build the Docker image, deploy the application to Kubernetes, and access it through the public **LoadBalancer**.

---

## 🧭 The Complete Architecture

```
                      [ External Internet User ]
                                  │
                                  ▼ (HTTP Port 80)
                ┌───────────────────────────────────┐
                │ Kubernetes Service (LoadBalancer) │
                │ Name: shopsmart-ai-service        │
                └─────────────────┬─────────────────┘
                                  │ (targetPort: 8000)
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
      [ Pod Replica #1 ]                [ Pod Replica #2 ]
      • FastAPI AI Backend              • FastAPI AI Backend
      • Semantic Vector Search          • Semantic Vector Search
      • Recommender Engine              • Recommender Engine
      • Interactive Chatbot             • Interactive Chatbot
```

---

## 🚀 Step-by-Step Deployment Commands

### Step 1: Build the Docker Image
Inside the project root directory:

```bash
docker build -t shopsmart-ai:v1 .
```

*(If deploying to Azure Kubernetes Service (AKS), tag and push to your Azure Container Registry):*
```bash
# Tag for your Azure Container Registry (ACR)
docker tag shopsmart-ai:v1 <your-acr-name>.azurecr.io/shopsmart-ai:v1

# Push to ACR
docker push <your-acr-name>.azurecr.io/shopsmart-ai:v1
```

---

### Step 2: Deploy to Kubernetes

Deploy both the **Deployment** and the **LoadBalancer Service** with one command:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

### Step 3: Verify Pods & Health Probes

Check that both pod replicas are created and running:

```bash
kubectl get pods -l app=shopsmart-ai
```

**Expected Output:**
```text
NAME                                       READY   STATUS    RESTARTS   AGE
shopsmart-ai-deployment-64d898bfcb-7x8zk   1/1     Running   0          25s
shopsmart-ai-deployment-64d898bfcb-m9r2l   1/1     Running   0          25s
```

*(Notice: `READY 1/1` means our `/api/health` Readiness Probe passed successfully!)*

---

### Step 4: Get the External LoadBalancer Public IP

Check the status of your LoadBalancer:

```bash
kubectl get service shopsmart-ai-service
```

**Expected Output (in Azure AKS or Cloud):**
```text
NAME                   TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)        AGE
shopsmart-ai-service   LoadBalancer   10.0.182.45    20.124.50.80    80:31250/TCP   45s
```

* Open your browser and navigate to: **`http://20.124.50.80`**  
  *(Replace with your actual `EXTERNAL-IP`!)*

#### 💡 If Testing on Local Minikube:
Local Minikube doesn't have an Azure cloud router, so run:
```bash
minikube service shopsmart-ai-service
# Or in a second terminal:
minikube tunnel
```

---

## 🎯 4 Questions Your Instructor Will Ask & How to Answer

### 1. "Why did you use `replicas: 2` in `deployment.yaml`?"
> **Answer**: *"For High Availability and zero downtime. If Pod #1 crashes or is restarting during an update, Kubernetes automatically routes all user traffic to Pod #2 without any interruption for the customer."*

### 2. "In `service.yaml`, what is the difference between `port: 80` and `targetPort: 8000`?"
> **Answer**: *"Port 80 is the external public HTTP port that customers connect to. TargetPort 8000 is the internal private port inside the container where our FastAPI web server is actively listening."*

### 3. "What is the purpose of the Liveness and Readiness probes in your deployment?"
> **Answer**: 
> * *"The **Readiness Probe** prevents user traffic from hitting a pod until its AI vector catalog has finished loading into memory."*
> * *"The **Liveness Probe** continuously monitors `/api/health`. If the Python process ever freezes or enters a deadlock, Kubernetes automatically kills and restarts the pod."*

### 4. "Why did you use `type: LoadBalancer` instead of `ClusterIP`?"
> **Answer**: *"ClusterIP only allows internal traffic inside the Kubernetes cluster. `type: LoadBalancer` provisions a public cloud IP address in Azure/AWS so external web customers can access our store over the internet."*
