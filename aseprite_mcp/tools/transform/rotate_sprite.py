from pydantic import BaseModel, Field, field_validator

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import TransformTarget
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class RotateSpriteInput(BaseModel):
    """Input for rotating sprite."""

    filename: ExistingFile = Field(description="Path to the Aseprite file")
    angle: int = Field(description="Rotation angle: 90, 180, or 270 degrees")
    target: TransformTarget = Field(
        default=TransformTarget.SPRITE,
        description="What to rotate: sprite, layer, or cel",
    )

    @field_validator("angle")
    @classmethod
    def validate_angle(cls, v: int) -> int:
        allowed = {90, 180, 270}
        if v not in allowed:
            raise ValueError(f"angle must be one of: {', '.join(map(str, allowed))}")
        return v


@mcp.tool
def rotate_sprite(input: RotateSpriteInput) -> OperationOutput:
    """Rotate a sprite, layer, or cel by 90, 180, or 270 degrees clockwise.

    Args:
        input: Rotation parameters including angle and target scope

    Returns:
        OperationOutput indicating whether rotation was applied
    """
    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        app.command.Rotate{{
            angle = {input.angle},
            target = "{input.target}"
        }}
    end)

    spr:saveAs(spr.filename)
    print("Sprite rotated {input.angle} degrees successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
