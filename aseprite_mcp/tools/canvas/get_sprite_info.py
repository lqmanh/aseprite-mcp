import json

from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import ColorMode
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class GetSpriteInfoInput(BaseModel):
    """Input for getting sprite information."""

    filename: FilePath = Field(description="Path to the Aseprite file")


class GetSpriteInfoOutput(BaseModel):
    """Sprite metadata response."""

    width: int = Field(description="Sprite width in pixels")
    height: int = Field(description="Sprite height in pixels")
    color_mode: ColorMode = Field(description="Color mode")
    frame_count: int = Field(description="Total number of animation frames")
    layer_count: int = Field(description="Total number of layers")
    layers: list[str] = Field(description="Names of all layers from bottom to top")


@mcp.tool
def get_sprite_info(input: GetSpriteInfoInput) -> GetSpriteInfoOutput:
    """Retrieve metadata about an existing Aseprite sprite.

    Args:
        input: Sprite info request with filename

    Returns:
        GetSpriteInfoOutput with dimensions, color mode, frame/layer counts, and layer names
    """
    script = """
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Map color mode enum to string
    local colorModeStr = "rgb"
    if spr.colorMode == ColorMode.GRAYSCALE then
        colorModeStr = "grayscale"
    elseif spr.colorMode == ColorMode.INDEXED then
        colorModeStr = "indexed"
    end

    -- Collect layer names
    local layers = {}
    for i, layer in ipairs(spr.layers) do
        table.insert(layers, layer.name)
    end

    -- Format as JSON-like output
    local output = string.format([[{
        "width": %d,
        "height": %d,
        "color_mode": "%s",
        "frame_count": %d,
        "layer_count": %d,
        "layers": ["%s"]
    }]],
        spr.width,
        spr.height,
        colorModeStr,
        #spr.frames,
        #spr.layers,
        table.concat(layers, '","')
    )

    print(output)
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        try:
            data = json.loads(output.strip())
            return GetSpriteInfoOutput(**data)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse sprite info: {e}")
    else:
        raise RuntimeError(f"Failed to get sprite info: {output}")
