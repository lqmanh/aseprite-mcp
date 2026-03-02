from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput, PixelData
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class DrawPixelsInput(BaseModel):
    """Input for drawing pixels."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    pixels: list[PixelData] = Field(description="List of pixel data to draw")


@mcp.tool
def draw_pixels(input: DrawPixelsInput) -> OperationOutput:
    """Draw pixels on the canvas with specified colors.

    Args:
        input: Pixel drawing parameters including filename and pixel data

    Returns:
        OperationOutput indicating whether pixels were drawn
    """
    script = """
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        local cel = app.activeCel
        if not cel then
            -- If no active cel, create one
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = app.activeCel
            if not cel then
                error("No active cel and couldn't create one")
            end
        end

        local img = cel.image
    """

    # Add pixel drawing commands
    for pixel in input.pixels:
        r, g, b, a = parse_hex_color(pixel.color)

        script += f"""
        img:putPixel({pixel.x}, {pixel.y}, Color({r}, {g}, {b}, {a}))
        """

    script += """
    end)

    spr:saveAs(spr.filename)
    print("Pixels drawn successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
