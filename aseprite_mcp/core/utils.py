def parse_hex_color(hex_color: str) -> tuple[int, int, int, int]:
    """Parse hex color string into RGBA components.

    Supports both #RRGGBB and #RRGGBBAA formats.
    Returns (r, g, b, a) where a defaults to 255 if not provided.

    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "#FF000080")

    Returns:
        Tuple of (red, green, blue, alpha) as integers (0-255)

    Raises:
        ValueError: If hex_color is not valid hex format

    Example:
        >>> parse_hex_color("#FF0000")
        (255, 0, 0, 255)
        >>> parse_hex_color("#FF000080")
        (255, 0, 0, 128)
    """
    if not hex_color.startswith("#"):
        raise ValueError(f"Color must start with #: {hex_color}")
    hex_part = hex_color[1:]
    if len(hex_part) not in (6, 8):
        raise ValueError(f"Color must be in #RRGGBB or #RRGGBBAA format: {hex_color}")
    try:
        int(hex_part, 16)
    except ValueError:
        raise ValueError(f"Invalid hex characters in color: {hex_color}")

    r = int(hex_part[0:2], 16)
    g = int(hex_part[2:4], 16)
    b = int(hex_part[4:6], 16)
    a = int(hex_part[6:8], 16) if len(hex_part) == 8 else 255
    return (r, g, b, a)


def escape_lua_str(s: str) -> str:
    """Escape special characters for safe Lua string embedding.

    Escapes backslashes, double quotes, newlines, and carriage returns.

    Args:
        s: String to escape

    Returns:
        Escaped string safe for Lua string literals

    Example:
        >>> escape_lua_str('My "Special" Layer')
        'My \\"Special\\" Layer'
    """
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
