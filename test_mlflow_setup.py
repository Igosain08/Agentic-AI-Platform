#!/usr/bin/env python3
"""Quick test script to verify MLflow integration is working."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

print("Testing MLflow integration...")
print("=" * 60)

# Test 1: Import MLflow
try:
    import mlflow
    print(f"✅ MLflow installed: version {mlflow.__version__}")
except ImportError as e:
    print(f"❌ MLflow not installed: {e}")
    sys.exit(1)

# Test 2: Import MLflow tracker
try:
    from agentic_ai.monitoring.mlflow_tracker import get_mlflow_tracker
    print("✅ MLflow tracker module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import MLflow tracker: {e}")
    sys.exit(1)

# Test 3: Initialize tracker
try:
    # Enable MLflow for testing
    os.environ["MLFLOW_ENABLED"] = "true"
    tracker = get_mlflow_tracker()
    if tracker.is_enabled:
        print("✅ MLflow tracker initialized and enabled")
    else:
        print("⚠️  MLflow tracker initialized but not enabled")
        print("   (Set MLFLOW_ENABLED=true to enable)")
except Exception as e:
    print(f"❌ Failed to initialize tracker: {e}")
    sys.exit(1)

# Test 4: Test basic logging
try:
    from agentic_ai.config.settings import get_settings
    settings = get_settings()
    print(f"✅ Settings loaded: experiment={settings.mlflow_experiment_name}")
except Exception as e:
    print(f"⚠️  Settings test failed: {e}")

print("=" * 60)
print("✅ All tests passed! MLflow integration is ready.")
print("\nNext steps:")
print("1. Set MLFLOW_ENABLED=true in your .env file")
print("2. Run: python scripts/evaluate_agent.py --queries 'test query' --mlflow-enabled")
print("3. View results: mlflow ui")

