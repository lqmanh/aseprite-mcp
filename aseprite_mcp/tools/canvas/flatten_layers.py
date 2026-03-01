from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class FlattenLayersInput(BaseModel):
    """Input for flattening layers."""

    filename: ExistingFile = Field(description="Path to the Aseprite file to modify")


@mcp.tool
def flatten_layers(input: FlattenLayersInput) -> OperationOutput:
    """Flatten all layers in a sprite into a single layer.

    Args:
        input: Flatten request with filename

    Returns:
        OperationOutput indicating whether layers were flattened
    """
    script = """
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        spr:flatten()
    end)

    spr:saveAs(spr.filename)
    print("Layers flattened successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
