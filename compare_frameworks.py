#!/usr/bin/env python3
"""
Framework Comparison - PDF Form Field/Box Detection
Compares PyMuPDF, pypdf, and pdfplumber for detecting form structure
"""

import json
import fitz  # PyMuPDF
from pypdf import PdfReader
import pdfplumber
from datetime import datetime

PDF_PATH = "pdf/A0124_pages_1_to_4.pdf"

print("="*80)
print(" PDF FRAMEWORK COMPARISON - Form Field/Box Detection")
print("="*80)
print(f"\nAnalyzing: {PDF_PATH}\n")

# ===========================================================================
# METHOD 1: PyMuPDF (fitz) - Form Fields
# ===========================================================================
print("="*80)
print("METHOD 1: PyMuPDF (fitz) - Form Widget Detection")
print("="*80)

doc = fitz.open(PDF_PATH)
pymupdf_widgets = []

for page_num in range(len(doc)):
    page = doc[page_num]
    widgets = list(page.widgets())  # Convert generator to list

    if widgets:
        print(f"\nPage {page_num + 1}: Found {len(widgets)} form widgets")
        for i, widget in enumerate(widgets):
            info = {
                'page': page_num + 1,
                'name': widget.field_name,
                'type': widget.field_type_string,
                'rect': {
                    'x0': widget.rect.x0,
                    'x1': widget.rect.x1,
                    'y0': widget.rect.y0,
                    'y1': widget.rect.y1
                },
                'value': widget.field_value
            }
            pymupdf_widgets.append(info)
            print(f"  Widget {i+1}: {info['name']} ({info['type']})")
            print(f"    Position: x={info['rect']['x0']:.1f}-{info['rect']['x1']:.1f}, "
                  f"y={info['rect']['y0']:.1f}-{info['rect']['y1']:.1f}")

if not pymupdf_widgets:
    print("  ❌ No form widgets found - PDF has no fillable form fields")

doc.close()

# ===========================================================================
# METHOD 2: PyMuPDF (fitz) - Rectangle Detection (for non-fillable forms)
# ===========================================================================
print("\n" + "="*80)
print("METHOD 2: PyMuPDF (fitz) - Rectangle/Box Detection")
print("="*80)

doc = fitz.open(PDF_PATH)
page = doc[0]  # First page only

# Get page rectangles (these define the visual boxes)
paths = page.get_drawings()
rectangles = [p for p in paths if p.get('type') == 'f' or p.get('rect')]

print(f"\nPage 1: Found {len(rectangles)} drawable rectangles")

# Focus on rectangles in the form field area (y: 160-320)
form_rects = []
for i, rect_info in enumerate(rectangles[:50]):  # Limit to first 50
    if 'rect' in rect_info:
        r = rect_info['rect']
        if 160 <= r.y0 <= 320:
            form_rects.append(r)
            width = r.x1 - r.x0
            height = r.y1 - r.y0
            print(f"  Rect {len(form_rects)}: x={r.x0:.1f}-{r.x1:.1f} (w={width:.1f}), "
                  f"y={r.y0:.1f}-{r.y1:.1f} (h={height:.1f})")

doc.close()

# ===========================================================================
# METHOD 3: pypdf - Form Field Detection
# ===========================================================================
print("\n" + "="*80)
print("METHOD 3: pypdf - Form Field Detection")
print("="*80)

reader = PdfReader(PDF_PATH)
pypdf_fields = []

form_fields = reader.get_fields()
if form_fields:
    print(f"\nFound {len(form_fields)} form fields")
    for field_name, field_data in form_fields.items():
        info = {
            'name': field_name,
            'type': str(field_data.get('/FT', 'Unknown')),
            'value': field_data.get('/V', ''),
            'default': field_data.get('/DV', '')
        }
        pypdf_fields.append(info)
        print(f"  Field: {info['name']}")
        print(f"    Type: {info['type']}")
        print(f"    Value: {info['value']}")
else:
    print("  ❌ No form fields found")

# ===========================================================================
# METHOD 4: pdfplumber - Rectangle/Line Detection
# ===========================================================================
print("\n" + "="*80)
print("METHOD 4: pdfplumber - Rectangle & Table Detection")
print("="*80)

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]

    # Get rectangles
    rects = page.rects if hasattr(page, 'rects') else []
    print(f"\nRectangles found: {len(rects)}")

    # Focus on form area rectangles
    print("\nRectangles in form field area (y: 160-320):")
    field_rects = []
    for i, rect in enumerate(rects):
        if 160 <= rect['top'] <= 320:
            field_rects.append(rect)
            width = rect['x1'] - rect['x0']
            height = rect['bottom'] - rect['top']
            print(f"  Box {len(field_rects)}: x={rect['x0']:.1f}-{rect['x1']:.1f} (w={width:.1f}), "
                  f"y={rect['top']:.1f}-{rect['bottom']:.1f} (h={height:.1f})")

            if len(field_rects) >= 10:  # Limit output
                print(f"  ... (showing first 10 of {len([r for r in rects if 160 <= r['top'] <= 320])} rectangles)")
                break

# ===========================================================================
# METHOD 5: pdfplumber - Text-based Field Detection
# ===========================================================================
print("\n" + "="*80)
print("METHOD 5: pdfplumber - Text-Based Field Label Detection")
print("="*80)

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()

    # Find field labels
    field_labels = ['성명', '주민등록번호', '연락처', '주소', 'name', 'address', 'phone']

    found_labels = []
    for word in words:
        for label in field_labels:
            if label in word['text'].lower():
                found_labels.append({
                    'text': word['text'],
                    'x0': word['x0'],
                    'x1': word['x1'],
                    'top': word['top'],
                    'bottom': word['bottom']
                })

    print(f"\nFound {len(found_labels)} potential field labels:")
    for label_info in found_labels:
        print(f"  Label: '{label_info['text']}'")
        print(f"    Position: x={label_info['x0']:.1f}-{label_info['x1']:.1f}, "
              f"y={label_info['top']:.1f}-{label_info['bottom']:.1f}")

# ===========================================================================
# SUMMARY & COMPARISON
# ===========================================================================
print("\n" + "="*80)
print(" SUMMARY & COMPARISON")
print("="*80)

print("\n┌─────────────────────────┬──────────┬────────────────────────────────┐")
print("│ Framework               │ Found    │ Best For                       │")
print("├─────────────────────────┼──────────┼────────────────────────────────┤")
print(f"│ PyMuPDF (widgets)       │ {len(pymupdf_widgets):8d} │ Fillable PDF forms             │")
print(f"│ PyMuPDF (rectangles)    │ {len(form_rects):8d} │ Visual box detection           │")
print(f"│ pypdf (form fields)     │ {len(pypdf_fields):8d} │ Fillable PDF forms             │")
print(f"│ pdfplumber (rectangles) │ {len(field_rects):8d} │ Visual box/table detection     │")
print(f"│ pdfplumber (text labels)│ {len(found_labels):8d} │ Field label detection          │")
print("└─────────────────────────┴──────────┴────────────────────────────────┘")

print("\n" + "="*80)
print(" RECOMMENDATION")
print("="*80)

if pymupdf_widgets or pypdf_fields:
    print("\n✅ PDF has FILLABLE FORM FIELDS")
    print("   Best approach: Use PyMuPDF or pypdf form field APIs")
    print("   Population: Direct field value assignment")
else:
    print("\n⚠️  PDF has NO fillable form fields (this is your case!)")
    print("   Best approach: Rectangle detection + text overlay")
    print("   Population: Coordinate-based text insertion")
    print("\n   Recommended framework: pdfplumber for analysis")
    print("   Reason:")
    print("   • Excellent rectangle detection")
    print("   • Precise coordinate information")
    print("   • Good text extraction for labels")
    print("   • Works with non-fillable forms")

# ===========================================================================
# CREATE TEXT/INPUT BOX MAPPING
# ===========================================================================
print("\n" + "="*80)
print(" TEXT LABEL → INPUT BOX MAPPING")
print("="*80)

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()
    rects = page.rects if hasattr(page, 'rects') else []

    # Find key field labels
    label_keywords = {
        '성명': 'Name',
        '주민등록번호': 'ID Number',
        '연락처': 'Contact',
        '주소': 'Address'
    }

    mappings = []

    for korean_label, english_label in label_keywords.items():
        # Find label position
        label_word = None
        for word in words:
            if korean_label in word['text']:
                label_word = word
                break

        if not label_word:
            continue

        # Find nearest rectangle (input box) to the right of label
        label_right = label_word['x1']
        label_y = label_word['top']

        best_rect = None
        min_distance = float('inf')

        for rect in rects:
            # Check if rectangle is roughly at same Y level
            if abs(rect['top'] - label_y) < 10:
                # Check if rectangle is to the right of label
                if rect['x0'] > label_right:
                    distance = rect['x0'] - label_right
                    if distance < min_distance:
                        min_distance = distance
                        best_rect = rect

        if best_rect:
            mappings.append({
                'label_korean': korean_label,
                'label_english': english_label,
                'label_position': {
                    'x': label_word['x0'],
                    'y': label_word['top']
                },
                'input_box': {
                    'x0': best_rect['x0'],
                    'x1': best_rect['x1'],
                    'y0': best_rect['top'],
                    'y1': best_rect['bottom'],
                    'width': best_rect['x1'] - best_rect['x0'],
                    'height': best_rect['bottom'] - best_rect['top']
                }
            })

    print("\nDetected Text Label → Input Box Mappings:\n")
    for mapping in mappings:
        print(f"{mapping['label_korean']} ({mapping['label_english']})")
        print(f"  Label at: ({mapping['label_position']['x']:.1f}, {mapping['label_position']['y']:.1f})")
        box = mapping['input_box']
        print(f"  Input Box: x={box['x0']:.1f}-{box['x1']:.1f} (width={box['width']:.1f}pt), "
              f"y={box['y0']:.1f}-{box['y1']:.1f} (height={box['height']:.1f}pt)")
        print()

# Save comparison report
output = {
    'pdf_file': PDF_PATH,
    'analysis_date': datetime.now().isoformat(),
    'results': {
        'pymupdf_widgets': pymupdf_widgets,
        'pymupdf_rectangles': len(form_rects),
        'pypdf_fields': pypdf_fields,
        'pdfplumber_rectangles': len(field_rects),
        'pdfplumber_labels': len(found_labels)
    },
    'text_to_box_mappings': mappings,
    'recommendation': 'pdfplumber' if not (pymupdf_widgets or pypdf_fields) else 'pymupdf'
}

output_file = 'results/framework_comparison.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print(f"✅ Comparison report saved to: {output_file}")
print("="*80)
