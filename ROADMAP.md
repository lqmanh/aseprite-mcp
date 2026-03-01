# Aseprite MCP - Roadmap

## Phase 1: Fundamental Features

Core tools that work with Aseprite's Lua API without requiring additional Python libraries.

### Canvas Management (4 tools)

- [ ] `get_sprite_info` - Read sprite metadata (width, height, color_mode, frames, layers)
- [ ] `delete_layer` - Remove layer (prevent deleting last layer)
- [ ] `delete_frame` - Remove frame (prevent deleting last frame)
- [ ] `flatten_layers` - Merge all visible layers

### Canvas Enhancement

- [ ] Add `color_mode` parameter to `create_canvas` (rgb/grayscale/indexed)

### Inspection Tools (1 tool)

- [ ] `get_pixels` - Read pixel data with cursor-based pagination
  - Support page_size parameter (default 1000, max 10000)
  - Return next_cursor for pagination

### Selection Tools (5 tools)

- [ ] `select_rectangle` - Rectangle selection with modes (replace/add/subtract/intersect)
- [ ] `select_ellipse` - Elliptical selection
- [ ] `select_all` - Select entire canvas
- [ ] `deselect` - Clear selection
- [ ] `move_selection` - Move by offset (dx, dy)

### Animation Tools (2 tools)

- [ ] `set_frame_duration` - Set frame timing in milliseconds
- [ ] `create_tag` - Animation tags with direction (forward/reverse/pingpong)

### Transform Tools (4 tools)

- [ ] `flip_sprite` - Horizontal/vertical flip
- [ ] `rotate_sprite` - 90/180/270 degree rotation
- [ ] `crop_sprite` - Crop to region
- [ ] `resize_canvas` - Resize with anchor positions

### Palette Tools (5 tools)

- [ ] `get_palette` - Read current palette
- [ ] `set_palette` - Set entire palette from color array
- [ ] `set_palette_color` - Modify single color by index
- [ ] `add_palette_color` - Append color to palette
- [ ] `sort_palette` - Sort by hue/saturation/brightness/luminance

**Phase 1 Total: 22 tools**

## Phase 2: Advanced Features

Tools requiring complex algorithms or advanced workflow features that can be implemented in pure Lua.

### Animation (3 tools)

- [ ] `duplicate_frame` - Copy existing frames
- [ ] `link_cel` - Create linked cels across frames
- [ ] `delete_tag` - Remove animation tags

### Selection (3 tools)

- [ ] `cut_selection` - Cut to clipboard
- [ ] `copy_selection` - Copy to clipboard
- [ ] `paste_clipboard` - Paste from clipboard

### Drawing (1 tool)

- [ ] `draw_contour` - Multi-segment polylines (open or closed)

### Transform (1 tool)

- [ ] `apply_outline` - Automatic outline generation

### Palette (1 tool)

- [ ] `apply_shading` - Apply shading with light direction

### Export/Import (3 tools)

- [ ] `export_spritesheet` - Export frames as spritesheet (horizontal/vertical/grid/packed)
- [ ] `import_image` - Import external images as layers
- [ ] `save_as` - Save to different path

### Dithering (1 tool)

- [ ] `draw_with_dither` - 16 dithering patterns
  - Bayer matrices: 2x2, 4x4, 8x8
  - Floyd-Steinberg error diffusion
  - 9 texture patterns (grass, water, stone, etc.)

**Phase 2 Total: 12 tools**

## Phase 3: Optional Features

Tools requiring additional Python libraries (Pillow, numpy, scikit-learn) for image processing.

### Analysis (1 tool)

- [ ] `analyze_reference` - Reference image analysis
  - **Requires:** Pillow, scikit-learn, numpy
  - k-means palette extraction (5-32 colors)
  - Brightness quantization (2-10 levels)
  - Edge detection with threshold
  - Composition analysis (rule of thirds, focal points)
  - Suggested dithering zones

### Quantization (1 tool)

- [ ] `quantize_palette` - Color reduction algorithms
  - **Requires:** Pillow, numpy
  - median_cut, k-means, octree algorithms
  - Floyd-Steinberg dithering option
  - Convert to indexed mode

### Transform (2 tools)

- [ ] `downsample_image` - Convert images to pixel art dimensions
  - **Requires:** Pillow, numpy
- [ ] `scale_sprite` - Scale with rotsprite algorithm
  - **Requires:** Pillow, numpy

### Auto-Shading (1 tool)

- [ ] `apply_auto_shading` - Automatic shading based on geometry
  - **Requires:** Pillow, numpy
  - 8 light directions, 3 styles (cell, smooth, soft)
  - Hue shifting (shadows cool, highlights warm)

### Antialiasing (1 tool)

- [ ] `suggest_antialiasing` - Edge detection and smoothing
  - **Requires:** Pillow, numpy
  - Detect jagged diagonal edges
  - Suggest intermediate colors

### Palette (1 tool)

- [ ] `analyze_palette_harmonies` - Color theory analysis
  - **Requires:** colorspacious (for LAB color space)
  - Complementary, triadic, analogous harmonies
  - Temperature analysis (warm/cool colors)

**Phase 3 Total: 7 tools**

## Summary

| Phase                | Tools        | Dependencies                               |
| -------------------- | ------------ | ------------------------------------------ |
| Phase 1: Fundamental | 22 tools     | None (pure Lua)                            |
| Phase 2: Advanced    | 12 tools     | Complex Lua algorithms                     |
| Phase 3: Optional    | 7 tools      | Pillow, numpy, scikit-learn, colorspacious |
| **Total**            | **41 tools** |                                            |

### Python Dependencies for Phase 3

```toml
[project.optional-dependencies]
advanced = [
    "pillow>=10.0.0",        # Image processing
    "numpy>=1.24.0",         # Array operations
    "scikit-learn>=1.3.0",   # k-means clustering
    "colorspacious>=1.1.0",  # LAB color space conversions
]
```

### Critical Path

1. **get_sprite_info** (Phase 1) → Required for input validation across all tools
2. **get_pixels** (Phase 1) → Required for Phase 3 analysis/shading/antialiasing
3. **Palette tools** (Phase 1) → Required for UsePalette flag in drawing operations
4. **Selection tools** (Phase 1) → Required for transform operations on selections
