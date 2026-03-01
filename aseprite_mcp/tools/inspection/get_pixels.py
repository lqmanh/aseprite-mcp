import json

from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.schemas.outputs import PixelData
from aseprite_mcp.core.utils import escape_lua_str
from aseprite_mcp.core.validation import ExistingFile
from aseprite_mcp.mcp import mcp


class GetPixelsInput(BaseModel):
    """Input for getting pixel data from a region.

    Note: frame_index is 0-based in Python, converted to 1-based for Lua.
    """

    filename: ExistingFile = Field(description="Path to the Aseprite file")
    layer_name: str = Field(description="Name of the layer to read from")
    frame_index: int = Field(
        ge=0, description="0-based index of the frame to read from"
    )
    x: int = Field(description="X coordinate of top-left corner of region")
    y: int = Field(description="Y coordinate of top-left corner of region")
    width: int = Field(gt=0, description="Width of region to read")
    height: int = Field(gt=0, description="Height of region to read")
    cursor: int = Field(default=0, description="Pagination offset for next page")
    page_size: int = Field(
        default=1000, ge=1, le=10000, description="Number of pixels per page"
    )


class GetPixelsOutput(BaseModel):
    """Pixel data response with pagination."""

    pixels: list[PixelData] = Field(description="Pixel data for current page")
    next_cursor: int | None = Field(
        default=None, description="Offset for fetching next page (None if done)"
    )
    total: int = Field(description="Total number of pixels in the region")


@mcp.tool
def get_pixels(input: GetPixelsInput) -> GetPixelsOutput:
    """Read pixel data from a rectangular region of a sprite with pagination support.

    Args:
        input: Pixel reading parameters including 0-based frame index, region bounds, and pagination options

    Returns:
        GetPixelsOutput with pixel data array, pagination cursor, and total count
    """
    # Use cursor as offset directly
    offset = input.cursor
    lua_frame_index = input.frame_index + 1

    total = input.width * input.height

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
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

    local frame = spr.frames[{lua_frame_index}]
    if not frame then
        error("Frame not found at index: {input.frame_index}")
    end

    local cel = layer:cel(frame)
    if not cel then
        error("No cel found at layer '{escape_lua_str(input.layer_name)}' frame index {input.frame_index}")
    end

    local img = cel.image
    local pixels = {{}}
    local startIdx = {offset}
    local pageSize = {input.page_size}
    local count = 0

    -- Calculate bounds
    local x1 = {input.x}
    local y1 = {input.y}
    local x2 = x1 + {input.width} - 1
    local y2 = y1 + {input.height} - 1

    -- Iterate through region
    for py = y1, y2 do
        for px = x1, x2 do
            local idx = (py - y1) * {input.width} + (px - x1)
            if idx >= startIdx and count < pageSize then
                -- Adjust coordinates relative to cel position
                local imgX = px - cel.position.x
                local imgY = py - cel.position.y

                local colorHex = "#00000000"
                if imgX >= 0 and imgX < img.width and imgY >= 0 and imgY < img.height then
                    local pixel = img:getPixel(imgX, imgY)
                    local r = app.pixelColor.rgbaR(pixel)
                    local g = app.pixelColor.rgbaG(pixel)
                    local b = app.pixelColor.rgbaB(pixel)
                    local a = app.pixelColor.rgbaA(pixel)
                    colorHex = string.format("#%02X%02X%02X%02X", r, g, b, a)
                end

                table.insert(pixels, {{
                    x = px,
                    y = py,
                    color = colorHex
                }})
                count = count + 1
            end
        end
    end

    -- Output as JSON
    local jsonParts = {{}}
    for i, p in ipairs(pixels) do
        table.insert(jsonParts, string.format('{{"x":%d,"y":%d,"color":"%s"}}', p.x, p.y, p.color))
    end
    print("[" .. table.concat(jsonParts, ",") .. "]")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        try:
            pixels_data = json.loads(output.strip())
            pixels = [PixelData(**p) for p in pixels_data]

            # Calculate next cursor
            next_offset = offset + len(pixels)
            next_cursor = next_offset if next_offset < total else None

            return GetPixelsOutput(
                pixels=pixels,
                next_cursor=next_cursor,
                total=total,
            )
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse pixel data: {e}")
    else:
        raise RuntimeError(f"Failed to get pixels: {output}")
