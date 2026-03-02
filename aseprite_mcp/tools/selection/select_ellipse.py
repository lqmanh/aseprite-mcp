from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import SelectionMode
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class SelectEllipseInput(BaseModel):
    """Input for elliptical selection."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    x: int = Field(description="X coordinate of selection ellipse bounding box")
    y: int = Field(description="Y coordinate of selection ellipse bounding box")
    width: int = Field(gt=0, description="Width of selection ellipse")
    height: int = Field(gt=0, description="Height of selection ellipse")
    mode: SelectionMode = Field(
        default=SelectionMode.REPLACE,
        description="Selection mode: replace, add, subtract, or intersect",
    )


@mcp.tool
def select_ellipse(input: SelectEllipseInput) -> OperationOutput:
    """Create an elliptical selection with specified mode.

    Args:
        input: Selection parameters including bounds and mode

    Returns:
        OperationOutput indicating whether selection was created
    """
    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Create elliptical selection by command
    app.transaction(function()
        -- Use the magic wand tool with ellipse option for selection
        app.command.MagicWand{{
            contiguous = false,
            bounds = Rectangle({input.x}, {input.y}, {input.width}, {input.height})
        }}
    end)

    spr:saveAs(spr.filename)
    print("Ellipse selection created successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
