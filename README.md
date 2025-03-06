# Google Docs MCP Server

A Model Context Protocol (MCP) server that enables AI assistants like Claude to seamlessly access and retrieve content from Google Docs.

## Features

- Search for documents in Google Drive
- Read content from Google Docs, Sheets, and Slides
- List available documents with filtering options
- Automatic format conversion (Docs → Markdown, Sheets → CSV, etc.)

## Installation

### Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account with Google Drive API enabled
- OAuth 2.0 client credentials

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/gdocs-mcp-server.git
   cd gdocs-mcp-server
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. Configure OAuth credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (Desktop application type)
   - Download the credentials JSON file
   - Save it as `credentials.json` in the `config` directory

## Detailed Setup Guide

### Creating Google Cloud Project and OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" at the top right and create a new project
3. Once in your project, go to "APIs & Services" > "Library"
4. Search for "Google Drive API" and enable it
5. Go to "APIs & Services" > "Credentials"
6. Click "Create Credentials" > "OAuth client ID"
7. Select "Desktop application" as the application type
8. Name your OAuth client (e.g., "Google Docs MCP")
9. Click "Create"
10. Download the JSON file by clicking the download icon
11. Rename the downloaded file to `credentials.json`
12. Create a `config` directory in your project root if it doesn't exist
13. Move the `credentials.json` file to the `config` directory

### First Run Authentication

When you first run the server, the following will happen:

1. The server will detect that you haven't authenticated yet
2. It will open a browser window asking you to sign in to your Google account
3. After signing in, Google will ask for permission to access your Drive files
4. Once you grant permission, you'll be redirected to a page showing an authentication code
5. The server will automatically receive this code and store a `token.json` file in your `config` directory
6. This `token.json` file will be used for future authentication, so you won't need to sign in again unless the token expires

## Usage

1. Start the server:
   ```bash
   gdocs-mcp
   ```

2. On first run, the server will prompt you to authorize access via a browser (as described above)

3. Configure Claude Desktop or another MCP client to connect to the server:
   ```json
   {
     "mcpServers": {
       "gdocs": {
         "command": "gdocs-mcp"
       }
     }
   }
   ```

4. You can now use the MCP tools in Claude or other compatible AI assistants to access your Google Docs

## Setting Up Claude with the MCP Server

1. Install Claude Desktop from the [Anthropic website](https://www.anthropic.com/claude)
2. Open Claude Desktop
3. Go to Settings > Advanced
4. Under "MCP Configuration," add the following configuration:
   ```json
   {
     "mcpServers": {
       "gdocs": {
         "command": "gdocs-mcp"
       }
     }
   }
   ```
5. Save settings and restart Claude
6. When interacting with Claude, you can now use prompts like "Search my Google Docs for [query]" or "Read the content of my Google Doc with ID [id]"

## Troubleshooting

### Authentication Issues

- If you encounter authentication errors, delete the `token.json` file in your `config` directory and restart the server
- Make sure your `credentials.json` file is correctly placed in the `config` directory
- Check that you've enabled the Google Drive API in your Google Cloud project

### Connection Issues

- Ensure the server is running when trying to use it with Claude
- Check if any firewall settings are blocking the local connections
- Verify your MCP configuration in Claude settings is correct

## Available Tools

### 1. gdocs_search

Search for documents in Google Drive.

**Parameters:**
- `query`: Search query string
- `max_results` (optional): Maximum number of results to return

### 2. gdocs_read

Read content from a Google Doc.

**Parameters:**
- `doc_id`: Google document ID
- `format` (optional): Output format (markdown, text, html)

### 3. gdocs_list

List documents in Google Drive.

**Parameters:**
- `folder_id` (optional): ID of the folder to list
- `max_results` (optional): Maximum number of results to return

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

## License

MIT 