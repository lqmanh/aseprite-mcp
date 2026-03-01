from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class AddFrameInput(BaseModel):
    """Input for adding a new frame."""

    filename: ExistingFile = Field(description="Path to the Aseprite file to modify")
    duration_ms: int = Field(
        default=100, gt=0, le=65535, description="Frame duration in milliseconds"
    )


class AddFrameOutput(BaseModel):
    """Response when a frame is created.

    Note: frame_index is 0-based in Python, converted from Lua's 1-based indexing.
    """

    frame_index: int = Field(description="0-based index of the created frame")


@mcp.tool
def add_frame(input: AddFrameInput) -> AddFrameOutput:
    """Add a new animation frame to the sprite with the specified duration.

    Args:
        input: Frame addition parameters including filename and duration_ms

    Returns:
        AddFrameOutput with the 0-based index of the created frame
    """
    duration_sec = input.duration_ms / 1000.0

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    app.transaction(function()
        local frame = spr:newFrame()
        frame.duration = {duration_sec:.3f}
    end)

    spr:saveAs(spr.filename)
    print(#spr.frames)
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        try:
            lua_frame_count = int(output.strip())
            frame_index = lua_frame_count - 1
            return AddFrameOutput(frame_index=frame_index)
        except ValueError:
            return AddFrameOutput(frame_index=0)
    else:
        raise RuntimeError(f"Failed to add frame: {output}")
