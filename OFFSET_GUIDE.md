# Field Offset & Surrounding Box Guide

## Problem: Detected Boxes Don't Match Actual Input Areas

The PDF rectangle detection finds table cell boundaries, but the actual input areas might be different. This is common in Korean forms where:
- Text labels and input boxes share table cells
- Visual boxes don't match logical input areas
- Pre-printed text overlaps with input regions

## Two Solutions

### ✅ Solution 1: Use Offsets (Manual Fine-Tuning)

Add `offset_x` and `offset_y` to shift text position without changing box coordinates.

**When to use:**
- Quick adjustments needed
- Box coordinates are close but not perfect
- You want to keep detected box for reference

**How to use:**
```json
{
  "id": "address",
  "box": {
    "x0": 93.3,
    "x1": 339.9,
    "y0": 296.9,
    "y1": 318.0
  },
  "offset_x": 0,      ← Shift left/right (negative = left)
  "offset_y": -10,    ← Shift up/down (negative = up)
  "alignment": "top"
}
```

**Offset values:**
- `offset_y: -10` moves text 10pts UP
- `offset_y: +10` moves text 10pts DOWN
- `offset_x: -5` moves text 5pts LEFT
- `offset_x: +5` moves text 5pts RIGHT

### ✅ Solution 2: Use Surrounding Box Detection (Automatic)

Run `find_surrounding_boxes.py` to automatically detect actual input boxes.

**When to use:**
- Want precise box coordinates
- Initial detection was completely wrong
- Need to find boxes programmatically

**How to use:**
```bash
# Run the detector
python find_surrounding_boxes.py

# Review recommended coordinates
# Update field_config.json with detected boxes
# Set offset_y to 0 (or small value for fine-tuning)
```

## Comparison: Detected vs Actual Boxes

### Address Field Example

**Original Detection:**
```
Box: x=93.3-339.9, y=296.9-318.0 (height=21.1pt)
Text position: y=303.9 (middle-ish)
Result: ❌ Text overlaps pre-printed content
```

**With Offset (-10pts):**
```
Box: x=93.3-339.9, y=296.9-318.0 (same)
Offset: y=-10
Text position: y=293.9
Result: ⚠️ Better, but still not optimal
```

**With Surrounding Box:**
```
Box: x=79.1-362.6, y=277.6-320.8 (height=43.2pt!)
Offset: y=0
Text position: y=285.4
Result: ✅ Perfect alignment with actual input area
```

## Surrounding Box Detection Results

Running `find_surrounding_boxes.py` found:

| Field | Original Box Y | Surrounding Box Y | Difference |
|-------|---------------|-------------------|------------|
| Name | 165.3-189.4 | 209.5-225.1 | +44.2pts (below) |
| ID Number | 165.3-189.4 | 190.6-225.4 | +25.3pts (below) |
| Contact | 165.3-189.4 | 190.6-225.4 | +25.3pts (below) |
| **Address** | **296.9-318.0** | **277.6-320.8** | **-19.3pts (bigger!)** |

### Key Findings

1. **Name, ID, Contact fields:** Actual input boxes are BELOW the labels
2. **Address field:** Actual input box is LARGER and starts higher
3. **Box heights:** Surrounding boxes are bigger (15-43pts vs 24pts)

## Configuration Options

### Option A: Minimal Config (Offsets Only)

Keep detected boxes, use offsets for fine-tuning:

```json
{
  "fields": [
    {
      "id": "address",
      "box": {"x0": 93.3, "x1": 339.9, "y0": 296.9, "y1": 318.0},
      "offset_y": -10,    ← Quick fix
      "alignment": "top"
    }
  ]
}
```

**Pros:**
- Simple, minimal changes
- Easy to tweak incrementally

**Cons:**
- May not perfectly match input area
- Box size might be wrong

### Option B: Precise Config (Surrounding Boxes)

Use detected surrounding boxes:

```json
{
  "fields": [
    {
      "id": "address",
      "box": {"x0": 79.1, "x1": 362.6, "y0": 277.6, "y1": 320.8},
      "offset_y": 0,      ← No offset needed!
      "alignment": "top"
    }
  ]
}
```

**Pros:**
- Matches actual input area precisely
- Correct box dimensions for wrapping

**Cons:**
- Requires running detection script
- More initial setup

### Option C: Hybrid (Best of Both)

Use surrounding boxes + small offsets for perfect placement:

```json
{
  "fields": [
    {
      "id": "address",
      "box": {"x0": 79.1, "x1": 362.6, "y0": 277.6, "y1": 320.8},
      "offset_x": 2,      ← Fine-tune horizontally
      "offset_y": -3,     ← Fine-tune vertically
      "alignment": "top"
    }
  ]
}
```

**Pros:**
- Best precision
- Flexibility for edge cases

**Cons:**
- Most complex
- Requires testing

## Step-by-Step Workflow

### Method 1: Quick Fix with Offsets

1. Run current config
   ```bash
   python populate_pdf_config.py
   ```

2. Check output PDF - is text too high/low?

3. Adjust offset in field_config.json:
   ```json
   "offset_y": -5   // Try different values
   ```

4. Re-run and check again

5. Repeat until perfect

### Method 2: Precise Detection

1. Run surrounding box detector
   ```bash
   python find_surrounding_boxes.py
   ```

2. Review output - note recommended coordinates

3. Update field_config.json with detected boxes:
   ```json
   "box": {
     "x0": 79.1,
     "x1": 362.6,
     "y0": 277.6,
     "y1": 320.8
   },
   "offset_y": 0
   ```

4. Test
   ```bash
   python populate_pdf_config.py
   ```

5. Fine-tune with small offsets if needed

## Visual Verification

Use the debug script to see boxes and alignment:

```bash
python populate_pdf_config_debug.py
```

This shows:
- Colored boxes around configured areas
- Reference lines (top/middle/bottom)
- Text baseline positions
- Helpful for comparing detected vs actual

## Common Offset Values

| Adjustment Need | offset_y Value | Description |
|----------------|---------------|-------------|
| Text too low | -5 to -15 | Move up into input area |
| Text too high | +5 to +15 | Move down |
| Perfect vertical | 0 | No adjustment needed |

| Adjustment Need | offset_x Value | Description |
|----------------|---------------|-------------|
| Text too far right | -5 to -10 | Move left |
| Text too far left | +5 to +10 | Move right |
| Perfect horizontal | 0 | No adjustment needed |

## Testing Tips

1. **Start with surrounding box detection**
   - Gets you close to correct coordinates
   - Saves time vs manual trial-and-error

2. **Use offsets for final tweaks**
   - ±2-5pts for minor adjustments
   - Test in small increments

3. **Check debug output**
   - Visual verification is fastest
   - Look for text position relative to lines

4. **Test with real data**
   - Long text (addresses)
   - Short text (names)
   - Ensure both fit well

## Current Configuration Status

**As of last update:**

```
Address Field:
  Box: 79.1-362.6 (width=283.5), 277.6-320.8 (height=43.2)
  Alignment: top
  Offset: x=0, y=0
  Text position: y=285.4
  Status: ✅ Using surrounding box coordinates
```

**Previous iterations:**
1. Original: y=296.9-318.0, no offset → y=303.9 ❌
2. With offset: y=296.9-318.0, offset_y=-10 → y=293.9 ⚠️
3. Surrounding box: y=277.6-320.8, offset_y=0 → y=285.4 ✅

## Summary

| Approach | Setup Time | Precision | Flexibility | Best For |
|----------|-----------|-----------|-------------|----------|
| **Offsets only** | Low | Medium | High | Quick fixes |
| **Surrounding boxes** | Medium | High | Medium | Accurate placement |
| **Hybrid** | Medium | Very High | Very High | Production use |

### Recommendation

**For your PDF:**
1. ✅ Use surrounding box coordinates (already applied)
2. ⚠️ Add small offsets only if needed for fine-tuning
3. ✅ Test with real data to verify

**Current status:** Using surrounding boxes for address field. Text at y=285.4, which should align properly with the actual input area!

## Files Reference

- `field_config.json` - Main configuration with boxes and offsets
- `populate_pdf_config.py` - Population script (reads offsets)
- `find_surrounding_boxes.py` - Automatic box detection
- `populate_pdf_config_debug.py` - Visual verification
- `results/surrounding_boxes_*.json` - Detected box coordinates

## Next Steps

1. ✅ Open `results/populated_config_*.pdf`
2. ✅ Verify address field alignment
3. ⚠️ If still not perfect, adjust offset_y by ±2-5pts
4. ✅ Repeat for other fields if needed

The offset system gives you complete control over text placement while keeping the configuration clean and maintainable!
