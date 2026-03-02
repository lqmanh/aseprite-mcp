from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import FilePath, HexColor
from aseprite_mcp.mcp import mcp


class DrawCircleInput(BaseModel):
    """Input for drawing a circle."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    center_x: int = Field(description="X coordinate of circle center")
    center_y: int = Field(description="Y coordinate of circle center")
    radius: int = Field(gt=0, description="Radius of the circle in pixels")
    color: HexColor
    fill: bool = Field(default=False, description="Whether to fill the circle")


@mcp.tool
def draw_circle(input: DrawCircleInput) -> OperationOutput:
    """Draw a circle on the canvas.

    Args:
        input: Circle drawing parameters including center, radius, color, and fill option

    Returns:
        OperationOutput indicating whether circle was drawn
    """
    r, g, b, a = parse_hex_color(input.color)

    tool = "filled_ellipse" if input.fill else "ellipse"

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
        app.useTool({{
            tool="{tool}",
            color=color,
            points={{
                Point({input.center_x - input.radius}, {input.center_y - input.radius}),
                Point({input.center_x + input.radius}, {input.center_y + input.radius})
            }}
        }})
    end)

    spr:saveAs(spr.filename)
    print("Circle drawn successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
