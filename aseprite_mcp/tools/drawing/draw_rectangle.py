from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import ExistingFile, HexColor
from aseprite_mcp.mcp import mcp


class DrawRectangleInput(BaseModel):
    """Input for drawing a rectangle."""

    filename: ExistingFile = Field(description="Path to the Aseprite file to modify")
    x: int = Field(description="Top-left x coordinate")
    y: int = Field(description="Top-left y coordinate")
    width: int = Field(gt=0, description="Width of the rectangle")
    height: int = Field(gt=0, description="Height of the rectangle")
    color: HexColor
    fill: bool = Field(default=False, description="Whether to fill the rectangle")


@mcp.tool
def draw_rectangle(input: DrawRectangleInput) -> OperationOutput:
    """Draw a rectangle on the canvas.

    Args:
        input: Rectangle drawing parameters including bounds, color, and fill option

    Returns:
        OperationOutput indicating whether rectangle was drawn
    """
    r, g, b, a = parse_hex_color(input.color)

    tool = "filled_rectangle" if input.fill else "rectangle"

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
            points={{Point({input.x}, {input.y}), Point({input.x + input.width}, {input.y + input.height})}}
        }})
    end)

    spr:saveAs(spr.filename)
    print("Rectangle drawn successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
