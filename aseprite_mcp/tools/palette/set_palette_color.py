from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import FilePath, HexColor
from aseprite_mcp.mcp import mcp


class SetPaletteColorInput(BaseModel):
    """Input for setting a single palette color."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    index: int = Field(ge=0, le=255, description="Palette index (0-255)")
    color: HexColor


@mcp.tool
def set_palette_color(input: SetPaletteColorInput) -> OperationOutput:
    """Set a specific palette index to a color.

    Args:
        input: Single color setting parameters

    Returns:
        OperationOutput indicating whether color was set
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

    -- Validate index
    if {input.index} < 0 or {input.index} >= #palette then
        error(string.format("Palette index %d out of range (palette has %d colors)", {input.index}, #palette))
    end

    -- Set color at index
    palette:setColor({input.index}, Color({r}, {g}, {b}, {a}))

    spr:saveAs(spr.filename)
    print("Palette color set successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
