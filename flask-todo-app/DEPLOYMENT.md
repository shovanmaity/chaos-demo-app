# 🚀 Deployment Guide - Flask Todo App

This guide covers Docker and Kubernetes deployment for the Flask Todo App.

## 📦 Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t flask-todo-app:latest .

# Verify the image
docker images | grep flask-todo-app
```

### Run Docker Container

```bash
# Run with default settings
docker run -d \
  --name flask-todo-app \
  -p 5000:5000 \
  flask-todo-app:latest

# Run with custom environment variables
docker run -d \
  --name flask-todo-app \
  -p 5000:5000 \
  -e APPLICATION_NAME=my-todo-app \
  -e EMISSARY_URL=http://emissary:8080 \
  flask-todo-app:latest

# Check logs
docker logs -f flask-todo-app

# Access the app
open http://localhost:5000
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  todo-app:
    build: .
    image: flask-todo-app:latest
    container_name: flask-todo-app
    ports:
      - "5000:5000"
    environment:
      - APPLICATION_NAME=flask-todo-app
      - EMISSARY_URL=http://emissary:8080
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

Run with Docker Compose:

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- Docker image built and available

### Option 1: Local Kubernetes (Minikube/Kind)

#### Step 1: Start Minikube (if using)

```bash
minikube start
eval $(minikube docker-env)
```

#### Step 2: Build Image in Minikube

```bash
# Build image inside minikube
docker build -t flask-todo-app:latest .
```

#### Step 3: Deploy to Kubernetes

```bash
# Apply all resources
kubectl apply -f deployment.yaml

# Verify deployment
kubectl get all -n todo-app

# Check pods
kubectl get pods -n todo-app -w

# Check logs
kubectl logs -f deployment/flask-todo-app -n todo-app
```

#### Step 4: Access the Application

**Option A: NodePort**
```bash
# Get the NodePort URL (if using minikube)
minikube service flask-todo-app-nodeport -n todo-app

# Or manually
kubectl get svc -n todo-app
# Access at: http://<node-ip>:30500
```

**Option B: Port Forward**
```bash
kubectl port-forward -n todo-app svc/flask-todo-app-service 5000:80
# Access at: http://localhost:5000
```

**Option C: Ingress**
```bash
# Enable ingress (minikube)
minikube addons enable ingress

# Add to /etc/hosts
echo "$(minikube ip) todo-app.local" | sudo tee -a /etc/hosts

# Access at: http://todo-app.local
```

### Option 2: Cloud Kubernetes (GKE, EKS, AKS)

#### Step 1: Push Image to Registry

```bash
# Tag for your registry
docker tag flask-todo-app:latest <your-registry>/flask-todo-app:latest

# Push to registry
docker push <your-registry>/flask-todo-app:latest
```

#### Step 2: Update deployment.yaml

Edit `deployment.yaml` and update the image:

```yaml
spec:
  containers:
  - name: flask-todo-app
    image: <your-registry>/flask-todo-app:latest
    imagePullPolicy: Always
```

#### Step 3: Deploy

```bash
kubectl apply -f deployment.yaml
```

#### Step 4: Access via LoadBalancer

Update service type to LoadBalancer:

```bash
kubectl patch svc flask-todo-app-service -n todo-app -p '{"spec": {"type": "LoadBalancer"}}'

# Get external IP
kubectl get svc -n todo-app flask-todo-app-service
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APPLICATION_NAME` | Application identifier | `flask-todo-app` |
| `EMISSARY_URL` | Chaos emissary service URL | `http://localhost:8080` |

### Resource Limits

Default resource configuration:

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Auto-Scaling

HPA (Horizontal Pod Autoscaler) is configured:
- Min replicas: 2
- Max replicas: 10
- CPU threshold: 70%
- Memory threshold: 80%

## 📊 Monitoring

### Check Application Health

```bash
# Via kubectl
kubectl get pods -n todo-app

# Check health endpoint
kubectl port-forward -n todo-app svc/flask-todo-app-service 5000:80
curl http://localhost:5000/health

# Check stats
curl http://localhost:5000/api/stats
```

### View Logs

```bash
# All pods
kubectl logs -f -l app=flask-todo-app -n todo-app

# Specific pod
kubectl logs -f <pod-name> -n todo-app

# Previous logs (if pod crashed)
kubectl logs --previous <pod-name> -n todo-app
```

### Describe Resources

```bash
kubectl describe deployment flask-todo-app -n todo-app
kubectl describe pod <pod-name> -n todo-app
kubectl describe svc flask-todo-app-service -n todo-app
```

## 🔄 Updates and Rollbacks

### Update Deployment

```bash
# Update image
kubectl set image deployment/flask-todo-app \
  flask-todo-app=flask-todo-app:v2 \
  -n todo-app

# Check rollout status
kubectl rollout status deployment/flask-todo-app -n todo-app

# View rollout history
kubectl rollout history deployment/flask-todo-app -n todo-app
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/flask-todo-app -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/flask-todo-app --to-revision=2 -n todo-app
```

## 🧹 Cleanup

### Remove Kubernetes Resources

```bash
# Delete all resources
kubectl delete -f deployment.yaml

# Or delete namespace
kubectl delete namespace todo-app
```

### Remove Docker Resources

```bash
# Stop and remove container
docker stop flask-todo-app
docker rm flask-todo-app

# Remove image
docker rmi flask-todo-app:latest
```

## 🐛 Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Check events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n todo-app
```

### Image Pull Errors

```bash
# Verify image exists
docker images | grep flask-todo-app

# Check imagePullPolicy
kubectl get deployment flask-todo-app -n todo-app -o yaml | grep imagePullPolicy
```

### Health Check Failures

```bash
# Test health endpoint manually
kubectl port-forward <pod-name> -n todo-app 5000:5000
curl http://localhost:5000/health

# Check probe configuration
kubectl describe pod <pod-name> -n todo-app | grep -A 5 Liveness
```

## 📝 Notes

- **In-Memory Storage**: Data is lost when pods restart
- **5-Minute Expiration**: Todos automatically expire after 5 minutes
- **Stateless**: App is stateless and can scale horizontally
- **No Persistence**: Consider adding Redis/Database for production use

## 🔗 Useful Commands

```bash
# Quick status check
kubectl get all -n todo-app

# Watch pods
kubectl get pods -n todo-app -w

# Execute command in pod
kubectl exec -it <pod-name> -n todo-app -- /bin/bash

# Copy files from pod
kubectl cp todo-app/<pod-name>:/app/app.py ./app.py

# Scale manually
kubectl scale deployment flask-todo-app --replicas=5 -n todo-app
```

## 🚀 Production Recommendations

1. **Use a proper image registry** (Docker Hub, GCR, ECR, ACR)
2. **Add persistent storage** for production data
3. **Configure TLS/SSL** for secure connections
4. **Set up monitoring** (Prometheus, Grafana)
5. **Configure logging** (ELK stack, Loki)
6. **Use secrets** for sensitive data
7. **Implement CI/CD** pipeline
8. **Add network policies** for security
9. **Configure resource quotas** per namespace
10. **Set up backup and disaster recovery**

---

**Happy Deploying! 🚀**
