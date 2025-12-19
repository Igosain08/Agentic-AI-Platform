#!/bin/bash
# Script to manually import Grafana dashboard if auto-provisioning doesn't work

GRAFANA_URL="http://localhost:3000"
GRAFANA_USER="admin"
GRAFANA_PASSWORD="admin"
DASHBOARD_FILE="grafana/dashboards/agentic-ai-platform.json"

echo "📊 Importing Grafana Dashboard..."

# Get API key or use basic auth
AUTH=$(echo -n "$GRAFANA_USER:$GRAFANA_PASSWORD" | base64)

# Check if dashboard file exists
if [ ! -f "$DASHBOARD_FILE" ]; then
    echo "❌ Dashboard file not found: $DASHBOARD_FILE"
    exit 1
fi

# Read dashboard JSON
DASHBOARD_JSON=$(cat "$DASHBOARD_FILE")

# Import dashboard via API
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Basic $AUTH" \
    -d "{\"dashboard\":$DASHBOARD_JSON,\"overwrite\":true}" \
    "$GRAFANA_URL/api/dashboards/db")

# Check if import was successful
if echo "$RESPONSE" | grep -q '"status":"success"'; then
    echo "✅ Dashboard imported successfully!"
    echo "   View at: $GRAFANA_URL/d/agentic-ai-platform"
else
    echo "❌ Failed to import dashboard"
    echo "Response: $RESPONSE"
    exit 1
fi

