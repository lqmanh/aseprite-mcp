from pydantic import BaseModel, Field

from aseprite_mcp.core.validation import HexColor


class PixelData(BaseModel):
    """Single pixel information."""

    x: int = Field(description="X coordinate in sprite space")
    y: int = Field(description="Y coordinate in sprite space")
    color: HexColor


class OperationOutput(BaseModel):
    """Standard response for operations."""

    success: bool = Field(description="Whether the operation succeeded")
    message: str | None = Field(
        default=None, description="Additional message or error details"
    )


class SpriteDimensions(BaseModel):
    """Response with sprite dimensions."""

    width: int = Field(description="Sprite width in pixels")
    height: int = Field(description="Sprite height in pixels")
