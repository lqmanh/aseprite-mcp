from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class DeleteFrameInput(BaseModel):
    """Input for deleting a frame.

    Note: frame_index is 0-based in Python, converted to 1-based for Lua.
    """

    filename: ExistingFile = Field(description="Path to the Aseprite file to modify")
    frame_index: int = Field(ge=0, description="0-based index of the frame to delete")


@mcp.tool
def delete_frame(input: DeleteFrameInput) -> OperationOutput:
    """Delete a frame from an existing sprite. Cannot delete the last remaining frame.

    Args:
        input: Frame deletion parameters including 0-based frame index

    Returns:
        OperationOutput indicating whether the frame was deleted
    """
    lua_frame_index = input.frame_index + 1

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Check if this is the last frame
    if #spr.frames == 1 then
        error("Cannot delete the last frame")
    end

    local frame = spr.frames[{lua_frame_index}]
    if not frame then
        error("Frame not found at index: {input.frame_index}")
    end

    app.transaction(function()
        spr:deleteFrame(frame)
    end)

    spr:saveAs(spr.filename)
    print("Frame deleted successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
