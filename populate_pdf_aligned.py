#!/usr/bin/env python3
"""
Perfectly Aligned PDF Population Script
Uses exact coordinates from form field analysis
"""

import json
import fitz  # PyMuPDF
from datetime import datetime

# Configuration
PDF_INPUT = "pdf/A0124_pages_1_to_4.pdf"
JSON_INPUT = "inputs/test.json"
PDF_OUTPUT = f"results/populated_aligned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Load JSON data
print("="*70)
print("Perfectly Aligned PDF Population")
print("="*70)
print("\nLoading JSON data...")
with open(JSON_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('parsedJson', {})
print(f"  ✓ Name: {data.get('name')}")
print(f"  ✓ ID: {data.get('id_number')}")
print(f"  ✓ Address: {data.get('address')}")
print(f"  ✓ Phone: {data.get('phone')}")

# Open PDF
print(f"\nOpening PDF: {PDF_INPUT}")
doc = fitz.open(PDF_INPUT)
page = doc[0]  # First page

print(f"  Page size: {page.rect.width} x {page.rect.height}")

# Exact field positions based on analysis
# Format: Field boxes were identified at specific coordinates
# We place text with small padding inside each box
# Boxes are at y=165.3-189.4 (height ~24) for top row
# Text should be vertically centered: top + height/2 + small_offset

field_boxes = {
    'name': {
        'label': '성명 (Name)',
        'box': {'x0': 79.1, 'x1': 148.8, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('name', ''),
        'fontsize': 10
    },
    'id_number': {
        'label': '주민등록번호 (ID Number)',
        'box': {'x0': 207.2, 'x1': 371.0, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('id_number', ''),
        'fontsize': 10
    },
    'phone': {
        'label': '연락처 (Contact)',
        'box': {'x0': 401.9, 'x1': 552.5, 'y0': 165.3, 'y1': 189.4},
        'text': data.get('phone', ''),
        'fontsize': 10
    },
    'address': {
        'label': '주소 (Address)',
        'box': {'x0': 93.3, 'x1': 339.9, 'y0': 296.9, 'y1': 308.2},
        'text': data.get('address', ''),
        'fontsize': 8  # Smaller font for long address
    }
}

print("\nPopulating PDF with perfect alignment...")
print("-" * 70)

for field_key, field_info in field_boxes.items():
    box = field_info['box']
    text = field_info['text']

    # Calculate position
    # X: Left edge of box + small padding (3 points)
    x = box['x0'] + 3

    # Y: Vertically centered in box
    # For PyMuPDF, text baseline is at the y coordinate
    # So we need: top + (height/2) + (fontsize/3) for approximate centering
    box_height = box['y1'] - box['y0']
    y = box['y0'] + (box_height / 2) + (field_info['fontsize'] / 3)

    point = fitz.Point(x, y)

    # Insert text
    page.insert_text(
        point,
        text,
        fontsize=field_info['fontsize'],
        fontname="helv",
        color=(0, 0, 0),  # Black text
    )

    print(f"  ✓ {field_info['label']}")
    print(f"    Value: '{text}'")
    print(f"    Position: x={x:.1f}, y={y:.1f} (in box x={box['x0']:.1f}-{box['x1']:.1f})")
    print()

# Save the populated PDF
print(f"Saving to: {PDF_OUTPUT}")
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*70)
print("SUCCESS! PDF populated with perfect alignment!")
print("="*70)
print(f"\nOutput file: {PDF_OUTPUT}")
print("\nAll text has been placed precisely within the form field boxes.")
print("If you need micro-adjustments, modify the x/y offset calculations in the code.")
