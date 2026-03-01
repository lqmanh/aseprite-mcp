from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import FlipDirection, TransformTarget
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class FlipSpriteInput(BaseModel):
    """Input for flipping sprite."""

    filename: ExistingFile = Field(description="Path to the Aseprite file")
    direction: FlipDirection = Field(description="Flip direction")
    target: TransformTarget = Field(
        default=TransformTarget.SPRITE,
        description="What to flip: sprite, layer, or cel",
    )


@mcp.tool
def flip_sprite(input: FlipSpriteInput) -> OperationOutput:
    """Flip a sprite, layer, or cel horizontally or vertically.

    Args:
        input: Flip parameters including direction and target scope

    Returns:
        OperationOutput indicating whether flip was applied
    """
    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        app.command.Flip{{
            orientation = "{input.direction}",
            target = "{input.target}"
        }}
    end)

    spr:saveAs(spr.filename)
    print("Sprite flipped {input.direction} successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
