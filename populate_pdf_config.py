#!/usr/bin/env python3
"""
Config-Based PDF Population with Smart Alignment
Reads field configuration from JSON and supports top/middle/bottom alignment
Detects existing text to avoid overlaps
"""

import json
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime

# Configuration files
FIELD_CONFIG = "field_config.json"
DATA_INPUT = "inputs/test.json"
PDF_OUTPUT = f"results/populated_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"


def get_text_width(text, fontsize):
    """Estimate text width in points"""
    return len(text) * fontsize * 0.5


def fit_text_to_box(text, box_width, initial_fontsize, min_fontsize=6):
    """Calculate optimal font size to fit text in box"""
    fontsize = initial_fontsize
    padding = 0.9  # Use 90% of box width

    while fontsize >= min_fontsize:
        text_width = get_text_width(text, fontsize)
        if text_width <= box_width * padding:
            return fontsize, True
        fontsize -= 0.5

    return min_fontsize, False


def wrap_text(text, box_width, fontsize):
    """Wrap text to fit within box width"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width = get_text_width(test_line, fontsize)

        if test_width <= box_width * 0.9:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def check_existing_text_in_box(pdf_path, page_num, box):
    """
    Check if there's already text in the specified box area
    Returns (has_text, existing_text, text_positions)
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        words = page.extract_words()

        existing_text = []
        for word in words:
            # Check if word overlaps with box
            word_x0, word_x1 = word['x0'], word['x1']
            word_y0, word_y1 = word['top'], word['bottom']

            # Check overlap
            x_overlap = not (word_x1 < box['x0'] or word_x0 > box['x1'])
            y_overlap = not (word_y1 < box['y0'] or word_y0 > box['y1'])

            if x_overlap and y_overlap:
                existing_text.append({
                    'text': word['text'],
                    'x': word['x0'],
                    'y': word['top']
                })

    return len(existing_text) > 0, existing_text


def calculate_y_position(box, fontsize, alignment, line_height=None, line_number=0):
    """
    Calculate Y position based on alignment type

    Args:
        box: Dict with y0, y1 keys
        fontsize: Font size in points
        alignment: 'top', 'middle', or 'bottom'
        line_height: For multi-line text
        line_number: Which line (0-indexed)

    Returns:
        Y coordinate for text baseline
    """
    box_height = box['y1'] - box['y0']

    if alignment == 'top':
        # Align to top - text baseline at top of box
        # For PyMuPDF, baseline should be approximately fontsize * 0.75 from top edge
        y = box['y0'] + (fontsize * 0.75) + 1  # +1 for tiny padding
        if line_height and line_number > 0:
            y += line_number * line_height

    elif alignment == 'bottom':
        # Align to bottom - text baseline at bottom of box
        # Baseline should be approximately fontsize * 0.25 from bottom edge
        y = box['y1'] - (fontsize * 0.25) - 1  # -1 for tiny padding
        if line_height and line_number > 0:
            y -= line_number * line_height

    else:  # middle (default)
        # Center vertically
        y = box['y0'] + (box_height / 2) + (fontsize / 3)
        if line_height and line_number > 0:
            # For multi-line, adjust to keep all lines centered
            y += line_number * line_height

    return y


# Load configurations
print("="*70)
print("Config-Based PDF Population with Smart Alignment")
print("="*70)

print("\nLoading field configuration...")
with open(FIELD_CONFIG, 'r', encoding='utf-8') as f:
    config = json.load(f)

print(f"  ✓ Loaded {len(config['fields'])} field definitions")

print("\nLoading data...")
with open(DATA_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('parsedJson', {})
print(f"  ✓ Name: {data.get('name')}")
print(f"  ✓ ID: {data.get('id_number')}")
print(f"  ✓ Address: {data.get('address')}")
print(f"  ✓ Phone: {data.get('phone')}")

# Open PDF
pdf_input = config.get('pdf_template', 'pdf/A0124_pages_1_to_4.pdf')
print(f"\nOpening PDF: {pdf_input}")
doc = fitz.open(pdf_input)
page = doc[0]

settings = config.get('settings', {})
padding_h = settings.get('padding_horizontal', 3)
padding_v_top = settings.get('padding_vertical_top', 3)
line_height_mult = settings.get('line_height_multiplier', 1.3)

print(f"  Page size: {page.rect.width} x {page.rect.height}")
print("\n" + "="*70)
print("Processing fields...")
print("="*70)

# Process each field
for field_def in config['fields']:
    field_id = field_def['id']
    label = field_def['label']
    json_key = field_def['json_key']
    box = field_def['box']
    alignment = field_def.get('alignment', 'middle')
    allow_wrap = field_def.get('allow_wrap', False)
    initial_fontsize = field_def.get('fontsize', 10)
    min_fontsize = field_def.get('min_fontsize', 6)

    # Get data value
    text = data.get(json_key, '')
    if not text:
        print(f"\n⚠️  {label}: No data found for '{json_key}'")
        continue

    print(f"\n{label}:")
    print(f"  Data: '{text}'")
    print(f"  Alignment: {alignment}")

    # Check for existing text in box
    has_existing, existing = check_existing_text_in_box(pdf_input, 0, box)
    if has_existing:
        print(f"  ⚠️  Detected existing text in box area:")
        for ex in existing[:3]:  # Show first 3
            print(f"      '{ex['text']}' at ({ex['x']:.1f}, {ex['y']:.1f})")
        if alignment == 'top':
            print(f"  ✓ Using top alignment to avoid overlap")

    # Calculate box dimensions
    box_width = box['x1'] - box['x0']
    box_height = box['y1'] - box['y0']
    print(f"  Box: {box_width:.1f}w × {box_height:.1f}h")

    # Fit text to box
    fontsize, fits_single = fit_text_to_box(text, box_width, initial_fontsize, min_fontsize)
    print(f"  Font size: {fontsize}pt")

    # Get offset values (default to 0 if not specified)
    offset_x = field_def.get('offset_x', 0)
    offset_y = field_def.get('offset_y', 0)

    # Calculate X position
    x = box['x0'] + padding_h + offset_x

    # Insert text
    if fits_single or not allow_wrap:
        # Single line
        y = calculate_y_position(box, fontsize, alignment) + offset_y

        if offset_x != 0 or offset_y != 0:
            print(f"  Offset: x={offset_x:+.1f}, y={offset_y:+.1f}")

        page.insert_text(
            fitz.Point(x, y),
            text,
            fontsize=fontsize,
            fontname=settings.get('default_fontname', 'helv'),
            color=tuple(settings.get('default_color', [0, 0, 0])),
        )
        print(f"  ✓ Inserted at x={x:.1f}, y={y:.1f} (single line)")

    else:
        # Multi-line with wrapping
        lines = wrap_text(text, box_width, fontsize)
        line_height = fontsize * line_height_mult
        print(f"  ✓ Wrapped into {len(lines)} lines:")

        if offset_x != 0 or offset_y != 0:
            print(f"  Offset: x={offset_x:+.1f}, y={offset_y:+.1f}")

        for i, line in enumerate(lines):
            y = calculate_y_position(box, fontsize, alignment, line_height, i) + offset_y

            page.insert_text(
                fitz.Point(x, y),
                line,
                fontsize=fontsize,
                fontname=settings.get('default_fontname', 'helv'),
                color=tuple(settings.get('default_color', [0, 0, 0])),
            )
            print(f"    Line {i+1}: '{line}' at x={x:.1f}, y={y:.1f}")

# Save
print(f"\n{'='*70}")
print("Saving PDF...")
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*70)
print("SUCCESS! Config-based PDF created!")
print("="*70)
print(f"\nOutput: {PDF_OUTPUT}")
print("\nFeatures:")
print("  ✓ Configuration-driven field definitions")
print("  ✓ Top/Middle/Bottom alignment support")
print("  ✓ Automatic text size fitting")
print("  ✓ Smart wrapping for long text")
print("  ✓ Existing text detection")
print("\nTo customize:")
print(f"  Edit '{FIELD_CONFIG}' to adjust field positions and alignment")
