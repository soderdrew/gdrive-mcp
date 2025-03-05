"""
Entry point for running the gdocs_mcp package as a module.
"""
import asyncio
import sys
import os
from pathlib import Path

from .server import GoogleDocsMCPServer

async def main():
    """Run the Google Docs MCP server."""
    # Print current working directory for debugging
    cwd = os.getcwd()
    print(f"DEBUG: Current working directory: {cwd}", file=sys.stderr)
    
    # Get config path from environment or use default
    config_path = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
        print(f"DEBUG: Using config path from command line: {config_path}", file=sys.stderr)
    else:
        # Try common config locations
        possible_paths = [
            Path("config/default.json"),
            Path.home() / ".config" / "gdocs-mcp" / "config.json",
            Path(__file__).parent.parent.parent / "config" / "default.json",
            Path(cwd) / "config" / "default.json",
        ]
        
        for path in possible_paths:
            print(f"DEBUG: Checking for config at: {path}", file=sys.stderr)
            if path.exists():
                config_path = path
                print(f"DEBUG: Found config at: {config_path}", file=sys.stderr)
                break
    
    if not config_path or not config_path.exists():
        print(f"DEBUG ERROR: Could not find config file", file=sys.stderr)
    
    # Create and start server
    print(f"DEBUG: Creating server with config: {config_path}", file=sys.stderr)
    server = GoogleDocsMCPServer(config_path)
    print(f"DEBUG: Starting server", file=sys.stderr)
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main()) 