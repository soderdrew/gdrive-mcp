#!/usr/bin/env python
"""
Example MCP server using MCP SDK 1.3.0.
"""
import asyncio
import logging
from typing import Optional

from mcp.server import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

class ExampleServer(FastMCP):
    """Example MCP server."""
    
    def __init__(self):
        """Initialize the server."""
        super().__init__()
        
        # Register tools
        self.tool(
            name="hello_world",
            description="Responds with a greeting message",
        )(self.hello_world)
    
    async def hello_world(self, name: Optional[str] = "World") -> str:
        """Respond with a greeting message."""
        logger.info(f"Greeting {name}")
        return f"Hello, {name}!"

async def main() -> None:
    """Run the server."""
    server = ExampleServer()
    
    # Run using stdio interface (command line)
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main()) 