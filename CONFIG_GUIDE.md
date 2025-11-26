# Field Configuration Guide

## Overview

The config-based system uses JSON to define field positions, alignment, and behavior. This makes it easy to:
- ✅ Adjust field positions without changing code
- ✅ Specify vertical alignment (top/middle/bottom)
- ✅ Control font sizes and wrapping
- ✅ Detect existing text to avoid overlaps

## Quick Start

```bash
# Use default configuration
python populate_pdf_config.py

# The script reads: field_config.json
```

## Configuration File Structure

### Basic Structure

```json
{
  "pdf_template": "path/to/template.pdf",
  "fields": [
    {
      "id": "unique_field_id",
      "label": "Field Display Name",
      "json_key": "data_key_from_json",
      "box": {
        "x0": 100,
        "x1": 200,
        "y0": 150,
        "y1": 170
      },
      "fontsize": 10,
      "alignment": "middle",
      "allow_wrap": false,
      "min_fontsize": 6
    }
  ],
  "settings": {
    "padding_horizontal": 3,
    "line_height_multiplier": 1.3
  }
}
```

## Field Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for the field |
| `label` | string | Yes | Human-readable field name |
| `json_key` | string | Yes | Key to extract data from input JSON |
| `box` | object | Yes | Coordinates: x0, x1, y0, y1 |
| `fontsize` | number | Yes | Initial/preferred font size |
| `alignment` | string | No | "top", "middle" (default), or "bottom" |
| `allow_wrap` | boolean | No | Enable text wrapping (default: false) |
| `min_fontsize` | number | No | Minimum font size when scaling (default: 6) |
| `comment` | string | No | Documentation note |

## Alignment Options

### Middle Alignment (Default)
```json
"alignment": "middle"
```

**Use for:**
- Standard form fields
- Single-line text
- Fields with space above and below

**Behavior:**
- Text centered vertically in box
- Most common alignment

**Example:**
```
┌─────────────┐
│             │
│  Text Here  │  ← Centered
│             │
└─────────────┘
```

### Top Alignment
```json
"alignment": "top"
```

**Use for:**
- Fields with text or elements below
- Address fields
- Long text that might overlap content below

**Behavior:**
- Text starts at top of box with small padding
- Prevents overlap with content below

**Example:**
```
┌─────────────┐
│ Text Here   │  ← Top aligned
│             │
│             │
└─────────────┘
```

### Bottom Alignment
```json
"alignment": "bottom"
```

**Use for:**
- Fields with text or elements above
- Signature lines
- Fields where space above is critical

**Behavior:**
- Text aligns to bottom of box with small padding
- Preserves space above

**Example:**
```
┌─────────────┐
│             │
│             │
│  Text Here  │  ← Bottom aligned
└─────────────┘
```

## Box Coordinates

Coordinates define the rectangular area for the field:

```json
"box": {
  "x0": 79.1,   // Left edge
  "x1": 148.8,  // Right edge
  "y0": 165.3,  // Top edge
  "y1": 189.4   // Bottom edge
}
```

### Coordinate System
- Origin (0, 0) is at **top-left** of page
- X increases to the right
- Y increases downward
- Units: points (1/72 inch)

### Finding Box Coordinates

See the analysis from notebook 01 or use the debug script:

```bash
# Run analysis to find box positions
python -c "
import pdfplumber
with pdfplumber.open('pdf/your_file.pdf') as pdf:
    page = pdf.pages[0]
    for rect in page.rects[:10]:
        print(f'Box: x={rect[\"x0\"]}-{rect[\"x1\"]}, y={rect[\"top\"]}-{rect[\"bottom\"]}')
"
```

## Text Wrapping

### Enable Wrapping
```json
{
  "allow_wrap": true,
  "alignment": "top"  // Works best with top or bottom
}
```

### Wrapping Behavior
- Long text splits into multiple lines
- Words break at spaces
- Line height = fontsize × 1.3 (configurable)
- All lines use same alignment

### Example: Address Field
```json
{
  "id": "address",
  "json_key": "address",
  "box": {...},
  "fontsize": 9,
  "alignment": "top",
  "allow_wrap": true,
  "min_fontsize": 6
}
```

Result:
```
┌─────────────────────────┐
│ 48, Sambong-ro,         │
│ Jongno-gu, Seoul,       │
│ 03156, Rep. of KOREA    │
└─────────────────────────┘
```

## Font Sizing

### Auto-Scaling
The script automatically scales font size to fit text in box:

1. **Start** with `fontsize`
2. **Check** if text fits
3. **Scale down** by 0.5pt increments
4. **Stop** at `min_fontsize`
5. **Wrap** if `allow_wrap` is true

### Font Size Example
```json
{
  "fontsize": 10,      // Try 10pt first
  "min_fontsize": 6    // Don't go below 6pt
}
```

If text too long:
- 10pt → 9.5pt → 9pt → ... → 6pt
- If still doesn't fit: wrap (if enabled)

## Existing Text Detection

The script automatically detects existing text in box areas:

```
주소 (Address):
  Data: '48, Sambong-ro, Jongno-gu, Seoul...'
  Alignment: top
  ⚠️  Detected existing text in box area:
      '고객정보' at (95.1, 299.5)
      '변경동의' at (124.5, 299.5)
  ✓ Using top alignment to avoid overlap
```

**Benefits:**
- Warns you of potential overlaps
- Helps choose correct alignment
- Shows what text exists in area

## Settings Section

Global settings that apply to all fields:

```json
"settings": {
  "padding_horizontal": 3,
  "padding_vertical_top": 3,
  "padding_vertical_bottom": 3,
  "line_height_multiplier": 1.3,
  "default_fontname": "helv",
  "default_color": [0, 0, 0]
}
```

| Setting | Description | Default |
|---------|-------------|---------|
| `padding_horizontal` | Left padding in points | 3 |
| `padding_vertical_top` | Top padding for top-aligned | 3 |
| `padding_vertical_bottom` | Bottom padding for bottom-aligned | 3 |
| `line_height_multiplier` | Line spacing (fontsize × multiplier) | 1.3 |
| `default_fontname` | Font name (helv, times, courier) | helv |
| `default_color` | RGB color [R, G, B] (0-1 scale) | [0,0,0] |

## Complete Examples

### Example 1: Single-Line Field (Middle)
```json
{
  "id": "name",
  "label": "Name",
  "json_key": "name",
  "box": {"x0": 79, "x1": 149, "y0": 165, "y1": 189},
  "fontsize": 10,
  "alignment": "middle",
  "allow_wrap": false,
  "min_fontsize": 7
}
```

### Example 2: Multi-Line Field (Top)
```json
{
  "id": "address",
  "label": "Address",
  "json_key": "address",
  "box": {"x0": 93, "x1": 340, "y0": 297, "y1": 318},
  "fontsize": 9,
  "alignment": "top",
  "allow_wrap": true,
  "min_fontsize": 6
}
```

### Example 3: Signature Field (Bottom)
```json
{
  "id": "signature",
  "label": "Signature",
  "json_key": "signature_name",
  "box": {"x0": 400, "x1": 550, "y0": 700, "y1": 730},
  "fontsize": 10,
  "alignment": "bottom",
  "allow_wrap": false,
  "min_fontsize": 8
}
```

## Troubleshooting

### Text Overlapping Below
**Solution:** Use `"alignment": "top"`

```json
"alignment": "top"  // Start at top of box
```

### Text Overlapping Above
**Solution:** Use `"alignment": "bottom"`

```json
"alignment": "bottom"  // Start at bottom of box
```

### Text Too Large
**Solution:** Reduce fontsize or min_fontsize

```json
"fontsize": 9,        // Start smaller
"min_fontsize": 6     // Allow smaller scaling
```

### Text Not Wrapping
**Solution:** Enable allow_wrap

```json
"allow_wrap": true,
"alignment": "top"    // Best with top/bottom
```

### Text Not Centered
**Solution:** Check alignment setting

```json
"alignment": "middle"  // Explicitly set middle
```

## Testing Different Alignments

Use the demo config to see all alignment types:

```bash
# Copy demo config
cp field_config_demo.json field_config.json

# Run population
python populate_pdf_config.py

# Check output to see different alignments
```

## Creating Your Own Config

1. **Start with template:**
   ```bash
   cp field_config.json my_form_config.json
   ```

2. **Find box coordinates:**
   - Run notebook 01 for analysis
   - Or use pdfplumber to examine rects
   - Or use populate_pdf_debug.py to see boxes

3. **Add fields one by one:**
   ```json
   {
     "id": "new_field",
     "label": "New Field Label",
     "json_key": "json_data_key",
     "box": {...},  // Your coordinates
     "fontsize": 10,
     "alignment": "middle"
   }
   ```

4. **Test and adjust:**
   ```bash
   python populate_pdf_config.py
   # Check output
   # Adjust box coordinates or alignment
   # Repeat
   ```

## Best Practices

### 1. Always Set Alignment Explicitly
```json
"alignment": "middle"  // Don't rely on defaults
```

### 2. Use Top Alignment for Address Fields
```json
{
  "id": "address",
  "alignment": "top",     // Prevents overlap below
  "allow_wrap": true      // Handles long addresses
}
```

### 3. Leave Padding
```json
// Don't use full box width
"fontsize": 9,            // Slightly smaller than max
"min_fontsize": 6         // Allow scaling
```

### 4. Test with Long Data
```json
// Test with maximum expected text length
"allow_wrap": true,       // Handle edge cases
```

### 5. Document Your Fields
```json
{
  "id": "field_name",
  "comment": "This field is for customer signatures - bottom aligned to avoid overlap with printed name above"
}
```

## Integration with Data

### Input JSON Format
```json
{
  "parsedJson": {
    "name": "Jeon Chulmin",
    "id_number": "940101-1111111",
    "address": "48, Sambong-ro, Jongno-gu, Seoul",
    "phone": "010-1234-1234"
  }
}
```

### Field Mapping
The `json_key` in config maps to data:

```json
// Config
"json_key": "name"

// Gets data from
data.parsedJson.name  // "Jeon Chulmin"
```

## Summary

| Feature | Config Key | Values | Purpose |
|---------|-----------|--------|---------|
| **Alignment** | `alignment` | top/middle/bottom | Vertical text position |
| **Wrapping** | `allow_wrap` | true/false | Multi-line text |
| **Sizing** | `fontsize`, `min_fontsize` | 6-12 (points) | Text size |
| **Position** | `box` | {x0, x1, y0, y1} | Field location |

**Key Insight:**
- Use **top** alignment when text below needs preserving (addresses)
- Use **middle** alignment for standard fields (names, IDs)
- Use **bottom** alignment when text above needs preserving (signatures)

The system automatically detects existing text and helps you choose the right alignment!
