# 🚀 Deploy API to Railway (Easiest!)

## Quick Steps (5 minutes)

### 1. Sign up for Railway
- Go to [railway.app](https://railway.app)
- Sign up with GitHub (free tier available)

### 2. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repo: `Igosain08/Agentic-AI-Platform`

### 3. Configure Deployment
Railway will auto-detect your Dockerfile. If not:
- **Build Command**: (leave empty, uses Dockerfile)
- **Start Command**: `uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port $PORT`

### 4. Add Environment Variables
Click on your service → **Variables** tab → Add these:

```bash
# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=your_actual_openai_key_here

# Couchbase Configuration
CB_CONNECTION_STRING=your_couchbase_connection_string
CB_USERNAME=your_couchbase_username
CB_PASSWORD=your_couchbase_password
CB_BUCKET_NAME=travel-sample

# MCP Server Path (for Railway)
MCP_SERVER_PATH=/app/mcp-server-couchbase

# Redis (optional - Railway can add Redis service)
REDIS_HOST=localhost
REDIS_PORT=6379

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 5. Deploy!
- Railway will automatically build and deploy
- You'll get a URL like: `https://your-app.up.railway.app`

### 6. Update Streamlit
In your Streamlit app (or Streamlit Cloud), set API URL to:
```
https://your-app.up.railway.app
```

## Important Notes

### MCP Server Path Issue
The MCP server path needs to be adjusted for Railway. You have two options:

**Option A: Include MCP server in Docker image**
- Modify Dockerfile to copy mcp-server-couchbase
- Or use a different path

**Option B: Use Railway's file system**
- Set `MCP_SERVER_PATH=/app/mcp-server-couchbase`
- Make sure the path exists in the container

### Port Configuration
Railway uses `$PORT` environment variable automatically. The Dockerfile already exposes port 8000, which Railway will use.

## Alternative: Render (Also Easy)

### Steps:
1. Go to [render.com](https://render.com)
2. **New** → **Web Service**
3. Connect GitHub repo
4. Settings:
   - **Build Command**: `docker build -t agentic-ai-platform .`
   - **Start Command**: `docker run -p $PORT:8000 agentic-ai-platform`
   - Or use: `uvicorn agentic_ai.api.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as above)
6. Deploy!

## Quick Checklist

- [ ] Railway account created
- [ ] Project created from GitHub
- [ ] Environment variables added
- [ ] Deployment started
- [ ] Got API URL
- [ ] Updated Streamlit API URL

## Troubleshooting

### Build Fails
- Check Dockerfile is correct
- Check all dependencies in pyproject.toml

### MCP Server Not Found
- Verify `MCP_SERVER_PATH` is correct
- May need to include mcp-server-couchbase in Docker image

### Connection Issues
- Check API URL is correct (no trailing slash)
- Verify API is running: `https://your-app.up.railway.app/api/v1/health`

## After Deployment

Your API will be at: `https://your-app.up.railway.app`

Update Streamlit to use this URL instead of `localhost:8005`!

