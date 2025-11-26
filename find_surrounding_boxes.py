#!/usr/bin/env python3
"""
Find Surrounding Boxes - Automatically detect actual input boxes around text labels
This helps find the correct box coordinates when the detected rectangles don't match form structure
"""

import json
import pdfplumber
from datetime import datetime

PDF_PATH = "pdf/A0124_pages_1_to_4.pdf"

def find_containing_box(label_position, all_rects, search_direction='right', max_distance=100):
    """
    Find the box that contains or is near a label

    Args:
        label_position: Dict with x0, x1, top, bottom of label
        all_rects: List of all rectangles in the page
        search_direction: 'right', 'left', 'below', 'above'
        max_distance: Maximum distance to search

    Returns:
        Best matching rectangle or None
    """
    label_x = label_position['x0']
    label_right = label_position['x1']
    label_y = label_position['top']
    label_bottom = label_position['bottom']

    candidates = []

    for rect in all_rects:
        rect_x0 = rect['x0']
        rect_x1 = rect['x1']
        rect_y0 = rect['top']
        rect_y1 = rect['bottom']

        # Check if rectangle is in the search direction
        if search_direction == 'right':
            # Box should be to the right of label
            if rect_x0 >= label_right:
                # Check if roughly same Y level
                y_overlap = not (rect_y1 < label_y or rect_y0 > label_bottom)
                if y_overlap:
                    distance = rect_x0 - label_right
                    if distance <= max_distance:
                        candidates.append({
                            'rect': rect,
                            'distance': distance,
                            'score': 1.0 / (distance + 1)  # Closer is better
                        })

        elif search_direction == 'below':
            # Box should be below label
            if rect_y0 >= label_bottom:
                # Check if roughly same X position
                x_overlap = not (rect_x1 < label_x or rect_x0 > label_right)
                if x_overlap:
                    distance = rect_y0 - label_bottom
                    if distance <= max_distance:
                        candidates.append({
                            'rect': rect,
                            'distance': distance,
                            'score': 1.0 / (distance + 1)
                        })

    if not candidates:
        return None

    # Return the closest box with reasonable size
    candidates.sort(key=lambda c: -c['score'])

    # Filter out tiny boxes (likely lines/borders)
    good_candidates = [c for c in candidates if
                      (c['rect']['x1'] - c['rect']['x0']) > 30 and  # Width > 30pt
                      (c['rect']['bottom'] - c['rect']['top']) > 10]  # Height > 10pt

    if good_candidates:
        return good_candidates[0]['rect']
    elif candidates:
        return candidates[0]['rect']

    return None

print("="*80)
print(" Surrounding Box Detector - Find Actual Input Boxes")
print("="*80)
print(f"\nAnalyzing: {PDF_PATH}\n")

with pdfplumber.open(PDF_PATH) as pdf:
    page = pdf.pages[0]
    words = page.extract_words()
    rects = page.rects if hasattr(page, 'rects') else []

    print(f"Found {len(words)} words and {len(rects)} rectangles\n")

    # Field labels to search for
    field_labels = {
        '성명': 'Name',
        '주민등록번호': 'ID Number',
        '연락처': 'Contact',
        '주소': 'Address'
    }

    results = []

    for korean_label, english_label in field_labels.items():
        print("="*80)
        print(f"Searching for: {korean_label} ({english_label})")
        print("="*80)

        # Find the label
        label_word = None
        for word in words:
            if korean_label in word['text']:
                label_word = word
                break

        if not label_word:
            print(f"  ❌ Label not found\n")
            continue

        print(f"\n  Label position:")
        print(f"    x={label_word['x0']:.1f}-{label_word['x1']:.1f}, y={label_word['top']:.1f}-{label_word['bottom']:.1f}")

        # Try different search strategies
        print(f"\n  Searching for input box...")

        # Strategy 1: Look right (most common for horizontal forms)
        box_right = find_containing_box(label_word, rects, 'right', max_distance=50)

        # Strategy 2: Look below (for vertical forms)
        box_below = find_containing_box(label_word, rects, 'below', max_distance=30)

        # Choose best box
        best_box = None
        strategy = None

        if box_right and (not box_below or
                          (box_right['x1'] - box_right['x0']) > (box_below['x1'] - box_below['x0'])):
            best_box = box_right
            strategy = "to the right"
        elif box_below:
            best_box = box_below
            strategy = "below"

        if best_box:
            width = best_box['x1'] - best_box['x0']
            height = best_box['bottom'] - best_box['top']

            print(f"  ✓ Found input box {strategy}:")
            print(f"    x={best_box['x0']:.1f}-{best_box['x1']:.1f} (width={width:.1f}pt)")
            print(f"    y={best_box['top']:.1f}-{best_box['bottom']:.1f} (height={height:.1f}pt)")

            # Calculate recommended offset from currently configured box
            # (Assume current config uses the detected rectangle at label position)
            current_y = label_word['top']  # Approximate
            new_y_top = best_box['top']
            recommended_offset_y = new_y_top - current_y

            print(f"  💡 Recommended offset_y: {recommended_offset_y:.1f} pts")

            result = {
                'field_korean': korean_label,
                'field_english': english_label,
                'label': {
                    'x0': label_word['x0'],
                    'x1': label_word['x1'],
                    'y0': label_word['top'],
                    'y1': label_word['bottom']
                },
                'input_box': {
                    'x0': best_box['x0'],
                    'x1': best_box['x1'],
                    'y0': best_box['top'],
                    'y1': best_box['bottom'],
                    'width': width,
                    'height': height
                },
                'recommended_offset_y': round(recommended_offset_y, 1),
                'strategy': strategy
            }
            results.append(result)
        else:
            print(f"  ❌ No suitable input box found")

        print()

# Create summary table
print("\n" + "="*80)
print(" SUMMARY - Recommended Field Configuration")
print("="*80)

print("\n┌────────────────────┬─────────────────────────────┬──────────────┐")
print("│ Field              │ Input Box (x,y → x,y)       │ Offset Y     │")
print("├────────────────────┼─────────────────────────────┼──────────────┤")
for result in results:
    field = result['field_english']
    box = result['input_box']
    offset = result['recommended_offset_y']
    print(f"│ {field:18s} │ ({box['x0']:5.1f},{box['y0']:5.1f} → {box['x1']:5.1f},{box['y1']:5.1f}) │ {offset:+6.1f} pts  │")
print("└────────────────────┴─────────────────────────────┴──────────────┘")

# Generate updated config
print("\n" + "="*80)
print(" SUGGESTED CONFIG UPDATES")
print("="*80)

print("\nAdd these to your field_config.json:\n")
for result in results:
    box = result['input_box']
    print(f"// {result['field_english']}")
    print(f'{{"')
    print(f'  "id": "{result["field_english"].lower().replace(" ", "_")}",')
    print(f'  "box": {{')
    print(f'    "x0": {box["x0"]},')
    print(f'    "x1": {box["x1"]},')
    print(f'    "y0": {box["y0"]},')
    print(f'    "y1": {box["y1"]}')
    print(f'  }},')
    print(f'  "offset_y": {result["recommended_offset_y"]},  // To align with actual input area')
    print(f'  ...')
    print(f'}},\n')

# Save detailed report
output_file = f'results/surrounding_boxes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'pdf_file': PDF_PATH,
        'analysis_date': datetime.now().isoformat(),
        'fields': results
    }, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print(f"✅ Detailed analysis saved to: {output_file}")
print("="*80)
print("\nNext steps:")
print("  1. Review the recommended offset_y values above")
print("  2. Update field_config.json with the offset_y values")
print("  3. Or use the detected box coordinates directly")
print("  4. Run populate_pdf_config.py to test")
