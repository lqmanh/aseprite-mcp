from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import SpriteDimensions
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class CropSpriteInput(BaseModel):
    """Input for cropping sprite."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    x: int = Field(ge=0, description="Crop region X coordinate")
    y: int = Field(ge=0, description="Crop region Y coordinate")
    width: int = Field(gt=0, description="Crop region width")
    height: int = Field(gt=0, description="Crop region height")


@mcp.tool
def crop_sprite(input: CropSpriteInput) -> SpriteDimensions:
    """Crop a sprite to a specified rectangular region.

    Args:
        input: Crop parameters including region bounds

    Returns:
        SpriteDimensions with the new dimensions after cropping
    """
    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Validate crop bounds
    if {input.x} < 0 or {input.y} < 0 then
        error("Crop position must be non-negative")
    end

    if {input.width} <= 0 or {input.height} <= 0 then
        error("Crop dimensions must be positive")
    end

    if {input.x} + {input.width} > spr.width or {input.y} + {input.height} > spr.height then
        error(string.format("Crop bounds exceed sprite dimensions (sprite: %dx%d, crop: %d,%d,%dx%d)",
            spr.width, spr.height, {input.x}, {input.y}, {input.width}, {input.height}))
    end

    app.transaction(function()
        -- Select the crop region
        spr.selection = Selection(Rectangle({input.x}, {input.y}, {input.width}, {input.height}))
        -- Crop to selection
        app.command.CropSprite()
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
        raise RuntimeError(f"Failed to crop sprite: {output}")
