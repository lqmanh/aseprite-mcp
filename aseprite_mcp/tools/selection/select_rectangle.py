from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import SelectionMode
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class SelectRectangleInput(BaseModel):
    """Input for rectangular selection."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    x: int = Field(description="X coordinate of selection rectangle")
    y: int = Field(description="Y coordinate of selection rectangle")
    width: int = Field(gt=0, description="Width of selection rectangle")
    height: int = Field(gt=0, description="Height of selection rectangle")
    mode: SelectionMode = Field(
        default=SelectionMode.REPLACE,
        description="Selection mode: replace, add, subtract, or intersect",
    )


@mcp.tool
def select_rectangle(input: SelectRectangleInput) -> OperationOutput:
    """Create a rectangular selection with specified mode (replace/add/subtract/intersect).

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

    local rect = Rectangle({input.x}, {input.y}, {input.width}, {input.height})

    app.transaction(function()
        local mode = "{input.mode}"
        if mode == "replace" then
            spr.selection = Selection(rect)
        elseif mode == "add" then
            if spr.selection.isEmpty then
                spr.selection = Selection(rect)
            else
                spr.selection:add(Selection(rect))
            end
        elseif mode == "subtract" then
            if not spr.selection.isEmpty then
                spr.selection:subtract(Selection(rect))
            end
        elseif mode == "intersect" then
            if not spr.selection.isEmpty then
                spr.selection:intersect(Selection(rect))
            end
        end
    end)

    spr:saveAs(spr.filename)
    print("Rectangle selection created successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
