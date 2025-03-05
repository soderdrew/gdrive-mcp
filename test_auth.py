#!/usr/bin/env python
"""
Test script for Google authentication.
"""
import asyncio
import json
import logging
import os
from pathlib import Path
import sys

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gdocs_mcp.auth import GoogleAuthManager
from gdocs_mcp.drive import GoogleDriveClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Path to config directory
CONFIG_DIR = Path("config")
CREDENTIALS_PATH = CONFIG_DIR / "credentials.json"
TOKEN_PATH = CONFIG_DIR / "token.json"

async def test_auth():
    """Test Google authentication."""
    
    # Check if credentials file exists
    if not CREDENTIALS_PATH.exists():
        logger.error(f"Credentials file not found at {CREDENTIALS_PATH}")
        logger.error("Please download your credentials.json from Google Cloud Console.")
        return False
    
    # Initialize authentication manager
    auth_config = {
        "credentials_path": str(CREDENTIALS_PATH),
        "token_path": str(TOKEN_PATH),
        "scopes": [
            "https://www.googleapis.com/auth/drive.readonly",
        ],
    }
    
    auth_manager = GoogleAuthManager(auth_config)
    
    # Get credentials (this will prompt user to authenticate if needed)
    credentials = auth_manager.get_credentials()
    
    if not credentials:
        logger.error("Failed to get credentials")
        return False
    
    logger.info("Authentication successful!")
    
    # Initialize Drive client and test a simple operation
    drive_client = GoogleDriveClient(auth_manager)
    
    # Test search docs operation
    try:
        results = await drive_client.search_docs("test", max_results=3)
        logger.info(f"Found {len(results)} documents")
        for doc in results:
            logger.info(f"Document: {doc['name']} (ID: {doc['id']})")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Drive API: {e}")
        return False

async def main():
    """Main entry point."""
    success = await test_auth()
    if success:
        logger.info("Authentication test completed successfully!")
    else:
        logger.error("Authentication test failed!")

if __name__ == "__main__":
    asyncio.run(main()) 