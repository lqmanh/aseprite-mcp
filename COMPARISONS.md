# Aseprite MCP - Feature Comparisons

## Overview

This document compares **aseprite-mcp** (our Python project) with [**pixel-mcp**](https://github.com/willibrandon/pixel-mcp) (Go-based reference implementation) to identify gaps and opportunities for feature parity.

### Feature Comparison Matrix

| Category          | aseprite-mcp | pixel-mcp    | Gap                                  |
| ----------------- | ------------ | ------------ | ------------------------------------ |
| **Canvas**        | 3 tools      | 7 tools      | Missing 4 canvas management tools    |
| **Drawing**       | 5 tools      | 6 tools      | Missing draw_contour                 |
| **Selection**     | 0 tools      | 8 tools      | **Complete category missing**        |
| **Animation**     | 0 tools      | 5 tools      | **Complete category missing**        |
| **Export/Import** | 1 tool       | 4 tools      | Missing spritesheet, import, save_as |
| **Inspection**    | 0 tools      | 1 tool       | Missing get_pixels                   |
| **Transform**     | 0 tools      | 7 tools      | **Complete category missing**        |
| **Analysis**      | 0 tools      | 1 tool       | Missing analyze_reference            |
| **Dithering**     | 0 tools      | 1 tool       | Missing draw_with_dither             |
| **Palette**       | 0 tools      | 7 tools      | **Complete category missing**        |
| **Quantization**  | 0 tools      | 1 tool       | Missing quantize_palette             |
| **Auto-Shading**  | 0 tools      | 1 tool       | Missing apply_auto_shading           |
| **Antialiasing**  | 0 tools      | 1 tool       | Missing suggest_antialiasing         |
| **TOTAL**         | **9 tools**  | **50 tools** | **41 tools missing**                 |

## Tools Both Projects Offer

### Canvas Management

| Tool            | aseprite-mcp | pixel-mcp | Notes                                   |
| --------------- | ------------ | --------- | --------------------------------------- |
| `create_canvas` | ✅           | ✅        | Both create new sprites with dimensions |
| `add_layer`     | ✅           | ✅        | Both add layers to existing sprites     |
| `add_frame`     | ✅           | ✅        | pixel-mcp adds duration_ms parameter    |

### Drawing Tools

| Tool             | aseprite-mcp | pixel-mcp | Notes                                               |
| ---------------- | ------------ | --------- | --------------------------------------------------- |
| `draw_pixels`    | ✅           | ✅        | pixel-mcp supports UsePalette flag                  |
| `draw_line`      | ✅           | ✅        | Both support thickness parameter                    |
| `draw_rectangle` | ✅           | ✅        | Both support filled/outline variants                |
| `fill_area`      | ✅           | ✅        | pixel-mcp uses `fill` name with tolerance parameter |

### Export Tools

| Tool            | aseprite-mcp | pixel-mcp | Notes                                                 |
| --------------- | ------------ | --------- | ----------------------------------------------------- |
| `export_sprite` | ✅           | ✅        | pixel-mcp has more format options and frame selection |

## Features pixel-mcp Supports That We Don't

### Canvas & Sprite Info

- **`get_sprite_info`** - Retrieve sprite metadata (dimensions, color mode, frame count, layer names)
- **`delete_layer`** - Delete layers from sprite (cannot delete last remaining layer)
- **`delete_frame`** - Delete frames from sprite (cannot delete last remaining frame)
- **`flatten_layers`** - Merge all layers into a single layer
- **Color mode support** - RGB, Grayscale, Indexed modes in create_canvas

### Advanced Drawing

- **`draw_contour`** - Draw multi-segment polylines (open or closed)
- **UsePalette flag** - Snap colors to nearest palette color using LAB color space

### Selection Tools (Complete category missing)

- `select_rectangle` - Rectangle selection with modes (replace/add/subtract/intersect)
- `select_ellipse` - Elliptical selection
- `select_all` / `deselect` - Selection management
- `move_selection` - Move selection by offset
- `cut_selection` / `copy_selection` / `paste_clipboard` - Clipboard operations

### Animation Tools (Complete category missing)

- `set_frame_duration` - Set frame timing in milliseconds
- `create_tag` - Create animation tags with playback direction (forward/reverse/pingpong)
- `duplicate_frame` - Copy existing frames
- `link_cel` - Create linked cels across frames
- `delete_tag` - Remove animation tags

### Import/Extended Export

- **`export_spritesheet`** - Export all frames as spritesheet (horizontal/vertical/grid/packed)
- **`import_image`** - Import external images as layers
- **`save_as`** - Save to different path

### Inspection Tools

- **`get_pixels`** - Read pixel data from regions with **cursor-based pagination** for large regions:
  - Default page size: 1000 pixels, max: 10000 pixels per request
  - Use `cursor` parameter to fetch subsequent pages
  - Returns `next_cursor` when more data available

### Transform Tools (Complete category missing)

- `downsample_image` - Convert images to pixel art dimensions
- `flip_sprite` - Horizontal/vertical flip
- `rotate_sprite` - 90/180/270 degree rotation
- `scale_sprite` - Nearest/bilinear/rotsprite algorithms
- `crop_sprite` - Crop to region
- `resize_canvas` - Resize with anchor positions
- `apply_outline` - Automatic outline generation

### Analysis Tools (Complete category missing)

- **`analyze_reference`** - Comprehensive reference image analysis:
  - k-means palette extraction (5-32 colors)
  - Brightness quantization (2-10 levels)
  - Edge detection with threshold
  - Composition analysis (rule of thirds, focal points)
  - Suggested dithering zones

### Dithering Tools (Complete category missing)

- **`draw_with_dither`** - 16 dithering patterns:
  - Bayer matrices: 2x2, 4x4, 8x8
  - Floyd-Steinberg error diffusion
  - Checkerboard
  - Texture patterns: grass, water, stone, cloud, brick, dots, diagonal, cross, noise, lines

### Palette Tools (Complete category missing)

- `get_palette` - Read current palette
- `set_palette` - Set entire palette
- `set_palette_color` - Modify single color by index
- `add_palette_color` - Append color to palette
- `sort_palette` - Sort by hue/saturation/brightness/luminance
- `apply_shading` - Apply shading with light direction
- `analyze_palette_harmonies` - Color theory analysis (complementary, triadic, analogous)

### Quantization Tools (Complete category missing)

- **`quantize_palette`** - Color reduction algorithms:
  - median_cut (fast, balanced)
  - kmeans (highest quality)
  - octree (very fast)
  - Floyd-Steinberg dithering option
  - Convert to indexed mode option

### Auto-Shading Tools (Complete category missing)

- **`apply_auto_shading`** - Automatic shading based on geometry:
  - 8 light directions
  - 3 styles: cell, smooth, soft
  - Hue shifting (shadows→cool, highlights→warm)
  - Automatic shadow/highlight color generation

### Antialiasing Tools (Complete category missing)

- **`suggest_antialiasing`** - Edge detection and smoothing:
  - Detects jagged diagonal edges
  - Suggests intermediate colors
  - Auto-apply option

## Key Architectural Differences

### Language & Stack

- **aseprite-mcp**: Python 3.13+, FastMCP framework
- **pixel-mcp**: Go, custom MCP SDK implementation

### Lua Generation

- **aseprite-mcp**: Inline Lua strings in tool functions
- **pixel-mcp**: Dedicated LuaGenerator with method per operation

### Testing

- **aseprite-mcp**: Minimal (tests/ directory empty)
- **pixel-mcp**: Extensive (unit, integration, benchmark, MCP tests)

### Documentation

- **aseprite-mcp**: Basic README
- **pixel-mcp**: Comprehensive docs (TESTING.md, BENCHMARKS.md, DOCKER.md, examples/)

## Implementation Notes

### Go Image Processing Libraries

**Note:** Some pixel-mcp tools perform image processing in Go (not just Lua), using Go's standard `image` package and third-party libraries like `go-colorful`:

- **`analyze_reference`** - k-means palette extraction, brightness/edge detection in Go
- **`quantize_palette`** - Median cut, k-means, octree algorithms implemented in Go
- **`apply_auto_shading`** - Image analysis and shadow/highlight generation in Go before applying to Aseprite

### Differences in Similar Tools

**create_canvas:**

- aseprite-mcp: Simple width/height/filename
- pixel-mcp: Adds color_mode (rgb/grayscale/indexed), returns absolute path

**draw_pixels:**

- aseprite-mcp: Direct pixel manipulation via cel.image:putPixel()
- pixel-mcp: Batch operations, supports palette snapping, returns count

**add_frame:**

- aseprite-mcp: No duration parameter
- pixel-mcp: Supports duration_ms parameter

**export_sprite:**

- aseprite-mcp: Basic format export
- pixel-mcp: Frame selection, multiple formats, file size in output
