#!/usr/bin/env python3
"""
Visual Debug - Show surrounding boxes, detected boxes, and text placement
Perfect for verifying alignment and box detection accuracy
"""

import json
import fitz  # PyMuPDF
import pdfplumber
from datetime import datetime

# Configuration
PDF_INPUT = "pdf/A0124_pages_1_to_4.pdf"
JSON_INPUT = "inputs/test.json"
FIELD_CONFIG = "field_config.json"
SURROUNDING_BOXES = "results/surrounding_boxes_20251126_151746.json"  # Latest detection
PDF_OUTPUT = f"results/visual_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

print("="*80)
print(" VISUAL DEBUG - Surrounding Boxes vs Configured Boxes")
print("="*80)

# Load data
with open(JSON_INPUT, 'r', encoding='utf-8') as f:
    json_data = json.load(f)
data = json_data.get('parsedJson', {})

with open(FIELD_CONFIG, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Load surrounding boxes detection
try:
    with open(SURROUNDING_BOXES, 'r', encoding='utf-8') as f:
        surrounding_data = json.load(f)
    surrounding_boxes = {field['field_english']: field for field in surrounding_data.get('fields', [])}
    print(f"\n✓ Loaded surrounding box data: {len(surrounding_boxes)} fields")
except FileNotFoundError:
    print(f"\n⚠️  Surrounding boxes file not found. Run find_surrounding_boxes.py first.")
    surrounding_boxes = {}

# Open PDF
doc = fitz.open(PDF_INPUT)
page = doc[0]

print(f"\nPage size: {page.rect.width} x {page.rect.height}")
print("\nDrawing visual debug overlay...")
print("="*80)

# Color scheme
COLORS = {
    'configured_box': (0, 0, 1),      # Blue - Current configured box
    'surrounding_box': (0, 0.8, 0),   # Green - Detected surrounding box
    'text_baseline': (1, 0, 0),       # Red - Text baseline position
    'label': (0.5, 0.5, 0.5),         # Gray - Field labels
}

# Process each field
settings = config.get('settings', {})
padding_h = settings.get('padding_horizontal', 3)

for field_def in config['fields']:
    field_id = field_def['id']
    label = field_def['label']
    json_key = field_def['json_key']
    box = field_def['box']
    alignment = field_def.get('alignment', 'middle')
    fontsize = field_def.get('fontsize', 10)
    offset_x = field_def.get('offset_x', 0)
    offset_y = field_def.get('offset_y', 0)

    text = data.get(json_key, '')
    if not text:
        continue

    print(f"\n{label}:")

    # === 1. Draw CONFIGURED BOX (Blue) ===
    configured_rect = fitz.Rect(box['x0'], box['y0'], box['x1'], box['y1'])
    page.draw_rect(configured_rect, color=COLORS['configured_box'], width=2)

    # Label for configured box
    page.insert_text(
        fitz.Point(box['x0'], box['y0'] - 10),
        "[CONFIGURED]",
        fontsize=7,
        fontname="helv",
        color=COLORS['configured_box'],
    )

    print(f"  Configured box: x={box['x0']:.1f}-{box['x1']:.1f}, y={box['y0']:.1f}-{box['y1']:.1f}")

    # === 2. Draw SURROUNDING BOX (Green) if available ===
    english_label = label.split('(')[1].split(')')[0] if '(' in label else label
    if english_label in surrounding_boxes:
        surr_field = surrounding_boxes[english_label]
        surr_box = surr_field['input_box']

        surr_rect = fitz.Rect(surr_box['x0'], surr_box['y0'], surr_box['x1'], surr_box['y1'])
        page.draw_rect(surr_rect, color=COLORS['surrounding_box'], width=2, dashes="[4 4]")

        # Label for surrounding box
        page.insert_text(
            fitz.Point(surr_box['x0'], surr_box['y0'] - 3),
            "[DETECTED]",
            fontsize=7,
            fontname="helv",
            color=COLORS['surrounding_box'],
        )

        print(f"  Surrounding box: x={surr_box['x0']:.1f}-{surr_box['x1']:.1f}, y={surr_box['y0']:.1f}-{surr_box['y1']:.1f}")

        # Show difference
        y_diff = surr_box['y0'] - box['y0']
        height_diff = surr_box['height'] - (box['y1'] - box['y0'])
        print(f"  Difference: Y offset={y_diff:+.1f}pts, Height diff={height_diff:+.1f}pts")

    # === 3. Calculate and mark TEXT POSITION ===
    box_height = box['y1'] - box['y0']

    # Calculate Y based on alignment (same as populate_pdf_config.py)
    if alignment == 'top':
        y = box['y0'] + (fontsize * 0.75) + 1
    elif alignment == 'bottom':
        y = box['y1'] - (fontsize * 0.25) - 1
    else:  # middle
        y = box['y0'] + (box_height / 2) + (fontsize / 3)

    # Apply offset
    x = box['x0'] + padding_h + offset_x
    y = y + offset_y

    # Draw horizontal line at text baseline
    page.draw_line(
        fitz.Point(box['x0'], y),
        fitz.Point(box['x1'], y),
        color=COLORS['text_baseline'],
        width=1.5
    )

    # Draw small circle at text start position
    page.draw_circle(fitz.Point(x, y), 2, color=COLORS['text_baseline'], fill=COLORS['text_baseline'])

    print(f"  Text position: x={x:.1f}, y={y:.1f} ({alignment} aligned)")
    if offset_x != 0 or offset_y != 0:
        print(f"  Applied offset: x={offset_x:+.1f}, y={offset_y:+.1f}")

    # === 4. Insert actual TEXT (in black) ===
    # Truncate if too long for visualization
    display_text = text if len(text) <= 50 else text[:47] + "..."

    page.insert_text(
        fitz.Point(x, y),
        display_text,
        fontsize=fontsize,
        fontname="helv",
        color=(0, 0, 0),  # Black
    )

# === 5. Add LEGEND ===
legend_x = 400
legend_y = 50

page.insert_text(
    fitz.Point(legend_x, legend_y),
    "LEGEND:",
    fontsize=10,
    fontname="helv",
    color=(0, 0, 0),
)

# Blue box
page.draw_rect(
    fitz.Rect(legend_x, legend_y + 5, legend_x + 30, legend_y + 20),
    color=COLORS['configured_box'],
    width=2
)
page.insert_text(
    fitz.Point(legend_x + 35, legend_y + 17),
    "Configured Box (from field_config.json)",
    fontsize=8,
    fontname="helv",
    color=(0, 0, 0),
)

# Green dashed box
page.draw_rect(
    fitz.Rect(legend_x, legend_y + 25, legend_x + 30, legend_y + 40),
    color=COLORS['surrounding_box'],
    width=2,
    dashes="[4 4]"
)
page.insert_text(
    fitz.Point(legend_x + 35, legend_y + 37),
    "Detected Surrounding Box (actual input area)",
    fontsize=8,
    fontname="helv",
    color=(0, 0, 0),
)

# Red line
page.draw_line(
    fitz.Point(legend_x, legend_y + 47),
    fitz.Point(legend_x + 30, legend_y + 47),
    color=COLORS['text_baseline'],
    width=1.5
)
page.insert_text(
    fitz.Point(legend_x + 35, legend_y + 50),
    "Text Baseline Position",
    fontsize=8,
    fontname="helv",
    color=(0, 0, 0),
)

# Black text
page.insert_text(
    fitz.Point(legend_x, legend_y + 60),
    "Sample Text",
    fontsize=8,
    fontname="helv",
    color=(0, 0, 0),
)
page.insert_text(
    fitz.Point(legend_x + 35, legend_y + 63),
    "Populated Text Data",
    fontsize=8,
    fontname="helv",
    color=(0, 0, 0),
)

# Save
doc.save(PDF_OUTPUT, garbage=4, deflate=True)
doc.close()

print("\n" + "="*80)
print("VISUAL DEBUG PDF CREATED")
print("="*80)
print(f"\nOutput: {PDF_OUTPUT}")
print("\nWhat to look for:")
print("  • BLUE solid boxes = Your configured box coordinates")
print("  • GREEN dashed boxes = Detected surrounding boxes (actual input area)")
print("  • RED lines = Where text baseline is positioned")
print("  • BLACK text = Actual populated data")
print("\nPerfect alignment:")
print("  • Text should be inside or near top of GREEN box")
print("  • If GREEN and BLUE boxes differ significantly, consider using GREEN coordinates")
print("  • RED line shows exact text position - adjust with offset_y if needed")
print("\n" + "="*80)
