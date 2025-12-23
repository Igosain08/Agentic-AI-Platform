#!/usr/bin/env python3
"""Test MCP server connection and Couchbase connectivity."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentic_ai.config.settings import get_settings
from agentic_ai.core.mcp_client import MCPClient
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)


async def test_mcp_connection():
    """Test MCP server connection."""
    print("=" * 60)
    print("🔍 TESTING MCP SERVER CONNECTION")
    print("=" * 60)
    
    settings = get_settings()
    
    # Check settings
    print(f"\n📋 Configuration:")
    print(f"  MCP Server Path: {settings.mcp_server_path}")
    print(f"  Couchbase Connection: {settings.cb_connection_string[:50]}..." if settings.cb_connection_string else "  Couchbase Connection: NOT SET")
    print(f"  Couchbase Username: {settings.cb_username}")
    print(f"  Couchbase Bucket: {settings.cb_bucket_name}")
    
    # Check if MCP server path exists
    if not settings.mcp_server_path:
        print("\n❌ ERROR: MCP_SERVER_PATH not set!")
        return False
    
    if not os.path.exists(settings.mcp_server_path):
        print(f"\n❌ ERROR: MCP server path does not exist: {settings.mcp_server_path}")
        return False
    
    print(f"\n✅ MCP server path exists: {settings.mcp_server_path}")
    
    # Test MCP client
    print("\n🔌 Testing MCP client connection...")
    client = MCPClient()
    
    try:
        async with client.session() as session:
            print("✅ MCP session opened successfully")
            
            # Try to list tools
            print("\n🔧 Testing tool loading...")
            from langchain_mcp_adapters.tools import load_mcp_tools
            tools = await load_mcp_tools(session)
            print(f"✅ Loaded {len(tools)} MCP tools")
            
            if tools:
                tool_names = [getattr(t, 'name', 'unknown') for t in tools]
                print(f"   Tool names: {', '.join(tool_names)}")
            
            # Try to execute a simple query
            if tools:
                print("\n📊 Testing Couchbase query...")
                # Find the query tool
                query_tool = None
                for tool in tools:
                    if 'query' in getattr(tool, 'name', '').lower():
                        query_tool = tool
                        break
                
                if query_tool:
                    print(f"   Found query tool: {getattr(query_tool, 'name', 'unknown')}")
                    try:
                        # Try a simple query
                        result = await query_tool.ainvoke({
                            "bucket_name": settings.cb_bucket_name,
                            "scope_name": "inventory",
                            "query": "SELECT COUNT(*) as count FROM `hotel` LIMIT 1"
                        })
                        print(f"✅ Query executed successfully!")
                        print(f"   Result: {str(result)[:200]}")
                        return True
                    except Exception as e:
                        print(f"❌ Query failed: {e}")
                        print(f"   Error type: {type(e).__name__}")
                        return False
                else:
                    print("⚠️  No query tool found")
                    return False
            else:
                print("⚠️  No tools loaded - cannot test query")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to MCP server")
        print(f"   Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    sys.exit(0 if success else 1)

