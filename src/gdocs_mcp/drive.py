"""
Google Drive API client for interacting with Google Docs, Sheets, and Slides.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import sys

import googleapiclient.discovery
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import markdown

from .auth import GoogleAuthManager

logger = logging.getLogger(__name__)

# MIME types for Google Workspace documents
MIME_TYPES = {
    "document": "application/vnd.google-apps.document",
    "spreadsheet": "application/vnd.google-apps.spreadsheet",
    "presentation": "application/vnd.google-apps.presentation",
    "folder": "application/vnd.google-apps.folder",
}

class GoogleDriveClient:
    """Client for interacting with Google Drive API."""

    def __init__(self, auth_manager: GoogleAuthManager):
        """Initialize the Drive client with authentication manager."""
        self.auth_manager = auth_manager
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize the Google Drive API service."""
        try:
            credentials = self.auth_manager.get_credentials()
            if credentials:
                print(f"DEBUG: Got valid credentials, initializing service", file=sys.stderr)
                self.service = build("drive", "v3", credentials=credentials)
                logger.info("Google Drive API service initialized")
                print(f"DEBUG: Google Drive API service initialized successfully", file=sys.stderr)
            else:
                error_msg = "Failed to initialize Google Drive API service: No valid credentials"
                logger.error(error_msg)
                print(f"DEBUG ERROR: {error_msg}", file=sys.stderr)
        except Exception as e:
            error_msg = f"Failed to initialize Google Drive API service: {e}"
            logger.error(error_msg)
            print(f"DEBUG ERROR: {error_msg}", file=sys.stderr)
            self.service = None
    
    async def search_docs(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents in Google Drive.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of document metadata
        """
        if not self.service:
            self._initialize_service()
            if not self.service:
                raise RuntimeError("Google Drive API service not available")
        
        # Run the search in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._search_docs_sync, query, max_results
        )
    
    def _search_docs_sync(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Synchronous implementation of document search."""
        try:
            # Build search query to find only Google Docs, Sheets and Slides
            mime_filter = " or ".join([
                f"mimeType='{mime}'" 
                for mime in MIME_TYPES.values() 
                if mime != MIME_TYPES["folder"]
            ])
            full_query = f"({mime_filter}) and (name contains '{query}' or fullText contains '{query}')"
            
            # Execute the search
            results = self.service.files().list(
                q=full_query,
                pageSize=max_results,
                fields="files(id, name, mimeType, description, modifiedTime, webViewLink)",
            ).execute()
            
            # Process results
            files = results.get("files", [])
            return [
                {
                    "id": file["id"],
                    "name": file["name"],
                    "type": self._get_file_type(file["mimeType"]),
                    "modified": file.get("modifiedTime", ""),
                    "description": file.get("description", ""),
                    "url": file.get("webViewLink", ""),
                }
                for file in files
            ]
        
        except HttpError as error:
            logger.error(f"Error searching documents: {error}")
            raise RuntimeError(f"Failed to search Google Drive: {error}")
    
    async def read_document(self, doc_id: str, format: str = "markdown") -> Dict[str, Any]:
        """
        Read content from a Google Doc.
        
        Args:
            doc_id: Google document ID
            format: Output format (markdown, text, html)
            
        Returns:
            Document content and metadata
        """
        if not self.service:
            self._initialize_service()
            if not self.service:
                raise RuntimeError("Google Drive API service not available")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._read_document_sync, doc_id, format
        )
    
    def _read_document_sync(self, doc_id: str, format: str) -> Dict[str, Any]:
        """Synchronous implementation of document reading."""
        try:
            # Get file metadata
            file_metadata = self.service.files().get(
                fileId=doc_id, fields="id, name, mimeType, modifiedTime"
            ).execute()
            
            mime_type = file_metadata.get("mimeType", "")
            
            # Get content based on file type
            if mime_type == MIME_TYPES["document"]:
                content = self._export_document(doc_id, format)
            elif mime_type == MIME_TYPES["spreadsheet"]:
                content = self._export_spreadsheet(doc_id)
            elif mime_type == MIME_TYPES["presentation"]:
                content = self._export_presentation(doc_id)
            else:
                # Try to get content as text for other file types
                content = self._get_file_content(doc_id)
            
            return {
                "id": file_metadata["id"],
                "name": file_metadata["name"],
                "type": self._get_file_type(mime_type),
                "modified": file_metadata.get("modifiedTime", ""),
                "content": content,
            }
            
        except HttpError as error:
            logger.error(f"Error reading document {doc_id}: {error}")
            raise RuntimeError(f"Failed to read document from Google Drive: {error}")
    
    def _export_document(self, doc_id: str, format: str) -> str:
        """Export a Google Doc to the specified format."""
        export_mime = "text/plain"
        
        if format.lower() == "html":
            export_mime = "text/html"
        elif format.lower() == "markdown":
            # Export as HTML first, then convert to markdown
            html_content = self.service.files().export(
                fileId=doc_id, mimeType="text/html"
            ).execute().decode("utf-8")
            
            # Convert HTML to markdown
            return self._html_to_markdown(html_content)
        
        # Export document
        content = self.service.files().export(
            fileId=doc_id, mimeType=export_mime
        ).execute().decode("utf-8")
        
        return content
    
    def _export_spreadsheet(self, sheet_id: str) -> str:
        """Export a Google Sheet as CSV."""
        try:
            content = self.service.files().export(
                fileId=sheet_id, mimeType="text/csv"
            ).execute().decode("utf-8")
            return content
        except HttpError:
            # Fallback to plain text if CSV export fails
            content = self.service.files().export(
                fileId=sheet_id, mimeType="text/plain"
            ).execute().decode("utf-8")
            return content
    
    def _export_presentation(self, slide_id: str) -> str:
        """Export a Google Slides presentation as text."""
        try:
            content = self.service.files().export(
                fileId=slide_id, mimeType="text/plain"
            ).execute().decode("utf-8")
            return content
        except HttpError:
            # Fallback to PDF if text export fails
            logger.warning(
                "Failed to export presentation as text, handling this better "
                "would require more complex parsing."
            )
            return "[This presentation cannot be exported as text. Please view it in Google Slides.]"
    
    def _get_file_content(self, file_id: str) -> str:
        """Get content of a regular file from Google Drive."""
        try:
            # Download the file content
            request = self.service.files().get_media(fileId=file_id)
            content = request.execute()
            
            # Try to decode as text, if possible
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return "[Binary content not displayed]"
        
        except HttpError as error:
            logger.error(f"Error getting file content: {error}")
            return "[Error retrieving file content]"
    
    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to Markdown."""
        try:
            return markdown.markdown(html_content)
        except Exception as e:
            logger.error(f"Error converting HTML to Markdown: {e}")
            return html_content
    
    async def list_documents(
        self, folder_id: Optional[str] = None, max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        List documents in Google Drive, optionally filtered by folder.
        
        Args:
            folder_id: Optional folder ID to list documents from
            max_results: Maximum number of results to return
            
        Returns:
            List of document metadata
        """
        if not self.service:
            self._initialize_service()
            if not self.service:
                raise RuntimeError("Google Drive API service not available")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._list_documents_sync, folder_id, max_results
        )
    
    def _list_documents_sync(
        self, folder_id: Optional[str] = None, max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """Synchronous implementation of document listing."""
        try:
            # Build query to find only Google Docs, Sheets and Slides
            mime_filter = " or ".join([
                f"mimeType='{mime}'" 
                for mime in MIME_TYPES.values() 
                if mime != MIME_TYPES["folder"]
            ])
            
            # Add folder filter if specified
            if folder_id:
                query = f"({mime_filter}) and '{folder_id}' in parents"
            else:
                query = f"({mime_filter})"
            
            # Execute the query
            results = self.service.files().list(
                q=query,
                pageSize=max_results,
                fields="files(id, name, mimeType, description, modifiedTime, webViewLink)",
            ).execute()
            
            # Process results
            files = results.get("files", [])
            return [
                {
                    "id": file["id"],
                    "name": file["name"],
                    "type": self._get_file_type(file["mimeType"]),
                    "modified": file.get("modifiedTime", ""),
                    "description": file.get("description", ""),
                    "url": file.get("webViewLink", ""),
                }
                for file in files
            ]
        
        except HttpError as error:
            logger.error(f"Error listing documents: {error}")
            raise RuntimeError(f"Failed to list documents from Google Drive: {error}")
    
    def _get_file_type(self, mime_type: str) -> str:
        """Convert MIME type to a user-friendly file type."""
        mime_map = {
            MIME_TYPES["document"]: "document",
            MIME_TYPES["spreadsheet"]: "spreadsheet",
            MIME_TYPES["presentation"]: "presentation",
            MIME_TYPES["folder"]: "folder",
        }
        
        return mime_map.get(mime_type, "file") 