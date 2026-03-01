# Aseprite MCP - Agent Guidelines

## Build, Test, and Lint Commands

```bash
# Install dependencies
uv sync

# Run the MCP server
uv run aseprite-mcp
# Or
python -m aseprite_mcp

# Lint and format code (ruff)
uv run ruff check .
uv run ruff check --fix .
uv run ruff format .

# Type checking (using ty)
uv run ty

# Run all tests (when pytest is configured)
uv run pytest

# Run a single test file
uv run pytest tests/test_file.py

# Run a single test
uv run pytest tests/test_file.py::test_function_name -v
```

## Code Style Guidelines

### Python Version

- Python 3.13+ required

### Imports

- Order: stdlib → third-party → local
- Use absolute imports for ALL packages including internal modules (e.g., `from aseprite_mcp.core.commands import ...`)
- NO relative imports allowed (e.g., `from ..core.commands import ...` is forbidden)
- Group imports: stdlib, third-party, local (separated by blank lines)

### Formatting (Ruff)

- 4-space indentation
- Double quotes for strings
- Line length: 88 characters (default)
- Run `ruff check .` and `ruff format .` before committing

### Type Hints

- Use type hints for all function parameters and return types
- Use built-in generics: `list`, `dict`, `set`, `tuple` instead of `typing.List`, `typing.Dict`, etc.
- Only import from `typing` when necessary (e.g., `Any`, `Union`, `Optional` when `|` syntax not applicable)

### Naming Conventions

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### MCP Tool Patterns

- Decorate with `@mcp.tool`
- Define input/output data as Pydantic models in the same file
- Name input models as `<ToolName>Input` and output models as `<ToolName>Output`
- Use shared models from `core/schemas/inputs.py` or `core/schemas/outputs.py` only when used by multiple tools
- Validate inputs using Pydantic annotated validators (`ExistingFile`, `HexColor`, `NonEmptyStr`,...)
- Return descriptive success/failure messages

### Error Handling

- In command layer: Return tuple `(success: bool, output: str)`
- In tool layer: Check success and return appropriate message
- Validate file paths before operations
- Use try/except in command runner for subprocess errors

### Lua Script Generation

- Build Lua scripts as Python strings with f-strings
- Embed variables directly in f-strings
- Use triple quotes for multi-line Lua scripts
- Follow Aseprite Lua API conventions

### Project Structure

- `aseprite_mcp/mcp.py`: MCP server instance
- `aseprite_mcp/tools/`: Tool implementations organized by category:
  - `animation/`: Animation tools (set_frame_duration, create_tag)
  - `canvas/`: Canvas management (create_canvas, add_layer, add_frame, etc.)
  - `drawing/`: Drawing tools (draw_pixels, draw_line, draw_rectangle, etc.)
  - `export/`: Export tools (export_sprite)
  - `inspection/`: Inspection tools (get_pixels)
  - `palette/`: Palette tools (get_palette, set_palette, etc.)
  - `selection/`: Selection tools (select_rectangle, select_all, etc.)
  - `transform/`: Transform tools (flip_sprite, rotate_sprite, etc.)
- `aseprite_mcp/core/`: Core utilities
  - `commands.py`: Aseprite command execution
  - `enums.py`: StrEnum types (ColorMode, AnimationDirection, etc.)
  - `schemas/`: Pydantic schemas
    - `inputs.py`: Shared input models
    - `outputs.py`: Shared output models (OperationOutput, PixelData, SpriteDimensions)
  - `types.py`: Additional type definitions
  - `utils.py`: Utility functions (parse_hex_color, escape_lua_str)
  - `validation.py`: Reusable Pydantic validators (ExistingFile, HexColor, NonEmptyStr)

### Security

- Never commit `.env` files or API keys
- Use `python-dotenv` for environment variables
- Read ASEPRITE_PATH from environment with fallback

## Dependencies

Core:

- `fastmcp`: MCP server framework
- `python-dotenv`: Environment variable management

Dev:

- `ruff`: Linting and formatting
- `ty`: Type checking

## Environment Setup

1. Copy `.env.example` to `.env`
2. Set `ASEPRITE_PATH` to your Aseprite executable path
3. Run `uv sync` to install dependencies
