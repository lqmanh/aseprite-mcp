from pydantic import BaseModel, Field, field_validator

from aseprite_mcp.core.commands import AsepriteCommand
from aseprite_mcp.core.validation import AbsPath, FilePath
from aseprite_mcp.mcp import mcp


class ExportSpriteInput(BaseModel):
    """Input for exporting a sprite."""

    filename: FilePath = Field(description="Path to the Aseprite file")
    output_filename: AbsPath = Field(description="Name of the output file")
    format: str = Field(
        default="png", description="Output format (png, gif, jpg, etc.)"
    )

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        return v.lower()


class ExportSpriteOutput(BaseModel):
    """Response when a sprite is exported."""

    output_filename: AbsPath = Field(description="Absolute path to the exported file")


@mcp.tool
def export_sprite(input: ExportSpriteInput) -> ExportSpriteOutput:
    """Export the Aseprite file to another format.

    Args:
        input: Export parameters including filename, output name, and format

    Returns:
        ExportSpriteOutput with the actual output file path
    """
    # Ensure output filename has the correct extension
    output_filename = input.output_filename
    if not output_filename.lower().endswith(f".{input.format}"):
        output_filename = f"{output_filename}.{input.format}"

    args = ["--batch", input.filename, "--save-as", output_filename]
    success, output = AsepriteCommand.run_command(args)

    if success:
        return ExportSpriteOutput(output_filename=output_filename)
    else:
        raise RuntimeError(f"Failed to export sprite: {output}")
