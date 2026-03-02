"""Shared validation utilities for Aseprite MCP tools."""

import os
from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, Field, PlainValidator


def _validate_non_empty_string(v: str) -> str:
    """Validate that a string is not empty or whitespace-only."""
    if not v.strip():
        raise ValueError("String cannot be empty")
    return v


NonEmptyStr = Annotated[
    str,
    AfterValidator(_validate_non_empty_string),
    Field(description="A non-empty string"),
]


def _resolve_with_workdir(path: str) -> Path:
    p = Path(path)
    base_dir = os.getenv("ASEPRITE_WORKDIR")
    if base_dir:
        p = Path(base_dir) / p
    return p.resolve()


def _validate_file_path(filename: str) -> str:
    """Validate that a file exists and return absolute path."""
    path = _resolve_with_workdir(filename)
    if not path.exists():
        raise ValueError(f"File not found: {filename}")
    return str(path)


FilePath = Annotated[
    str,
    PlainValidator(_validate_file_path),
    Field(description="Path to an existing file"),
]


def _resolve_to_abs_path(path: str) -> str:
    """Resolve a path to absolute path."""
    return str(_resolve_with_workdir(path))


AbsPath = Annotated[
    str,
    PlainValidator(_resolve_to_abs_path),
    Field(description="Path resolved to absolute path"),
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


HexColor = Annotated[
    str,
    PlainValidator(_validate_hex_color),
    Field(description="Hex color code (#RRGGBB or #RRGGBBAA)"),
]
