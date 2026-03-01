from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import ExistingFile, HexColor
from aseprite_mcp.mcp import mcp


class DrawLineInput(BaseModel):
    """Input for drawing a line."""

    filename: ExistingFile = Field(description="Path to the Aseprite file to modify")
    x1: int = Field(description="Starting x coordinate")
    y1: int = Field(description="Starting y coordinate")
    x2: int = Field(description="Ending x coordinate")
    y2: int = Field(description="Ending y coordinate")
    color: HexColor
    thickness: int = Field(default=1, ge=1, description="Line thickness in pixels")


@mcp.tool
def draw_line(input: DrawLineInput) -> OperationOutput:
    """Draw a line on the canvas.

    Args:
        input: Line drawing parameters including coordinates, color, and thickness

    Returns:
        OperationOutput indicating whether line was drawn
    """
    r, g, b, a = parse_hex_color(input.color)

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        local cel = app.activeCel
        if not cel then
            app.activeLayer = spr.layers[1]
            app.activeFrame = spr.frames[1]
            cel = app.activeCel
            if not cel then
                error("No active cel and couldn't create one")
            end
        end

        local color = Color({r}, {g}, {b}, {a})
        local brush = Brush()
        brush.size = {input.thickness}
        app.useTool({{
            tool="line",
            color=color,
            brush=brush,
            points={{Point({input.x1}, {input.y1}), Point({input.x2}, {input.y2})}}
        }})
    end)

    spr:saveAs(spr.filename)
    print("Line drawn successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
