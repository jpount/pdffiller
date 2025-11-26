# Setup Guide - PDF Filler Project

## Virtual Environment Setup (Already Done! ✓)

Your virtual environment has been created and all dependencies are installed!

## Quick Start

### Option 1: One-Command Start (Easiest)

```bash
./start_jupyter.sh
```

This will:
- Activate the virtual environment
- Launch Jupyter Notebook
- Open your browser automatically

### Option 2: Manual Start

```bash
# Activate the virtual environment
source venv/bin/activate

# Start Jupyter Notebook
jupyter notebook

# Or start JupyterLab (modern interface)
jupyter lab
```

## Verify Installation

```bash
# Activate venv first
source venv/bin/activate

# Check Python version
python --version

# Check installed packages
pip list

# Test if PyMuPDF is working
python -c "import fitz; print('PyMuPDF version:', fitz.version)"
```

## Working with the Virtual Environment

### Activate
```bash
source venv/bin/activate
```

You'll see `(venv)` appear in your terminal prompt.

### Deactivate
```bash
deactivate
```

### Reinstall Dependencies (if needed)
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Jupyter Notebook Workflow

1. **Start Jupyter**
   ```bash
   source venv/bin/activate
   jupyter notebook
   ```

2. **Your browser will open automatically**
   - If not, check the terminal for a URL like `http://localhost:8888/...`

3. **Open notebooks in order:**
   - `01_extract_pdf_fields.ipynb` - Analyze PDF structure
   - `02_populate_pdf.ipynb` - Test population methods
   - `03_aws_textract_advanced.ipynb` - AWS integration (optional)

4. **Run cells**
   - Click "Run" or press `Shift + Enter`
   - Run cells in order from top to bottom

5. **Stop Jupyter**
   - Press `Ctrl + C` twice in the terminal
   - Or use "Quit" button in Jupyter interface

## File Structure

```
pdffiller/
├── venv/                    # Virtual environment (don't commit to git)
├── inputs/                  # JSON input data
├── pdf/                     # Input PDF files
├── results/                 # Output PDFs and analysis
├── 01_extract_pdf_fields.ipynb
├── 02_populate_pdf.ipynb
├── 03_aws_textract_advanced.ipynb
├── requirements.txt         # Python dependencies
├── activate.sh             # Helper activation script
├── start_jupyter.sh        # Quick start script
├── README.md               # Main documentation
└── SETUP.md                # This file
```

## Installed Packages

### PDF Processing
- **PyMuPDF** (fitz) - Comprehensive PDF manipulation
- **pypdf** - Alternative PDF library
- **pdfplumber** - Text extraction and analysis

### Data & Jupyter
- **pandas** - Data manipulation
- **jupyter** - Notebook interface
- **notebook** - Jupyter Notebook server
- **ipykernel** - Python kernel for Jupyter

### AWS (Optional)
- **boto3** - AWS SDK (for Textract integration)
- **botocore** - Core AWS functionality

## Troubleshooting

### Virtual environment not activating
```bash
# Make sure you're in the project directory
cd /Users/JOPOUNT/work/korea/pdffiller

# Try activating again
source venv/bin/activate
```

### Jupyter not found
```bash
# Activate venv first
source venv/bin/activate

# Reinstall Jupyter
pip install jupyter notebook
```

### Import errors in notebooks
```bash
# Activate venv and reinstall
source venv/bin/activate
pip install --force-reinstall -r requirements.txt
```

### Korean characters not displaying
- Make sure your terminal/editor supports UTF-8
- Check that system fonts include Korean support

### Permission denied for .sh files
```bash
chmod +x activate.sh
chmod +x start_jupyter.sh
```

## AWS Textract Setup (Optional)

If you want to use notebook 03:

```bash
# Install AWS CLI (if not already installed)
pip install awscli

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Format (json)

# Test connection
aws sts get-caller-identity
```

## Next Steps

1. ✅ Virtual environment is ready
2. ✅ All dependencies installed
3. **→ Start Jupyter**: `./start_jupyter.sh`
4. **→ Open**: `01_extract_pdf_fields.ipynb`
5. **→ Run cells** to analyze your PDF

## Getting Help

- Check README.md for detailed workflow
- Each notebook has extensive comments
- Output files go to `results/` folder
- Review error messages in notebook cells

## Deactivating When Done

```bash
# Stop Jupyter (Ctrl+C twice)
# Then deactivate the virtual environment
deactivate
```

Happy experimenting! 🚀
