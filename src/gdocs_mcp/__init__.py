"""
Google Docs MCP Server - A Model Context Protocol server for Google Docs integration.
"""
import asyncio
from pathlib import Path
import os
import sys

__version__ = "0.1.0"

def main():
    """Run the server."""
    # Get config path from environment variables or use default
    config_path = os.environ.get("GDOCS_MCP_CONFIG")
    if config_path:
        config_path = Path(config_path)
    else:
        # Try to find config in default locations
        possible_paths = [
            Path("config/default.json"),
            Path.home() / ".config" / "gdocs-mcp" / "config.json",
            Path(__file__).parent.parent.parent / "config" / "default.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
    
    # Run the server
    asyncio.run(_main(config_path))

async def _main(config_path=None):
    """Async entry point for the server."""
    # Import here to avoid circular imports
    from .server import GoogleDocsMCPServer, main as server_main
    
    if config_path:
        # Create and start the server with config
        server = GoogleDocsMCPServer(config_path)
        await server.run_stdio_async()
    else:
        # Use the server's main function
        await server_main(config_path)

if __name__ == "__main__":
    sys.exit(main()) 