# Kubernetes Deployment Guide

## Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Docker registry access

## Deployment Steps

### 1. Create Namespace
```bash
kubectl create namespace agentic-ai
```

### 2. Create Secrets
```bash
kubectl create secret generic agentic-ai-secrets \
  --from-literal=nebius-api-key=your-key \
  --from-literal=couchbase-connection-string=your-connection \
  --from-literal=couchbase-username=your-username \
  --from-literal=couchbase-password=your-password \
  -n agentic-ai
```

### 3. Deploy Redis
```bash
kubectl apply -f k8s/redis-deployment.yaml
```

### 4. Deploy Application
```bash
kubectl apply -f k8s/app-deployment.yaml
```

### 5. Deploy Service
```bash
kubectl apply -f k8s/app-service.yaml
```

## Health Checks
The application includes liveness and readiness probes:
- Liveness: `/api/v1/live`
- Readiness: `/api/v1/ready`

## Scaling
```bash
kubectl scale deployment agentic-ai-platform --replicas=3 -n agentic-ai
```

