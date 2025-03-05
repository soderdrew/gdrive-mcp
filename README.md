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

## Usage

1. Start the server:
   ```bash
   gdocs-mcp
   ```

2. On first run, the server will prompt you to authorize access via a browser

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