from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import ColorMode
from aseprite_mcp.core.validation import AbsPath
from aseprite_mcp.mcp import mcp


class CreateCanvasInput(BaseModel):
    """Input for creating a new canvas."""

    width: int = Field(gt=0, le=65535, description="Width of the canvas in pixels")
    height: int = Field(gt=0, le=65535, description="Height of the canvas in pixels")
    filename: AbsPath = Field(
        default="canvas.aseprite", description="Name of the output file"
    )
    color_mode: ColorMode = Field(
        default=ColorMode.RGB, description="Color mode: rgb, grayscale, or indexed"
    )


class CreateCanvasOutput(BaseModel):
    """Response when a canvas is created."""

    output_filename: AbsPath = Field(description="Absolute path to the created file")


@mcp.tool
def create_canvas(input: CreateCanvasInput) -> CreateCanvasOutput:
    """Create a new Aseprite canvas with specified dimensions and color mode.

    Args:
        input: Canvas creation parameters including width, height, filename, and color_mode

    Returns:
        CreateCanvasOutput with the path to the created file
    """
    color_mode_map = {
        ColorMode.RGB: "ColorMode.RGB",
        ColorMode.GRAYSCALE: "ColorMode.GRAYSCALE",
        ColorMode.INDEXED: "ColorMode.INDEXED",
    }
    color_mode_lua = color_mode_map[input.color_mode]

    script = f"""
    local spr = Sprite({input.width}, {input.height}, {color_mode_lua})
    """

    if input.color_mode == ColorMode.INDEXED:
        script += """
    spr.transparentColor = 255
    """

    script += f"""
    spr:saveAs("{input.filename}")
    print("{input.filename}")
    """

    success, output = AsepriteCommand.execute_lua_script(script)

    if success:
        return CreateCanvasOutput(output_filename=input.filename)
    else:
        raise RuntimeError(f"Failed to create canvas: {output}")
