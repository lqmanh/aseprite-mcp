from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import escape_lua_str
from aseprite_mcp.core.validation import FilePath, NonEmptyStr
from aseprite_mcp.mcp import mcp


class DeleteLayerInput(BaseModel):
    """Input for deleting a layer."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    layer_name: NonEmptyStr = Field(description="Name of the layer to delete")


@mcp.tool
def delete_layer(input: DeleteLayerInput) -> OperationOutput:
    """Delete a layer from an existing sprite. Cannot delete the last remaining layer.

    Args:
        input: Layer deletion parameters including filename and layer_name

    Returns:
        OperationOutput indicating whether the layer was deleted
    """
    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Check if this is the last layer
    if #spr.layers == 1 then
        error("Cannot delete the last layer")
    end

    -- Find layer by name
    local layer = nil
    for i, lyr in ipairs(spr.layers) do
        if lyr.name == "{escape_lua_str(input.layer_name)}" then
            layer = lyr
            break
        end
    end

    if not layer then
        error("Layer not found: {escape_lua_str(input.layer_name)}")
    end

    app.transaction(function()
        spr:deleteLayer(layer)
    end)

    spr:saveAs(spr.filename)
    print("Layer deleted successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
