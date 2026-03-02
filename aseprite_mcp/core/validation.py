"""Shared validation utilities for Aseprite MCP tools."""

from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, Field, PlainValidator


def _validate_non_empty_string(v: str) -> str:
    """Validate that a string is not empty or whitespace-only."""
    if not v.strip():
        raise ValueError("String cannot be empty")
    return v


# Reusable non-empty string type with automatic validation
NonEmptyStr = Annotated[
    str,
    AfterValidator(_validate_non_empty_string),
    Field(description="A non-empty string"),
]


def _validate_file_exists(filename: str) -> str:
    """Validate that a file exists."""
    if not Path(filename).exists():
        raise ValueError(f"File not found: {filename}")
    return filename


# Reusable file path type with automatic validation
ExistingFile = Annotated[
    str,
    PlainValidator(_validate_file_exists),
    Field(description="Path to an existing file"),
]


def _validate_hex_color(v: str) -> str:
    """Validate hex color code (#RRGGBB or #RRGGBBAA)."""
    if not v.startswith("#"):
        raise ValueError(f"Color must start with #: {v}")
    hex_part = v[1:]
    if len(hex_part) not in (6, 8):
        raise ValueError(f"Color must be in #RRGGBB or #RRGGBBAA format: {v}")
    try:
        int(hex_part, 16)
    except ValueError:
        raise ValueError(f"Invalid hex color: {v}")
    return v.upper()


# Reusable hex color type with automatic validation
HexColor = Annotated[
    str,
    PlainValidator(_validate_hex_color),
    Field(description="Hex color code (#RRGGBB or #RRGGBBAA)"),
]
