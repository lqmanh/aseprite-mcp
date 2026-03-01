from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class MoveSelectionInput(BaseModel):
    """Input for moving selection."""

    filename: ExistingFile = Field(description="Path to the Aseprite file")
    dx: int = Field(description="Horizontal offset in pixels (can be negative)")
    dy: int = Field(description="Vertical offset in pixels (can be negative)")


@mcp.tool
def move_selection(input: MoveSelectionInput) -> OperationOutput:
    """Move the current selection by a specified offset. Does not move pixel content.

    Args:
        input: Move parameters including offset values

    Returns:
        OperationOutput indicating whether selection was moved
    """
    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    if spr.selection.isEmpty then
        error("No active selection")
    end

    app.transaction(function()
        local bounds = spr.selection.bounds
        spr.selection = Selection(Rectangle(
            bounds.x + {input.dx},
            bounds.y + {input.dy},
            bounds.width,
            bounds.height
        ))
    end)

    spr:saveAs(spr.filename)
    print("Selection moved successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
