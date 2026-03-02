import json

from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.validation import FilePath, HexColor
from aseprite_mcp.mcp import mcp


class GetPaletteInput(BaseModel):
    """Input for getting palette."""

    filename: FilePath = Field(description="Path to the Aseprite file")


class GetPaletteOutput(BaseModel):
    """Palette information response."""

    colors: list[HexColor]
    size: int = Field(description="Number of colors in the palette")


@mcp.tool
def get_palette(input: GetPaletteInput) -> GetPaletteOutput:
    """Retrieve the current sprite palette as an array of hex colors.

    Args:
        input: Palette request with filename

    Returns:
        GetPaletteOutput with colors array and size (colors include alpha: #RRGGBBAA)
    """
    script = """
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Get palette
    local palette = spr.palettes[1]
    if not palette then
        error("No palette found")
    end

    -- Extract colors as hex strings with alpha
    local colors = {}
    for i = 0, #palette - 1 do
        local color = palette:getColor(i)
        local hex = string.format("#%02X%02X%02X%02X", color.red, color.green, color.blue, color.alpha)
        table.insert(colors, hex)
    end

    -- Format as JSON
    local colorList = '["' .. table.concat(colors, '","') .. '"]'
    local output = string.format('{"colors":%s,"size":%d}', colorList, #palette)

    print(output)
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        try:
            data = json.loads(output.strip())
            return GetPaletteOutput(**data)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse palette data: {e}")
    else:
        raise RuntimeError(f"Failed to get palette: {output}")
