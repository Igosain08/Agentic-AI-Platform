# 🚀 Deployment Guide

This guide covers how to deploy the Agentic AI Platform for production use and resume showcasing.

## Quick Deployment Options

### Option 1: Railway (Recommended - Easiest)
**Free tier available, perfect for demos**

1. **Sign up**: Go to [railway.app](https://railway.app)
2. **Create new project**: Click "New Project"
3. **Deploy from GitHub**: Connect your GitHub repo
4. **Add environment variables**: Copy from `.env.sample`
5. **Deploy**: Railway auto-detects Dockerfile and deploys

**Pros**: Free tier, auto-deploys on git push, easy setup
**Cons**: Free tier has limits

### Option 2: Render
**Free tier with limitations**

1. **Sign up**: Go to [render.com](https://render.com)
2. **New Web Service**: Connect GitHub repo
3. **Configure**:
   - Build Command: `docker build -t agentic-ai-platform .`
   - Start Command: `docker run -p 8000:8005 agentic-ai-platform`
   - Environment: Add all variables from `.env.sample`
4. **Deploy**: Click "Deploy"

**Pros**: Free tier, simple setup
**Cons**: Spins down after inactivity (free tier)

### Option 3: Fly.io
**Good free tier, always-on**

1. **Install flyctl**: `curl -L https://fly.io/install.sh | sh`
2. **Login**: `fly auth login`
3. **Launch**: `fly launch` (in project directory)
4. **Set secrets**: `fly secrets set OPENAI_API_KEY=xxx CB_CONNECTION_STRING=xxx ...`
5. **Deploy**: `fly deploy`

**Pros**: Always-on free tier, good performance
**Cons**: Slightly more complex setup

### Option 4: AWS/GCP/Azure (Production)
**For serious production deployments**

See `docs/deployment/kubernetes.md` for detailed Kubernetes deployment.

## Environment Variables Needed

Copy these from your `.env` file to your hosting platform:

```bash
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Couchbase Configuration
CB_CONNECTION_STRING=your_connection_string
CB_USERNAME=your_username
CB_PASSWORD=your_password
CB_BUCKET_NAME=travel-sample

# MCP Server
MCP_SERVER_PATH=/app/mcp-server-couchbase

# Redis (if using external Redis)
REDIS_HOST=your_redis_host
REDIS_PORT=6379

# Optional
CACHE_ENABLED=true
METRICS_ENABLED=true
```

## Docker Deployment

The project includes a `Dockerfile` ready for deployment:

```bash
# Build
docker build -t agentic-ai-platform .

# Run locally
docker run -p 8000:8005 --env-file .env agentic-ai-platform

# Or with docker-compose
docker-compose up
```

## What to Include on Resume

### If Deployed (Live Demo):
```
🔗 Live Demo: https://your-app.railway.app
📦 GitHub: https://github.com/Igosain08/Agentic-AI-Platform
```

### If Not Deployed (GitHub Only):
```
📦 GitHub: https://github.com/Igosain08/Agentic-AI-Platform
💻 Local Demo Available
```

### Best Practice:
**Include both GitHub link AND live demo if possible**

## Resume Link Format

### Option A: With Live Demo
```
Agentic AI Platform
🔗 https://your-app.railway.app | 📦 https://github.com/yourusername/agentic-ai-platform
```

### Option B: GitHub Only
```
Agentic AI Platform
📦 https://github.com/yourusername/agentic-ai-platform
```

## Quick Setup for Railway (Recommended)

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Production-ready agentic AI platform"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Go to railway.app
   - New Project → Deploy from GitHub
   - Select your repo
   - Add environment variables
   - Deploy!

3. **Get your URL**: Railway gives you a URL like `https://your-app.up.railway.app`

4. **Add to resume**: Include both GitHub and Railway links

## Notes

- **Free tiers** are perfect for resume demos
- **Environment variables** are critical - make sure all are set
- **MCP server path** may need adjustment for Docker (use `/app/mcp-server-couchbase`)
- **Redis** can use Railway's Redis addon or external service

## Troubleshooting

### MCP Server Not Found
- Ensure `MCP_SERVER_PATH` points to correct location in container
- May need to copy mcp-server-couchbase into Docker image

### Database Connection Issues
- Verify Couchbase connection string and credentials
- Check IP whitelist in Couchbase Capella

### Port Issues
- Railway/Render use PORT environment variable
- Update Dockerfile to use `$PORT` if needed

