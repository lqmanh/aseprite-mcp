from pydantic import BaseModel, Field, field_validator

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import AnimationDirection
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.utils import escape_lua_str
from aseprite_mcp.core.validation import FilePath, NonEmptyStr
from aseprite_mcp.mcp import mcp


class CreateTagInput(BaseModel):
    """Input for creating an animation tag.

    Note: Frame indices are 0-based in Python, converted to 1-based for Lua.
    """

    filename: FilePath = Field(description="Path to the Aseprite file")
    tag_name: NonEmptyStr = Field(description="Name for the animation tag")
    from_frame: int = Field(
        ge=0, description="0-based starting frame index (inclusive)"
    )
    to_frame: int = Field(ge=0, description="0-based ending frame index (inclusive)")
    direction: AnimationDirection = Field(
        default=AnimationDirection.FORWARD,
        description="Playback direction: forward, reverse, or pingpong",
    )

    @field_validator("to_frame")
    @classmethod
    def validate_frame_range(cls, v: int, info) -> int:
        from_frame = info.data.get("from_frame")
        if from_frame is not None and v < from_frame:
            raise ValueError(f"to_frame ({v}) must be >= from_frame ({from_frame})")
        return v


@mcp.tool
def create_tag(input: CreateTagInput) -> OperationOutput:
    """Create an animation tag to define a named frame range with playback direction.

    Args:
        input: Tag creation parameters including 0-based frame range and direction

    Returns:
        OperationOutput indicating whether tag was created
    """
    ani_dir_map = {
        AnimationDirection.FORWARD: "AniDir.FORWARD",
        AnimationDirection.REVERSE: "AniDir.REVERSE",
        AnimationDirection.PING_PONG: "AniDir.PING_PONG",
    }
    ani_dir = ani_dir_map[input.direction]
    lua_from_frame = input.from_frame + 1
    lua_to_frame = input.to_frame + 1

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    if #spr.frames < {lua_to_frame} then
        error("Frame range exceeds sprite frames")
    end

    app.transaction(function()
        local tag = spr:newTag({lua_from_frame}, {lua_to_frame})
        tag.name = "{escape_lua_str(input.tag_name)}"
        tag.aniDir = {ani_dir}
    end)

    spr:saveAs(spr.filename)
    print("Tag created successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
