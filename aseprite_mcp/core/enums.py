from enum import StrEnum


class ColorMode(StrEnum):
    """Color mode for Aseprite sprites."""

    RGB = "rgb"
    GRAYSCALE = "grayscale"
    INDEXED = "indexed"


class AnimationDirection(StrEnum):
    """Animation playback direction."""

    FORWARD = "forward"
    REVERSE = "reverse"
    PING_PONG = "pingpong"


class FlipDirection(StrEnum):
    """Flip direction for transform operations."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class TransformTarget(StrEnum):
    """Target scope for transform operations."""

    SPRITE = "sprite"
    LAYER = "layer"
    CEL = "cel"


class SelectionMode(StrEnum):
    """Selection mode for selection operations."""

    REPLACE = "replace"
    ADD = "add"
    SUBTRACT = "subtract"
    INTERSECT = "intersect"


class PaletteSortMethod(StrEnum):
    """Sort method for palette operations."""

    HUE = "hue"
    SATURATION = "saturation"
    BRIGHTNESS = "brightness"
    LUMINANCE = "luminance"
