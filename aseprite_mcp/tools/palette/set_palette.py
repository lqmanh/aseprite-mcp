from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import FilePath, HexColor
from aseprite_mcp.mcp import mcp


class SetPaletteInput(BaseModel):
    """Input for setting entire palette."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    colors: list[HexColor] = Field(min_length=1, max_length=256)


@mcp.tool
def set_palette(input: SetPaletteInput) -> OperationOutput:
    """Set the sprite's color palette to the specified colors.

    Args:
        input: Palette setting parameters with color array

    Returns:
        OperationOutput indicating whether palette was set
    """
    # Build color list for Lua
    color_entries = []
    for color in input.colors:
        r, g, b, a = parse_hex_color(color)
        color_entries.append(f"{{r={r},g={g},b={b},a={a}}}")

    colors_lua = "{\n" + ",\n".join(color_entries) + "\n}"

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Get or create palette
    local palette = spr.palettes[1]
    if not palette then
        error("No palette found")
    end

    -- Resize palette to match color count
    palette:resize({len(input.colors)})

    -- Set palette colors
    local colors = {colors_lua}

    for i, color in ipairs(colors) do
        palette:setColor(i - 1, Color(color.r, color.g, color.b, color.a))
    end

    spr:saveAs(spr.filename)
    print("Palette set successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
