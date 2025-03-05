#!/usr/bin/env python
"""
Test script for Google Docs MCP Server tools.
"""
import asyncio
import logging
from pathlib import Path

from gdocs_mcp.server import GoogleDocsMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

async def test_mcp_tool():
    """Test the MCP tools functionality."""
    # Create server instance with default config
    config_path = Path("config/default.json")
    server = GoogleDocsMCPServer(config_path)
    
    # Test a simple list operation (should work without parameters)
    print("\nTesting gdocs_list tool...")
    result = await server.gdocs_list()
    
    if not result.error:
        print("\n✅ MCP tool test successful!")
        print(f"Found {len(result.value)} documents")
        if result.value:
            print("\nFirst few documents:")
            for doc in result.value[:3]:
                print(f" - {doc.get('name', 'Unnamed')} ({doc.get('id', 'No ID')})")
    else:
        print("\n❌ MCP tool test failed:")
        print(f"Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_mcp_tool()) 