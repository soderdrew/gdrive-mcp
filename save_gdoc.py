#!/usr/bin/env python
import os
import io
import json
import sys
import argparse
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Configure paths
TOKEN_PATH = 'config/token.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
OUTPUT_DIR = 'gdocs_cache'

def get_credentials():
    """Get valid credentials from the saved token."""
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as token_file:
            creds = Credentials.from_authorized_user_info(json.load(token_file), SCOPES)
            return creds
    else:
        raise Exception(f"Token file not found at {TOKEN_PATH}. Run authentication first.")

def list_documents():
    """List all Google Docs in the user's Drive."""
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)
    
    # Call the Drive v3 API to list files
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.document'",
        pageSize=50,
        fields="nextPageToken, files(id, name)"
    ).execute()
    
    items = results.get('files', [])
    return items

def find_document_by_name(name):
    """Find a document by name (partial match)."""
    docs = list_documents()
    
    # First check for exact match
    for doc in docs:
        if doc['name'].lower() == name.lower():
            return doc
    
    # Then check for partial matches
    matches = [doc for doc in docs if name.lower() in doc['name'].lower()]
    if matches:
        return matches[0]  # Return the first match
    
    return None

def read_document(doc_id):
    """Read the content of a Google Doc by ID."""
    creds = get_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    
    # For Google Docs, use the Docs API
    document = docs_service.documents().get(documentId=doc_id).execute()
    
    # Extract text from the document
    doc_content = document.get('body').get('content')
    text_content = extract_text_from_doc_content(doc_content)
    
    return text_content

def extract_text_from_doc_content(elements):
    """Helper function to extract text from Google Docs elements."""
    text = ""
    for element in elements:
        if 'paragraph' in element:
            for paragraph_element in element['paragraph']['elements']:
                if 'textRun' in paragraph_element:
                    text += paragraph_element['textRun']['content']
        elif 'table' in element:
            # Handle tables (simplified)
            for row in element['table'].get('tableRows', []):
                for cell in row.get('tableCells', []):
                    if 'content' in cell:
                        text += extract_text_from_doc_content(cell['content'])
        elif 'tableOfContents' in element:
            # Handle table of contents
            if 'content' in element['tableOfContents']:
                text += extract_text_from_doc_content(element['tableOfContents']['content'])
    return text

def save_document_to_file(doc_name, doc_id, content):
    """Save document content to a file."""
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Create a safe filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in doc_name)
    filename = os.path.join(OUTPUT_DIR, f"{safe_name}.txt")
    
    # Save the content to the file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Document: {doc_name} (ID: {doc_id})\n")
        f.write("-" * 80 + "\n\n")
        f.write(content)
    
    return filename

def main():
    parser = argparse.ArgumentParser(description='Save Google Docs content to local files')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all Google Docs')
    
    # Save command
    save_parser = subparsers.add_parser('save', help='Save a Google Doc to a local file')
    save_parser.add_argument('name', help='Name of the document to save')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute commands
    if args.command == 'list':
        docs = list_documents()
        print(f"Found {len(docs)} documents:")
        for doc in docs:
            print(f"- {doc['name']} (ID: {doc['id']})")
            
    elif args.command == 'save':
        doc = find_document_by_name(args.name)
        if doc:
            print(f"Saving '{doc['name']}' to file...")
            content = read_document(doc['id'])
            filename = save_document_to_file(doc['name'], doc['id'], content)
            print(f"Document saved to: {os.path.abspath(filename)}")
            print(f"You can now open this file in Cursor.")
        else:
            print(f"No document found with name '{args.name}'")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 