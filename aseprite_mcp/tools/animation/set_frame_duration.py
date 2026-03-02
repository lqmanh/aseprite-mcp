from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class SetFrameDurationInput(BaseModel):
    """Input for setting frame duration.

    Note: frame_index is 0-based in Python, converted to 1-based for Lua.
    """

    filename: FilePath = Field(description="Path to the Aseprite file")
    frame_index: int = Field(ge=0, description="0-based index of the frame to modify")
    duration_ms: int = Field(
        ge=1, le=65535, description="Frame duration in milliseconds"
    )


@mcp.tool
def set_frame_duration(input: SetFrameDurationInput) -> OperationOutput:
    """Set the duration of an existing animation frame in milliseconds.

    Args:
        input: Frame duration parameters including 0-based frame index and duration

    Returns:
        OperationOutput indicating whether duration was set
    """
    duration_sec = input.duration_ms / 1000.0
    lua_frame_index = input.frame_index + 1

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    local frame = spr.frames[{lua_frame_index}]
    if not frame then
        error("Frame not found at index: {input.frame_index}")
    end

    app.transaction(function()
        frame.duration = {duration_sec:.3f}
    end)

    spr:saveAs(spr.filename)
    print("Frame duration set successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
