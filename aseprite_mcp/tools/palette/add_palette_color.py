import json

from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import FilePath, HexColor
from aseprite_mcp.mcp import mcp


class AddPaletteColorInput(BaseModel):
    """Input for adding a palette color."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    color: HexColor


class AddPaletteColorOutput(BaseModel):
    """Response with a palette index.

    Note: color_index is 0-based in Python, matching Lua's 0-based palette indexing.
    """

    color_index: int = Field(description="0-based index of the color in the palette")


@mcp.tool
def add_palette_color(input: AddPaletteColorInput) -> AddPaletteColorOutput:
    """Add a new color to the palette.

    Args:
        input: Color addition parameters

    Returns:
        AddPaletteColorOutput with the index of the newly added color
    """
    r, g, b, a = parse_hex_color(input.color)

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Get palette
    local palette = spr.palettes[1]
    if not palette then
        error("No palette found")
    end

    -- Check if palette is at maximum size
    if #palette >= 256 then
        error("Palette is already at maximum size (256 colors)")
    end

    -- Add new color to palette
    local newIndex = #palette
    palette:resize(#palette + 1)
    palette:setColor(newIndex, Color({r}, {g}, {b}, {a}))

    spr:saveAs(spr.filename)

    -- Output JSON with color_index
    local output = string.format('{{"color_index":%d}}', newIndex)
    print(output)
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        try:
            data = json.loads(output.strip())
            return AddPaletteColorOutput(**data)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse result: {e}")
    else:
        raise RuntimeError(f"Failed to add palette color: {output}")
