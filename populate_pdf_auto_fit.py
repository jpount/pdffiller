#!/usr/bin/env python3
"""
Auto-Fit PDF Population Script
Automatically scales text to fit boxes and handles wrapping
"""

import json
import fitz  # PyMuPDF
from datetime import datetime

# Configuration
PDF_INPUT = "pdf/A0124_pages_1_to_4.pdf"
JSON_INPUT = "inputs/test.json"
PDF_OUTPUT = f"results/populated_autofit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

def get_text_width(text, fontsize, fontname="helv"):
    """Calculate the width of text in points"""
    # Approximate character width for Helvetica
    # This is a rough estimate: average char width ≈ fontsize * 0.5
    return len(text) * fontsize * 0.5

def fit_text_to_box(text, box_width, initial_fontsize, min_fontsize=6):
    """
    Calculate the optimal font size to fit text in box width
    Returns (fontsize, fits_in_one_line)
    """
    fontsize = initial_fontsize

    while fontsize >= min_fontsize:
        text_width = get_text_width(text, fontsize)
        # Leave some padding (10% of box width)
        available_width = box_width * 0.9

        if text_width <= available_width:
            return (fontsize, True)

        fontsize -= 0.5

    # Text still too long even at min size - need to wrap
    return (min_fontsize, False)

def wrap_text(text, box_width, fontsize):
    """
    Wrap text to fit within box width
    Returns list of text lines
    """
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width = get_text_width(test_line, fontsize)
        available_width = box_width * 0.9

        if test_width <= available_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Single word too long
                lines.append(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines

# Load JSON data
print("="*70)
print("Auto-Fit PDF Population (Smart Text Sizing)")
print("="*70)
print("\nLoading JSON data...")
with open(JSON_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('parsedJson', {})

# Open PDF
doc = fitz.open(PDF_INPUT)
page = doc[0]

# Field boxes with initial font sizes
field_boxes = {
    'name': {
        'label': '성명 (Name)',
        'box': {'x0': 79.1, 'x1': 148.8, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('name', ''),
        'initial_fontsize': 10,
        'allow_wrap': False  # Name should be single line
    },
    'id_number': {
        'label': '주민등록번호 (ID Number)',
        'box': {'x0': 207.2, 'x1': 371.0, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('id_number', ''),
        'initial_fontsize': 10,
        'allow_wrap': False
    },
    'phone': {
        'label': '연락처 (Contact)',
        'box': {'x0': 401.9, 'x1': 552.5, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('phone', ''),
        'initial_fontsize': 10,
        'allow_wrap': False
    },
    'address': {
        'label': '주소 (Address)',
        'box': {'x0': 93.3, 'x1': 339.9, 'y0': 296.9, 'y1': 318.0},  # Extended to include both boxes
        'text': data.get('address', ''),
        'initial_fontsize': 9,
        'allow_wrap': True  # Address can wrap
    }
}

print("\nAnalyzing and fitting text to boxes...")
print("-" * 70)

for field_key, field_info in field_boxes.items():
    box = field_info['box']
    text = field_info['text']
    box_width = box['x1'] - box['x0']
    box_height = box['y1'] - box['y0']

    print(f"\n{field_info['label']}:")
    print(f"  Text: '{text}'")
    print(f"  Box: {box_width:.1f}w x {box_height:.1f}h")

    # Calculate optimal font size
    fontsize, fits_single_line = fit_text_to_box(
        text,
        box_width,
        field_info['initial_fontsize']
    )

    print(f"  Optimal font size: {fontsize}pt")

    # Position calculation
    x_start = box['x0'] + 3  # Left padding

    if fits_single_line or not field_info['allow_wrap']:
        # Single line text
        y = box['y0'] + (box_height / 2) + (fontsize / 3)

        page.insert_text(
            fitz.Point(x_start, y),
            text,
            fontsize=fontsize,
            fontname="helv",
            color=(0, 0, 0),
        )

        print(f"  ✓ Inserted as single line")

    else:
        # Multi-line text (wrapping)
        lines = wrap_text(text, box_width, fontsize)
        line_height = fontsize * 1.3  # 130% of font size for line spacing
        total_text_height = len(lines) * line_height

        # Start position to vertically center all lines
        y_start = box['y0'] + (box_height - total_text_height) / 2 + fontsize

        print(f"  ✓ Wrapped into {len(lines)} lines:")
        for i, line in enumerate(lines):
            y = y_start + (i * line_height)
            page.insert_text(
                fitz.Point(x_start, y),
                line,
                fontsize=fontsize,
                fontname="helv",
                color=(0, 0, 0),
            )
            print(f"    Line {i+1}: '{line}'")

# Save
print(f"\n{'='*70}")
print("Saving PDF...")
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*70)
print("SUCCESS! Auto-Fit PDF Created!")
print("="*70)
print(f"\nOutput: {PDF_OUTPUT}")
print("\nFeatures:")
print("  ✓ Text automatically scaled to fit boxes")
print("  ✓ Long text wrapped to multiple lines where appropriate")
print("  ✓ Minimum font size: 6pt")
print("  ✓ Vertical and horizontal alignment optimized")
