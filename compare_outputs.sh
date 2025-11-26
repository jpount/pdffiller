#!/bin/bash
# Quick comparison of generated PDFs

echo "==========================================="
echo "  PDF Population - Output Comparison"
echo "==========================================="
echo ""

RESULTS_DIR="results"

echo "Generated PDF files:"
echo "-------------------------------------------"
ls -lh "$RESULTS_DIR"/*.pdf | awk '{print $9, "(" $5 ")"}'

echo ""
echo "-------------------------------------------"
echo "File Details:"
echo "-------------------------------------------"

for file in "$RESULTS_DIR"/populated_*.pdf; do
    if [ -f "$file" ]; then
        basename=$(basename "$file")
        size=$(ls -lh "$file" | awk '{print $5}')
        timestamp=$(basename "$file" | grep -oE '[0-9]{8}_[0-9]{6}')

        echo ""
        case $basename in
            *aligned*)
                echo "✅ ALIGNED ($timestamp) - $size"
                echo "   Perfect alignment to exact box coordinates"
                echo "   Best for: Production use"
                ;;
            *autofit*)
                echo "🎯 AUTO-FIT ($timestamp) - $size"
                echo "   Automatically scales font to fit boxes"
                echo "   Best for: Variable-length data"
                ;;
            *debug*)
                echo "🔍 DEBUG ($timestamp) - $size"
                echo "   Visual verification with colored boxes"
                echo "   Best for: Checking alignment"
                ;;
            *smart*)
                echo "🤖 SMART ($timestamp) - $size"
                echo "   Auto-detects field positions"
                echo "   Best for: Quick testing"
                ;;
            *simple*)
                echo "📝 SIMPLE ($timestamp) - $size"
                echo "   Basic version with manual coordinates"
                echo "   Best for: Understanding the basics"
                ;;
        esac
    fi
done

echo ""
echo "==========================================="
echo "Recommendations:"
echo "==========================================="
echo ""
echo "1. First: Open DEBUG version to verify alignment"
echo "   → Look for colored boxes around fields"
echo ""
echo "2. Then: Use ALIGNED version for production"
echo "   → Perfect positioning, clean output"
echo ""
echo "3. Or: Use AUTO-FIT for variable data"
echo "   → Handles different text lengths"
echo ""
echo "To open a file:"
echo "  open results/populated_aligned_*.pdf"
echo ""
