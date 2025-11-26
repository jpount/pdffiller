#!/usr/bin/env python3
"""
Smart PDF Population Script
Automatically finds field locations and populates data
"""

import json
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime

# Configuration
PDF_INPUT = "pdf/A0124_pages_1_to_4.pdf"
JSON_INPUT = "inputs/test.json"
PDF_OUTPUT = f"results/populated_smart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

def find_text_positions(pdf_path, search_terms):
    """
    Find positions of specific text in PDF
    Returns dict of search term -> (x, y, page) positions
    """
    positions = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()

            for search_term in search_terms:
                for word in words:
                    if search_term in word['text']:
                        if search_term not in positions:
                            positions[search_term] = []
                        positions[search_term].append({
                            'x': word['x1'] + 5,  # Place text slightly after the label
                            'y': word['top'],
                            'page': page_num,
                            'label_width': word['x1'] - word['x0']
                        })

    return positions

# Load JSON data
print("="*60)
print("Smart PDF Population")
print("="*60)
print("\nLoading JSON data...")
with open(JSON_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('parsedJson', {})
print(f"  ✓ Name: {data.get('name')}")
print(f"  ✓ ID: {data.get('id_number')}")
print(f"  ✓ Address: {data.get('address')}")
print(f"  ✓ Phone: {data.get('phone')}")

# Find field label positions
print("\nSearching for field labels in PDF...")
search_terms = ['성명', '주민등록번호', '연락처', '주소']
field_positions = find_text_positions(PDF_INPUT, search_terms)

print(f"  Found {len(field_positions)} field labels")
for term, positions in field_positions.items():
    print(f"    '{term}': {len(positions)} occurrence(s)")

# Open PDF for editing
print(f"\nOpening PDF: {PDF_INPUT}")
doc = fitz.open(PDF_INPUT)

# Map data to fields
field_mapping = {
    '성명': data.get('name', ''),
    '주민등록번호': data.get('id_number', ''),
    '연락처': data.get('phone', ''),
    '주소': data.get('address', '')
}

# Populate fields
print("\nPopulating PDF...")
populated_count = 0

for field_label, field_value in field_mapping.items():
    if field_label in field_positions and field_positions[field_label]:
        # Use first occurrence of each field
        pos = field_positions[field_label][0]
        page = doc[pos['page']]

        # Insert text
        point = fitz.Point(pos['x'], pos['y'] + 10)  # Slight vertical offset

        # Use smaller font for long text (like address)
        fontsize = 8 if len(field_value) > 40 else 10

        page.insert_text(
            point,
            field_value,
            fontsize=fontsize,
            fontname="helv",
            color=(0, 0, 1),  # Blue to distinguish from original
        )

        populated_count += 1
        print(f"  ✓ '{field_label}' → '{field_value[:30]}...'")

# Save
print(f"\nSaving to: {PDF_OUTPUT}")
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*60)
print(f"SUCCESS! Populated {populated_count} fields")
print("="*60)
print(f"\nOutput: {PDF_OUTPUT}")
print("\nNote: New text is in BLUE to distinguish from original form")
print("      If positions need adjustment, modify the x/y offsets in code")
