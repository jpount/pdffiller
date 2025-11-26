#!/usr/bin/env python3
"""
Debug PDF Population - Shows field boxes visually
Creates a PDF with highlighted boxes to verify alignment
"""

import json
import fitz  # PyMuPDF
from datetime import datetime

# Configuration
PDF_INPUT = "pdf/A0124_pages_1_to_4.pdf"
JSON_INPUT = "inputs/test.json"
PDF_OUTPUT = f"results/populated_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Load JSON data
print("="*70)
print("DEBUG: PDF Population with Visual Field Boxes")
print("="*70)
print("\nLoading JSON data...")
with open(JSON_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('parsedJson', {})

# Open PDF
doc = fitz.open(PDF_INPUT)
page = doc[0]

# Field boxes
field_boxes = {
    'name': {
        'label': '성명',
        'box': {'x0': 79.1, 'x1': 148.8, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('name', ''),
        'fontsize': 10,
        'color': (1, 0, 0)  # Red
    },
    'id_number': {
        'label': '주민등록번호',
        'box': {'x0': 207.2, 'x1': 371.0, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('id_number', ''),
        'fontsize': 10,
        'color': (0, 0, 1)  # Blue
    },
    'phone': {
        'label': '연락처',
        'box': {'x0': 401.9, 'x1': 552.5, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('phone', ''),
        'fontsize': 10,
        'color': (0, 0.5, 0)  # Green
    },
    'address': {
        'label': '주소',
        'box': {'x0': 93.3, 'x1': 339.9, 'y0': 296.9, 'y1': 308.2},
        'text': data.get('address', ''),
        'fontsize': 8,
        'color': (0.5, 0, 0.5)  # Purple
    }
}

print("\nDrawing field boxes and populating data...")
print("-" * 70)

for field_key, field_info in field_boxes.items():
    box = field_info['box']
    text = field_info['text']
    color = field_info['color']

    # Draw a colored rectangle around the field box
    rect = fitz.Rect(box['x0'], box['y0'], box['x1'], box['y1'])
    page.draw_rect(rect, color=color, width=1.5)

    # Calculate text position
    x = box['x0'] + 3
    box_height = box['y1'] - box['y0']
    y = box['y0'] + (box_height / 2) + (field_info['fontsize'] / 3)
    point = fitz.Point(x, y)

    # Insert text in black
    page.insert_text(
        point,
        text,
        fontsize=field_info['fontsize'],
        fontname="helv",
        color=(0, 0, 0),
    )

    # Add a small label above the box
    label_point = fitz.Point(box['x0'], box['y0'] - 2)
    page.insert_text(
        label_point,
        f"[{field_info['label']}]",
        fontsize=7,
        fontname="helv",
        color=color,
    )

    print(f"  ✓ {field_info['label']}: '{text}'")
    print(f"    Box highlighted in color, text at x={x:.1f}, y={y:.1f}")

# Save
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*70)
print("DEBUG PDF Created!")
print("="*70)
print(f"\nOutput: {PDF_OUTPUT}")
print("\nThis PDF shows:")
print("  - Colored boxes around each field (Red, Blue, Green, Purple)")
print("  - Labels above each box")
print("  - Populated data inside the boxes")
print("\nUse this to verify that text is perfectly aligned within the form fields.")
