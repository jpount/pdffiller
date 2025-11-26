# PDF Form Filler - Jupyter Notebook Experiments

Experiment with various Python and AWS frameworks to extract PDF form fields and populate them with JSON data.

## Project Structure

```
pdffiller/
├── inputs/           # JSON input files with data to populate
│   └── test.json    # Sample data with name, ID, address, phone
├── pdf/             # Input PDF forms
│   └── A0124_pages_1_to_4.pdf
├── results/         # Output PDFs and analysis files
├── 01_extract_pdf_fields.ipynb       # Extract and analyze PDF form fields
├── 02_populate_pdf.ipynb             # Populate PDF with JSON data (4 methods)
├── 03_aws_textract_advanced.ipynb    # AWS Textract integration
├── requirements.txt                   # Python dependencies
└── README.md                         # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Run Jupyter Notebooks

```bash
# Start Jupyter
jupyter notebook

# Or use JupyterLab
jupyter lab
```

### 3. Execute Notebooks in Order

1. **Start with `01_extract_pdf_fields.ipynb`**
   - Analyzes your PDF structure
   - Detects form fields (if any)
   - Extracts text positions
   - Saves field analysis to `results/pdf_field_analysis.json`

2. **Then run `02_populate_pdf.ipynb`**
   - Tests 4 different population methods
   - Generates output PDFs with populated data
   - Compares approaches

3. **Optional: `03_aws_textract_advanced.ipynb`**
   - Requires AWS credentials
   - Uses AI to detect form structure automatically
   - Best for complex or scanned documents

## Available Methods

### Method 1: PyMuPDF Form Fields (Recommended for Fillable PDFs)
- Direct form field population
- Fast and reliable
- Requires PDF to have fillable form fields

### Method 2: Text Overlay (For Non-Fillable PDFs)
- Overlays text at specific coordinates
- Requires coordinate adjustment
- Works with any PDF

### Method 3: pypdf Form Filling (Alternative)
- Uses pypdf library
- Good compatibility
- Backup option for Method 1

### Method 4: Smart Auto-Detection (Quick Testing)
- Automatically matches fields by name
- Uses keyword matching
- Great for experimentation

### Method 5: AWS Textract (AI-Powered)
- Automatic form detection
- Works with scanned documents
- Handles mixed languages (Korean + English)
- Requires AWS account and credentials

## Data Format

Input JSON structure (`inputs/test.json`):

```json
{
  "parsedJson": {
    "name": "Jeon Chulmin",
    "id_number": "940101-1111111",
    "address": "48, Sambong-ro, Jongno-gu, Seoul, 03156, Rep. of KOREA",
    "phone": "010-1234-1234"
  }
}
```

## Workflow

```
┌─────────────┐
│  Input PDF  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ 01: Extract Fields          │
│ - PyMuPDF analysis          │
│ - pypdf analysis            │
│ - Text position analysis    │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ 02: Populate PDF            │
│ - Method 1: Form fields     │
│ - Method 2: Text overlay    │
│ - Method 3: pypdf           │
│ - Method 4: Auto-detect     │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ Output: Populated PDFs      │
│ - results/*.pdf             │
└─────────────────────────────┘

       ┌─────────────────────┐
       │ 03: AWS Textract    │
       │ - AI form detection │
       │ - Auto field mapping│
       └─────────────────────┘
```

## AWS Textract Setup (Optional)

### Prerequisites

1. AWS Account with Textract access
2. IAM user with permissions:
   - `textract:AnalyzeDocument`
   - `textract:DetectDocumentText`

### Configuration

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter:
#   AWS Access Key ID
#   AWS Secret Access Key
#   Default region (e.g., us-east-1)
#   Output format (json)

# Test Textract access
aws textract help
```

### Pricing

- **Textract Forms**: ~$1.50 per 1,000 pages
- **Free Tier**: 1,000 pages/month for 3 months (new accounts)

## Troubleshooting

### No Form Fields Found

If notebook 01 shows no form fields:
- Your PDF is likely not a fillable form
- Use Method 2 (Text Overlay) instead
- Or try Method 5 (AWS Textract)

### Text Overlay Misalignment

If Method 2 positions text incorrectly:
1. Check `results/textract_text_elements.json` for positions
2. Adjust coordinates in the `text_overlays` list
3. PDF coordinates: (0,0) = top-left corner

### Korean Text Not Displaying

If Korean characters don't show:
1. Ensure UTF-8 encoding in all files
2. Use a font that supports Korean (e.g., 'malgun' or 'gulim')
3. For PyMuPDF: specify font with `fontfile` parameter

### AWS Credentials Error

If Textract notebook fails:
```bash
# Check credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

## Library Comparison

| Library | Form Fields | Text Overlay | Scanned PDFs | Korean Support | Difficulty |
|---------|-------------|--------------|--------------|----------------|------------|
| **PyMuPDF** | ✅ Excellent | ✅ Excellent | ✅ Good | ✅ Good | Easy |
| **pypdf** | ✅ Good | ❌ Limited | ❌ No | ✅ Good | Easy |
| **pdfplumber** | ❌ No | ⚠️ Analysis | ✅ Good | ✅ Good | Medium |
| **AWS Textract** | ✅ Excellent | ✅ Excellent | ✅ Excellent | ✅ Excellent | Medium |

## Best Practices

1. **Always start with notebook 01** to understand your PDF structure
2. **Test all methods** to find what works best for your specific PDF
3. **Save field mappings** once you find the right configuration
4. **Use version control** for your mapping configurations
5. **Cache Textract results** during development to save costs

## Adding Your Own PDFs

1. Place PDF in `pdf/` folder
2. Update `PDF_PATH` variable in notebooks
3. Create JSON data in `inputs/`
4. Run notebook 01 to analyze
5. Adjust field mappings based on analysis

## Output Files

After running notebooks, check `results/`:

```
results/
├── pdf_field_analysis.json          # Field extraction results
├── textract_response.json           # Raw AWS Textract output
├── textract_key_values.json         # Extracted key-value pairs
├── textract_text_elements.json      # Text with positions
├── field_mappings.json              # Auto-generated mappings
├── populated_output_*_method1_*.pdf # Method 1 output
├── populated_output_*_method2_*.pdf # Method 2 output
├── populated_output_*_method3_*.pdf # Method 3 output
├── populated_output_*_method4_*.pdf # Method 4 output
└── populated_textract.pdf           # Textract method output
```

## Next Steps

1. ✅ Run `01_extract_pdf_fields.ipynb` to analyze your PDF
2. ✅ Review the analysis in `results/pdf_field_analysis.json`
3. ✅ Run `02_populate_pdf.ipynb` to test population methods
4. ✅ Compare output PDFs to find the best method
5. ⚠️ (Optional) Set up AWS and run `03_aws_textract_advanced.ipynb`
6. 🎯 Create production script based on the best method

## Production Deployment

Once you've found the best approach:

1. **Extract the working code** from the notebook
2. **Create a Python script** (e.g., `populate_pdf.py`)
3. **Add error handling** and logging
4. **Implement batch processing** for multiple PDFs
5. **Deploy as API** (FastAPI/Flask) or Lambda function

Example production structure:
```python
# populate_pdf.py
def extract_fields(pdf_path): ...
def load_json_data(json_path): ...
def populate_pdf(input_pdf, data, output_pdf): ...

if __name__ == "__main__":
    # CLI interface
    ...
```

## Support

- **PyMuPDF Docs**: https://pymupdf.readthedocs.io/
- **pypdf Docs**: https://pypdf.readthedocs.io/
- **AWS Textract**: https://docs.aws.amazon.com/textract/
- **Issues**: Review notebook outputs for detailed error messages

## License

Experiment freely! Adapt the notebooks to your needs.
