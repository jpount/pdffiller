#!/usr/bin/env python3
"""
Simple PDF Population Script
Overlays text at specific coordinates for forms without fillable fields
"""

import json
import fitz  # PyMuPDF
from datetime import datetime

# Configuration
PDF_INPUT = "pdf/A0124_pages_1_to_4.pdf"
JSON_INPUT = "inputs/test.json"
PDF_OUTPUT = f"results/populated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Load JSON data
print("Loading JSON data...")
with open(JSON_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('parsedJson', {})
print(f"  Name: {data.get('name')}")
print(f"  ID: {data.get('id_number')}")
print(f"  Address: {data.get('address')}")
print(f"  Phone: {data.get('phone')}")

# Open PDF
print(f"\nOpening PDF: {PDF_INPUT}")
doc = fitz.open(PDF_INPUT)
page = doc[0]  # First page

print(f"  Page size: {page.rect.width} x {page.rect.height}")

# Korean font support (using default font that supports Unicode)
# For better Korean support, you can install a Korean font file
fontname = "helv"  # Helvetica supports Unicode
fontsize = 10

# Define where to place text (approximate coordinates based on form structure)
# These coordinates are for the "피보험자" (Insured Person) section
# Format: (x, y) where (0,0) is top-left

text_placements = [
    {
        'label': '성명 (Name)',
        'text': data.get('name', ''),
        'position': (95, 285),  # After "성명" field
        'fontsize': 10
    },
    {
        'label': '주민등록번호 (ID Number)',
        'text': data.get('id_number', ''),
        'position': (225, 285),  # After "주민등록번호" field
        'fontsize': 10
    },
    {
        'label': '연락처 (Contact)',
        'text': data.get('phone', ''),
        'position': (465, 285),  # After "연락처" field
        'fontsize': 10
    },
]

print("\nPopulating PDF with data...")
for placement in text_placements:
    point = fitz.Point(placement['position'][0], placement['position'][1])

    # Insert text
    rc = page.insert_text(
        point,
        placement['text'],
        fontsize=placement.get('fontsize', 10),
        fontname=fontname,
        color=(0, 0, 0),  # Black
    )

    print(f"  ✓ {placement['label']}: '{placement['text']}' at {placement['position']}")

# Save the populated PDF
print(f"\nSaving populated PDF to: {PDF_OUTPUT}")
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*60)
print("SUCCESS! PDF populated successfully!")
print("="*60)
print(f"\nOutput file: {PDF_OUTPUT}")
print("\nNote: If text position is incorrect, adjust the 'position' coordinates")
print("in the text_placements list (higher Y = lower on page)")
