from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class DeselectInput(BaseModel):
    """Input for clearing selection."""

    filename: ExistingFile = Field(description="Path to the Aseprite file")


@mcp.tool
def deselect(input: DeselectInput) -> OperationOutput:
    """Clear the current selection.

    Args:
        input: Deselect request with filename

    Returns:
        OperationOutput indicating whether selection was cleared
    """
    script = """
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        spr.selection = Selection()
    end)

    spr:saveAs(spr.filename)
    print("Deselect completed successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
