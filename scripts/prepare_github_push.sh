#!/bin/bash
# Script to prepare and push changes to GitHub

set -e

echo "📋 Preparing GitHub Push..."
echo ""

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not a git repository"
    exit 1
fi

# Show current status
echo "📊 Current Status:"
git status --short | head -10
echo ""

# Ask for confirmation
read -p "Continue with adding files? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Add core files
echo "📦 Adding files..."
git add README.md
git add src/
git add tests/
git add scripts/
git add docker-compose.yml
git add requirements.txt pyproject.toml
git add prometheus/
git add grafana/
git add docs/

# Add documentation (optional summary files)
git add MONITORING_IMPLEMENTATION_SUMMARY.md 2>/dev/null || true
git add TESTING_COMPLETE_SUMMARY.md 2>/dev/null || true
git add MLFLOW_IMPLEMENTATION_SUMMARY.md 2>/dev/null || true
git add GITHUB_PUSH_CHECKLIST.md 2>/dev/null || true

echo "✅ Files added"
echo ""

# Show what will be committed
echo "📝 Files to be committed:"
git status --short
echo ""

# Ask for commit message
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="feat: Add MLflow tracking, comprehensive testing, and Prometheus/Grafana monitoring

- MLflow integration for experiment tracking and P99 latency monitoring
- 34+ comprehensive tests (edge cases, service failures, ground truth)
- Prometheus + Grafana production monitoring with custom metrics
- Pipeline performance breakdown (Embedding vs LLM latency)
- Request latency heatmap visualization
- Updated README with all features"
fi

# Commit
echo "💾 Committing..."
git commit -m "$commit_msg"

echo ""
echo "✅ Committed successfully!"
echo ""
echo "🚀 Next step: Push to GitHub"
echo "   Run: git push origin main"
echo ""

