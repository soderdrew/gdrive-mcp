"""
MCP server for Google Docs integration.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

from mcp.server import FastMCP

from .auth import GoogleAuthManager
from .drive import GoogleDriveClient

logger = logging.getLogger(__name__)

class GoogleDocsMCPServer(FastMCP):
    """MCP server for Google Docs integration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the server with configuration."""
        super().__init__()
        
        # Load configuration
        self.config = {}
        if config_path and config_path.exists():
            print(f"DEBUG: Loading config from {config_path}", file=sys.stderr)
            try:
                self.config = json.loads(config_path.read_text())
                # Store the config path for use in auth manager
                self.config["config_path"] = str(config_path)
            except Exception as e:
                print(f"DEBUG ERROR: Failed to load config: {e}", file=sys.stderr)
                logging.error(f"Failed to load config: {e}")
        
        # Initialize auth manager and drive client
        self.auth_manager = GoogleAuthManager(self.config)
        self.drive_client = GoogleDriveClient(self.auth_manager)
        
        # Register tools
        self.tool(
            name="gdocs_search",
            description="Search for Google Docs by query",
        )(self.gdocs_search)
        
        self.tool(
            name="gdocs_read",
            description="Read a Google Doc by ID",
        )(self.gdocs_read)
        
        self.tool(
            name="gdocs_list",
            description="List Google Docs in a folder",
        )(self.gdocs_list)
        
        logging.info("Initializing server...")
    
    async def gdocs_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for Google Docs matching a query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results
        """
        logger.info(f"Searching for Google Docs with query: {query}")
        results = await self.drive_client.search_docs(query, max_results)
        return {"results": results}
    
    async def gdocs_read(self, doc_id: str, format: str = "markdown") -> Dict[str, Any]:
        """
        Read a Google Doc by ID.
        
        Args:
            doc_id: Google Doc ID
            format: Format to return the document in (markdown, text, html)
            
        Returns:
            Dictionary with document content
        """
        logger.info(f"Reading Google Doc with ID: {doc_id}")
        content = await self.drive_client.read_document(doc_id, format)
        return {"content": content}
    
    async def gdocs_list(
        self, folder_id: Optional[str] = None, max_results: int = 20
    ) -> Dict[str, Any]:
        """
        List Google Docs in a folder.
        
        Args:
            folder_id: Google Drive folder ID (None for root)
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with list of documents
        """
        logger.info(f"Listing Google Docs in folder: {folder_id or 'root'}")
        docs = await self.drive_client.list_documents(folder_id, max_results)
        return {"docs": docs}

async def main(config_path: Optional[Path] = None) -> None:
    """Run the server with optional configuration."""
    server = GoogleDocsMCPServer(config_path)
    
    # Run using stdio interface (command line)
    await server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main()) 