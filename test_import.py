#!/usr/bin/env python
"""
Test basic imports for the MCP module.
"""

def test_imports():
    """Test importing various modules."""
    try:
        import mcp
        print("✅ Successfully imported mcp")
    except ImportError as e:
        print(f"❌ Failed to import mcp: {e}")
    
    try:
        from mcp.server import MCPServer
        print("✅ Successfully imported MCPServer")
    except ImportError as e:
        print(f"❌ Failed to import MCPServer: {e}")
    
    try:
        import gdocs_mcp
        print("✅ Successfully imported gdocs_mcp")
    except ImportError as e:
        print(f"❌ Failed to import gdocs_mcp: {e}")

if __name__ == "__main__":
    test_imports() 