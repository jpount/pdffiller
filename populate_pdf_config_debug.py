#!/usr/bin/env python3
"""
Config-Based PDF Population with Visual Debug
Shows alignment with colored boxes and reference lines
"""

import json
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime

# Load config from populate_pdf_config.py's calculate_y_position
def calculate_y_position(box, fontsize, alignment, line_height=None, line_number=0):
    """Calculate Y position based on alignment type"""
    box_height = box['y1'] - box['y0']

    if alignment == 'top':
        y = box['y0'] + (fontsize * 0.75) + 1
        if line_height and line_number > 0:
            y += line_number * line_height
    elif alignment == 'bottom':
        y = box['y1'] - (fontsize * 0.25) - 1
        if line_height and line_number > 0:
            y -= line_number * line_height
    else:  # middle
        y = box['y0'] + (box_height / 2) + (fontsize / 3)
        if line_height and line_number > 0:
            y += line_number * line_height

    return y

# Configuration
FIELD_CONFIG = "field_config.json"
DATA_INPUT = "inputs/test.json"
PDF_OUTPUT = f"results/populated_config_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Load configurations
print("="*70)
print("Config-Based PDF with Visual Debug Guides")
print("="*70)

with open(FIELD_CONFIG, 'r', encoding='utf-8') as f:
    config = json.load(f)

with open(DATA_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('parsedJson', {})

# Open PDF
pdf_input = config.get('pdf_template', 'pdf/A0124_pages_1_to_4.pdf')
doc = fitz.open(pdf_input)
page = doc[0]

settings = config.get('settings', {})
padding_h = settings.get('padding_horizontal', 3)

print(f"\nProcessing {len(config['fields'])} fields with visual guides...")
print("="*70)

# Define colors for each alignment type
alignment_colors = {
    'top': (1, 0, 0),      # Red
    'middle': (0, 0, 1),   # Blue
    'bottom': (0, 0.5, 0), # Green
}

for field_def in config['fields']:
    field_id = field_def['id']
    label = field_def['label']
    json_key = field_def['json_key']
    box = field_def['box']
    alignment = field_def.get('alignment', 'middle')
    fontsize = field_def.get('fontsize', 10)

    text = data.get(json_key, '')
    if not text:
        continue

    print(f"\n{label}:")
    print(f"  Alignment: {alignment}")
    print(f"  Box: {box['y0']} to {box['y1']} (height={box['y1']-box['y0']:.1f})")

    # Draw box outline
    rect = fitz.Rect(box['x0'], box['y0'], box['x1'], box['y1'])
    color = alignment_colors.get(alignment, (0, 0, 0))
    page.draw_rect(rect, color=color, width=2)

    # Draw reference lines
    # Top line (in box)
    page.draw_line(
        fitz.Point(box['x0'], box['y0']),
        fitz.Point(box['x1'], box['y0']),
        color=color, width=0.5, dashes="[2 2]"
    )

    # Middle line
    box_middle = box['y0'] + (box['y1'] - box['y0']) / 2
    page.draw_line(
        fitz.Point(box['x0'], box_middle),
        fitz.Point(box['x1'], box_middle),
        color=color, width=0.5, dashes="[2 2]"
    )

    # Bottom line
    page.draw_line(
        fitz.Point(box['x0'], box['y1']),
        fitz.Point(box['x1'], box['y1']),
        color=color, width=0.5, dashes="[2 2]"
    )

    # Calculate text position
    x = box['x0'] + padding_h
    y = calculate_y_position(box, fontsize, alignment)

    # Draw a small marker at text baseline position
    page.draw_circle(fitz.Point(x - 2, y), 1.5, color=color, fill=color)

    # Insert text in BLACK (not colored)
    page.insert_text(
        fitz.Point(x, y),
        text,
        fontsize=fontsize,
        fontname="helv",
        color=(0, 0, 0),
    )

    # Add alignment label outside box
    label_y = box['y0'] - 3
    page.insert_text(
        fitz.Point(box['x0'], label_y),
        f"[{alignment.upper()}]",
        fontsize=7,
        fontname="helv",
        color=color,
    )

    print(f"  Text Y: {y:.1f}")
    print(f"  Distance from top: {y - box['y0']:.1f}pt")
    print(f"  Distance from middle: {y - box_middle:.1f}pt")
    print(f"  Distance from bottom: {box['y1'] - y:.1f}pt")

# Save
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*70)
print("DEBUG PDF Created!")
print("="*70)
print(f"\nOutput: {PDF_OUTPUT}")
print("\nVisual guides:")
print("  • Colored boxes show field boundaries")
print("  • Dashed lines show top/middle/bottom references")
print("  • Small dots show text baseline position")
print("  • Labels show alignment type")
print("\nColors:")
print("  • RED = TOP alignment")
print("  • BLUE = MIDDLE alignment")
print("  • GREEN = BOTTOM alignment")
