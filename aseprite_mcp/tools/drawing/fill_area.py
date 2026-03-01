from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import parse_hex_color
from aseprite_mcp.core.validation import ExistingFile, HexColor
from aseprite_mcp.mcp import mcp


class FillAreaInput(BaseModel):
    """Input for filling an area."""

    filename: ExistingFile = Field(description="Path to the Aseprite file to modify")
    x: int = Field(description="X coordinate to fill from")
    y: int = Field(description="Y coordinate to fill from")
    color: HexColor


@mcp.tool
def fill_area(input: FillAreaInput) -> OperationOutput:
    """Fill an area with color using the paint bucket tool.

    Args:
        input: Fill parameters including position and color

    Returns:
        OperationOutput indicating whether area was filled
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
        app.useTool({{
            tool="paint_bucket",
            color=color,
            points={{Point({input.x}, {input.y})}}
        }})
    end)

    spr:saveAs(spr.filename)
    print("Area filled successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
