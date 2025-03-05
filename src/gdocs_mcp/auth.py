"""
Authentication module for Google Drive API.
"""
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

# Default scopes for Google Drive API
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
]

class GoogleAuthManager:
    """Manage authentication with Google Drive API."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the auth manager with configuration."""
        self.config = config
        self.credentials = None
        
        # Get the project root directory (where the config file is located)
        config_path = Path(config.get("config_path", ""))
        if config_path.exists():
            # If the config path is like /path/to/project/config/default.json
            # We need to go up two levels to get the project root
            if "config" in config_path.parts and config_path.name.endswith(".json"):
                self.project_root = config_path.parent.parent
            else:
                self.project_root = config_path.parent
        else:
            # Fallback to the directory structure in the user's project
            self.project_root = Path(__file__).parent.parent.parent
        
        print(f"DEBUG: Project root directory: {self.project_root}", file=sys.stderr)
        
        # Use absolute paths based on project root
        self.credentials_path = self.project_root / "config" / "credentials.json"
        self.token_path = self.project_root / "config" / "token.json"
        
        print(f"DEBUG: Using credentials path: {self.credentials_path}", file=sys.stderr)
        print(f"DEBUG: Using token path: {self.token_path}", file=sys.stderr)
        
        # Check if credentials file exists, if not try other common locations
        if not self.credentials_path.exists():
            print(f"DEBUG: Credentials file not found at primary location, trying alternatives", file=sys.stderr)
            alternative_paths = [
                Path("config/credentials.json"),  # Relative to current directory
                Path.home() / ".config" / "gdocs-mcp" / "credentials.json",  # User config directory
                Path(__file__).parent.parent.parent / "config" / "credentials.json",  # Project root
                Path(os.getcwd()) / "config" / "credentials.json",  # Current working directory
            ]
            
            for alt_path in alternative_paths:
                print(f"DEBUG: Checking alternative path: {alt_path}", file=sys.stderr)
                if alt_path.exists():
                    self.credentials_path = alt_path
                    print(f"DEBUG: Found credentials at: {self.credentials_path}", file=sys.stderr)
                    break
        
        # Similarly check for token file in alternative locations
        token_filename = "token.json"
        if not self.token_path.exists():
            print(f"DEBUG: Token file not found at primary location, will create if needed", file=sys.stderr)
            # If we found credentials in an alternative location, try to use the same directory for token
            if self.credentials_path != self.project_root / "config" / "credentials.json":
                self.token_path = self.credentials_path.parent / token_filename
                print(f"DEBUG: Updated token path to: {self.token_path}", file=sys.stderr)
        
        # Get scopes from config or use default
        self.scopes = self.config.get(
            "scopes", ["https://www.googleapis.com/auth/drive.readonly"]
        )
        
        # Load credentials on initialization
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load and validate credentials."""
        try:
            print(f"DEBUG: Looking for token at {self.token_path}", file=sys.stderr)
            if self.token_path.exists():
                print(f"DEBUG: Token file exists, loading credentials", file=sys.stderr)
                # Load existing token if available
                self.credentials = Credentials.from_authorized_user_info(
                    json.loads(self.token_path.read_text()),
                    self.scopes,
                )
                
                # Check if credentials need refreshing
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    print(f"DEBUG: Credentials expired, refreshing", file=sys.stderr)
                    request = google.auth.transport.requests.Request()
                    self.credentials.refresh(request)
                    self._save_token()
            
            # If no valid credentials, need to authenticate
            if not self.credentials or not self.credentials.valid:
                print(f"DEBUG: No valid credentials found, initiating OAuth flow", file=sys.stderr)
                logger.info("No valid credentials found. Initiating OAuth flow.")
                self._authenticate()
        
        except Exception as e:
            error_msg = f"Error loading credentials: {e}"
            logger.error(error_msg)
            print(f"DEBUG ERROR: {error_msg}", file=sys.stderr)
            self.credentials = None
    
    def _authenticate(self) -> None:
        """Run the OAuth authentication flow."""
        try:
            # Check if credentials file exists
            print(f"DEBUG: Looking for credentials at {self.credentials_path}", file=sys.stderr)
            if not self.credentials_path.exists():
                error_msg = f"Credentials file not found at {self.credentials_path}. Please download OAuth credentials from Google Cloud Console."
                logger.error(error_msg)
                print(f"DEBUG ERROR: {error_msg}", file=sys.stderr)
                return
            
            # Start OAuth flow
            print(f"DEBUG: Starting OAuth flow", file=sys.stderr)
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, self.scopes
            )
            self.credentials = flow.run_local_server(port=0)
            
            # Save the obtained token
            self._save_token()
            
            logger.info("Successfully authenticated with Google Drive API.")
            print(f"DEBUG: Successfully authenticated with Google Drive API", file=sys.stderr)
        
        except Exception as e:
            error_msg = f"Authentication failed: {e}"
            logger.error(error_msg)
            print(f"DEBUG ERROR: {error_msg}", file=sys.stderr)
            self.credentials = None
    
    def _save_token(self) -> None:
        """Save the token to disk."""
        if self.credentials:
            try:
                # Create parent directory if it doesn't exist
                self.token_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save token
                token_data = self.credentials.to_json()
                self.token_path.write_text(token_data)
                logger.info(f"Token saved to {self.token_path}")
                print(f"DEBUG: Token saved to {self.token_path}", file=sys.stderr)
            except Exception as e:
                error_msg = f"Failed to save token: {e}"
                logger.error(error_msg)
                print(f"DEBUG ERROR: {error_msg}", file=sys.stderr)
    
    def get_credentials(self) -> Optional[Credentials]:
        """Get the current credentials, refreshing if necessary."""
        if not self.credentials:
            self._authenticate()
        
        return self.credentials 