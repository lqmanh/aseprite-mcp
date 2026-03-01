# Aseprite MCP

A Python MCP server for interacting with the Aseprite API

Demo where Cursor draws a cloud in aseprite using the MCP:

https://github.com/user-attachments/assets/572edf75-ab66-4700-87ee-d7d3d196c597

## Installation

### Prerequisites

- Python 3.13+
- `uv` package manager

### Instructions

#### Claude Code / Claude Desktop

Add to your Claude Code / Claude Desktop configurations:

```json
{
  "mcpServers": {
    "aseprite": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/aseprite-mcp",
        "run",
        "-m",
        "aseprite_mcp"
      ]
    }
  }
}
```

#### OpenCode

Add to your `opencode.json` (project root or `~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "aseprite": {
      "type": "local",
      "command": ["uv", "--directory", "/path/to/aseprite-mcp", "run", "-m", "aseprite_mcp"],
      "enabled": true
    }
  }
}
```
