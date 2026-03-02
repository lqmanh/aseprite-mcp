from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.utils import escape_lua_str
from aseprite_mcp.core.validation import FilePath, NonEmptyStr
from aseprite_mcp.mcp import mcp


class AddLayerInput(BaseModel):
    """Input for adding a new layer."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    layer_name: NonEmptyStr = Field(description="Name for the new layer")


class AddLayerOutput(BaseModel):
    """Response when a layer is created.

    Note: layer_index is 0-based in Python, converted from Lua's 1-based indexing.
    """

    layer_index: int = Field(description="0-based index of the created layer")
    layer_name: str = Field(description="Name of the created layer")


@mcp.tool
def add_layer(input: AddLayerInput) -> AddLayerOutput:
    """Add a new layer to an existing Aseprite sprite.

    Args:
        input: Layer addition parameters including filename and layer_name

    Returns:
        AddLayerOutput with the 0-based layer index and name
    """
    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    local layerIndex = 0
    app.transaction(function()
        local layer = spr:newLayer()
        layer.name = "{escape_lua_str(input.layer_name)}"
        -- Get the index of the newly created layer (1-based in Lua)
        for i, lyr in ipairs(spr.layers) do
            if lyr.name == "{escape_lua_str(input.layer_name)}" then
                layerIndex = i
                break
            end
        end
    end)

    spr:saveAs(spr.filename)
    print(string.format("%d,%s", layerIndex, "{escape_lua_str(input.layer_name)}"))
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        try:
            parts = output.strip().split(",", 1)
            lua_layer_index = int(parts[0])
            layer_index = lua_layer_index - 1
            layer_name = parts[1] if len(parts) > 1 else input.layer_name
            return AddLayerOutput(layer_index=layer_index, layer_name=layer_name)
        except (ValueError, IndexError):
            # Fallback if parsing fails
            return AddLayerOutput(layer_index=0, layer_name=input.layer_name)
    else:
        raise RuntimeError(f"Failed to add layer: {output}")
