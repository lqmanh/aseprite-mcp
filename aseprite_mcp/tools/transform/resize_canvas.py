from pydantic import BaseModel, Field, field_validator

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import SpriteDimensions
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class ResizeCanvasInput(BaseModel):
    """Input for resizing canvas."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    width: int = Field(gt=0, le=65535, description="New canvas width")
    height: int = Field(gt=0, le=65535, description="New canvas height")
    anchor: str = Field(
        default="center",
        description="Anchor position: center, top_left, top_right, bottom_left, or bottom_right",
    )

    @field_validator("anchor")
    @classmethod
    def validate_anchor(cls, v: str) -> str:
        allowed = {"center", "top_left", "top_right", "bottom_left", "bottom_right"}
        if v.lower() not in allowed:
            raise ValueError(f"anchor must be one of: {', '.join(allowed)}")
        return v.lower()


@mcp.tool
def resize_canvas(input: ResizeCanvasInput) -> SpriteDimensions:
    """Resize the canvas without scaling content.

    Content is positioned according to the anchor point.

    Args:
        input: Resize parameters including dimensions and anchor

    Returns:
        SpriteDimensions with the new canvas dimensions
    """
    # Calculate padding based on anchor
    anchor_padding = {
        "center": (
            "math.floor((newWidth - oldWidth) / 2)",
            "math.floor((newHeight - oldHeight) / 2)",
            "math.ceil((newWidth - oldWidth) / 2)",
            "math.ceil((newHeight - oldHeight) / 2)",
        ),
        "top_left": ("0", "0", "newWidth - oldWidth", "newHeight - oldHeight"),
        "top_right": ("newWidth - oldWidth", "0", "0", "newHeight - oldHeight"),
        "bottom_left": ("0", "newHeight - oldHeight", "newWidth - oldWidth", "0"),
        "bottom_right": ("newWidth - oldWidth", "newHeight - oldHeight", "0", "0"),
    }

    left, top, right, bottom = anchor_padding[input.anchor]

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    local oldWidth = spr.width
    local oldHeight = spr.height
    local newWidth = {input.width}
    local newHeight = {input.height}

    app.transaction(function()
        app.command.CanvasSize{{
            left = {left},
            top = {top},
            right = {right},
            bottom = {bottom}
        }}
    end)

    spr:saveAs(spr.filename)
    print(string.format("%d,%d", spr.width, spr.height))
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        try:
            width, height = map(int, output.strip().split(","))
            return SpriteDimensions(width=width, height=height)
        except ValueError:
            # Fallback to input dimensions if parsing fails
            return SpriteDimensions(width=input.width, height=input.height)
    else:
        raise RuntimeError(f"Failed to resize canvas: {output}")
