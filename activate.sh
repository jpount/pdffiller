#!/bin/bash
# Activation script for the PDF Filler virtual environment

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "✓ Virtual environment activated!"
echo ""
echo "Python version:"
python --version
echo ""
echo "Available commands:"
echo "  jupyter notebook  - Start Jupyter Notebook"
echo "  jupyter lab       - Start JupyterLab"
echo "  deactivate        - Exit virtual environment"
echo ""
echo "To deactivate the virtual environment later, just type: deactivate"
