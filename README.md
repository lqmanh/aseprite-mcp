# Aseprite MCP

A Python MCP server for interacting with the Aseprite API

Demo where Cursor draws a cloud in aseprite using the MCP:

https://github.com/user-attachments/assets/572edf75-ab66-4700-87ee-d7d3d196c597

## Local Installation

### Prerequisites

- Python 3.13+
- `uv` package manager

### Installation:

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "/opt/homebrew/bin/uv",
      "args": ["--directory", "/path/to/repo", "run", "-m", "aseprite_mcp"]
    }
  }
}
```
