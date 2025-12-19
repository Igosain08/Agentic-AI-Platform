# Docker Troubleshooting Guide

## Issue: "Cannot connect to the Docker daemon"

This error means Docker Desktop is not running on your Mac.

## Solution

### 1. Start Docker Desktop

**Option A: From Applications**
- Open **Applications** folder
- Double-click **Docker** (or **Docker Desktop**)

**Option B: From Terminal**
```bash
open -a Docker
```

**Option C: From Spotlight**
- Press `Cmd + Space`
- Type "Docker"
- Press Enter

### 2. Wait for Docker to Start

Docker Desktop takes 10-30 seconds to start. You'll know it's ready when:
- Docker icon appears in menu bar (top right)
- Icon shows "Docker Desktop is running"

### 3. Verify Docker is Running

```bash
docker info
```

If this command works without errors, Docker is running!

### 4. Try docker-compose Again

```bash
docker-compose up -d
```

## Alternative: Run Services Locally (Without Docker)

If you prefer not to use Docker, you can run services individually:

### 1. Start FastAPI API

```bash
# Install dependencies
pip install -e .[dev]

# Start API
uvicorn src.agentic_ai.api.main:app --host 0.0.0.0 --port 8000
```

### 2. Start Prometheus

```bash
# Download Prometheus
# https://prometheus.io/download/

# Run Prometheus
./prometheus --config.file=prometheus/prometheus.yml
```

### 3. Start Grafana

```bash
# Download Grafana
# https://grafana.com/grafana/download

# Run Grafana
./grafana-server
```

### 4. Update Prometheus Config

Edit `prometheus/prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'agentic-ai-api'
    static_configs:
      - targets: ['localhost:8000']  # Changed from 'api:8000'
```

## Common Issues

### Docker Desktop Won't Start

1. **Check System Requirements**
   - macOS 10.15 or later
   - At least 4GB RAM
   - VirtualBox/VMware not running (conflicts)

2. **Restart Docker Desktop**
   - Quit Docker Desktop completely
   - Restart it

3. **Reset Docker Desktop**
   - Docker Desktop → Preferences → Reset to factory defaults
   - ⚠️ This will delete all containers and images

### Port Already in Use

If port 8000, 9090, or 3000 is already in use:

1. **Find what's using the port:**
```bash
lsof -i :8000
lsof -i :9090
lsof -i :3000
```

2. **Kill the process or change ports in docker-compose.yml**

### Docker Compose Not Found

Install Docker Compose:
```bash
# Docker Compose is included with Docker Desktop
# If missing, install separately:
pip install docker-compose
```

## Quick Check Script

Run this to check Docker status:

```bash
#!/bin/bash
if docker info >/dev/null 2>&1; then
    echo "✅ Docker is running"
    docker-compose --version
else
    echo "❌ Docker is not running"
    echo "Start Docker Desktop and try again"
fi
```

## Still Having Issues?

1. Check Docker Desktop logs:
   - Docker Desktop → Troubleshoot → View logs

2. Check system resources:
   - Docker Desktop → Preferences → Resources
   - Ensure enough CPU/Memory allocated

3. Restart your Mac (sometimes helps)

4. Reinstall Docker Desktop (last resort)

