from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class SelectAllInput(BaseModel):
    """Input for selecting all."""

    filename: FilePath = Field(description="Path to the Aseprite file")


@mcp.tool
def select_all(input: SelectAllInput) -> OperationOutput:
    """Select the entire canvas.

    Args:
        input: Select all request with filename

    Returns:
        OperationOutput indicating whether selection was created
    """
    script = """
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        spr.selection = Selection(Rectangle(0, 0, spr.width, spr.height))
    end)

    spr:saveAs(spr.filename)
    print("Select all completed successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
