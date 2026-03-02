from pydantic import BaseModel, Field

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.enums import PaletteSortMethod
from aseprite_mcp.core.schemas.outputs import OperationOutput
from aseprite_mcp.core.validation import FilePath
from aseprite_mcp.mcp import mcp


class SortPaletteInput(BaseModel):
    """Input for sorting palette."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    method: PaletteSortMethod = Field(
        description="Sort method: hue, saturation, brightness, or luminance"
    )
    ascending: bool = Field(default=True, description="Sort in ascending order")


@mcp.tool
def sort_palette(input: SortPaletteInput) -> OperationOutput:
    """Sort the palette by hue, saturation, brightness, or luminance.

    Args:
        input: Sort parameters including method and order

    Returns:
        OperationOutput indicating whether palette was sorted
    """
    sort_key = input.method[0]  # h, s, b, or l
    sort_direction = "<" if input.ascending else ">"

    script = f"""
    local spr = app.activeSprite
    if not spr then
        error("No active sprite")
    end

    -- Get palette
    local palette = spr.palettes[1]
    if not palette then
        error("No palette found")
    end

    -- Helper: Convert RGB to HSL
    local function rgbToHSL(r, g, b)
        r, g, b = r / 255, g / 255, b / 255
        local max = math.max(r, g, b)
        local min = math.min(r, g, b)
        local delta = max - min

        local h, s, l = 0, 0, (max + min) / 2

        if delta ~= 0 then
            -- Calculate saturation
            if l < 0.5 then
                s = delta / (max + min)
            else
                s = delta / (2.0 - max - min)
            end

            -- Calculate hue
            if max == r then
                h = ((g - b) / delta)
                if g < b then
                    h = h + 6.0
                end
            elseif max == g then
                h = ((b - r) / delta) + 2.0
            elseif max == b then
                h = ((r - g) / delta) + 4.0
            end

            h = h * 60.0
        end

        return h, s, l
    end

    -- Extract colors with HSL values
    local colors = {{}}
    for i = 0, #palette - 1 do
        local color = palette:getColor(i)
        local h, s, l = rgbToHSL(color.red, color.green, color.blue)
        table.insert(colors, {{
            index = i,
            color = color,
            h = h,
            s = s,
            l = l
        }})
    end

    -- Sort colors by {input.method}
    table.sort(colors, function(a, b)
        return a.{sort_key} {sort_direction} b.{sort_key}
    end)

    -- Apply sorted colors back to palette
    for i, entry in ipairs(colors) do
        palette:setColor(i - 1, entry.color)
    end

    spr:saveAs(spr.filename)
    print("Palette sorted by {input.method} successfully")
    """

    success, output = AsepriteCommand.execute_lua_script(script, input.filename)

    if success:
        return OperationOutput(success=True)
    else:
        return OperationOutput(success=False, message=output)
