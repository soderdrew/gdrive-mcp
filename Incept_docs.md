# Inception Documents

This file contains a chronological record of documents created during the project.

## January 17, 2025 - Project Setup Guide for Google Docs MCP Server

### Project Structure
```
gdocs-mcp-server/
├── pyproject.toml       # Project metadata and dependencies
├── README.md            # Project documentation
├── src/
│   └── gdocs_mcp/       # Main package directory
│       ├── __init__.py  # Package initialization
│       ├── server.py    # MCP server implementation
│       ├── auth.py      # Authentication handling
│       ├── drive.py     # Google Drive API interaction
│       └── tools/       # MCP tools implementation
│           ├── __init__.py
│           ├── search.py
│           ├── read.py
│           └── list.py
├── tests/               # Test directory
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_drive.py
│   └── test_tools.py
└── config/              # Configuration files
    └── default.json     # Default configuration
```

### Project Configuration (pyproject.toml)
```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "gdocs-mcp-server"
description = "MCP server for Google Docs integration"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
dynamic = ["version"]
dependencies = [
    "mcp",
    "google-api-python-client",
    "google-auth",
    "google-auth-oauthlib",
    "google-auth-httplib2",
    "markdown",
    "pydantic",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "isort",
    "mypy",
    "ruff",
]

[tool.setuptools_scm]

[tool.black]
line-length = 88
target-version = ["py39"]

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[project.scripts]
gdocs-mcp = "gdocs_mcp:main"
```

### Basic Server Implementation (server.py)
```python
"""
MCP server for Google Docs integration.
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from mcp.server import MCPServer
from mcp.tools import Tool, ToolResult, schema

from .auth import GoogleAuthManager
from .drive import GoogleDriveClient

logger = logging.getLogger(__name__)

class GoogleDocsMCPServer(MCPServer):
    """MCP server that provides access to Google Docs."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the server with optional configuration."""
        super().__init__()
        
        # Load configuration
        self.config = {}
        if config_path:
            with open(config_path, "r") as f:
                self.config = json.load(f)
        
        # Initialize auth and drive clients
        self.auth_manager = GoogleAuthManager(self.config.get("auth", {}))
        self.drive_client = GoogleDriveClient(self.auth_manager)
        
        # Register tools
        self.register_tools()
    
    def register_tools(self) -> None:
        """Register all tools with the server."""
        self.register_tool(
            "gdocs_search",
            self.gdocs_search,
            schema.Schema({
                "query": schema.String(description="Search query"),
                "max_results": schema.Optional(
                    schema.Integer(description="Maximum number of results to return")
                ),
            }),
            "Search for documents in Google Drive",
        )
        
        self.register_tool(
            "gdocs_read",
            self.gdocs_read,
            schema.Schema({
                "doc_id": schema.String(description="Google Doc ID to read"),
                "format": schema.Optional(
                    schema.String(
                        description="Output format (markdown, text, html)",
                        enum=["markdown", "text", "html"],
                    )
                ),
            }),
            "Read content from a Google Doc",
        )
        
        self.register_tool(
            "gdocs_list",
            self.gdocs_list,
            schema.Schema({
                "folder_id": schema.Optional(
                    schema.String(description="Folder ID to list documents from")
                ),
                "max_results": schema.Optional(
                    schema.Integer(description="Maximum number of results to return")
                ),
            }),
            "List Google Docs in a folder",
        )
    
    async def gdocs_search(self, query: str, max_results: int = 10) -> ToolResult:
        """Search for documents in Google Drive."""
        try:
            results = await self.drive_client.search_docs(query, max_results)
            return ToolResult(results)
        except Exception as e:
            logger.error(f"Error searching docs: {e}")
            return ToolResult(
                error=f"Failed to search documents: {str(e)}"
            )
    
    async def gdocs_read(self, doc_id: str, format: str = "markdown") -> ToolResult:
        """Read content from a Google Doc."""
        try:
            content = await self.drive_client.read_document(doc_id, format)
            return ToolResult(content)
        except Exception as e:
            logger.error(f"Error reading doc {doc_id}: {e}")
            return ToolResult(
                error=f"Failed to read document: {str(e)}"
            )
    
    async def gdocs_list(
        self, folder_id: Optional[str] = None, max_results: int = 20
    ) -> ToolResult:
        """List Google Docs in a folder."""
        try:
            docs = await self.drive_client.list_documents(folder_id, max_results)
            return ToolResult(docs)
        except Exception as e:
            logger.error(f"Error listing docs: {e}")
            return ToolResult(
                error=f"Failed to list documents: {str(e)}"
            )

async def main() -> None:
    """Run the server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Load config path from environment or use default
    config_path = Path("config/default.json")
    
    # Create and start server
    server = GoogleDocsMCPServer(config_path)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())

## January 24, 2025 - Phase 1 Testing Guide

### Testing Phase 1 Authentication

To verify that the authentication flow is working correctly, we can use the provided test scripts.

#### Prerequisites
- A Google Cloud Platform project with the Google Drive API enabled
- OAuth 2.0 client credentials downloaded as `credentials.json` and placed in the `config` directory

#### Test Steps

1. Create a default configuration file:
```bash
mkdir -p config
echo "{}" > config/default.json
```

2. Run the authentication test script:
```bash
python test_auth.py
```

The script should:
- Load the OAuth credentials
- Open a browser for authentication if no token exists
- Store the token after successful authentication
- Display token expiration information

3. Run the MCP tool test:
```bash
python test_mcp_tool.py
```

This will test the basic MCP tool functionality by listing Google Drive documents.

### Authentication Flow Verification Checklist

- [ ] Server initializes without errors
- [ ] Authentication URL is generated correctly
- [ ] OAuth callback is handled properly
- [ ] Tokens are stored securely
- [ ] Tokens are refreshed automatically when expired
- [ ] Configuration file is read from the correct location

Complete these tests before moving to implementing the remaining components in Phase 2 and beyond.

## GitHub Repository Creation
- **Date**: March 6, 2024
- **Repository Name**: mcp
- **Type**: Private Repository
- **Description**: Initial push of MCP project files
- **Actions Taken**: 
  - Created private GitHub repository
  - Added comprehensive .gitignore file
  - Pushed existing project files to repository 