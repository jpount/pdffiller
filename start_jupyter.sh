#!/bin/bash
# Quick start script - activates venv and launches Jupyter Notebook

echo "=========================================="
echo "  PDF Filler - Jupyter Notebook Launcher"
echo "=========================================="
echo ""

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"
echo "✓ Starting Jupyter Notebook..."
echo ""
echo "Press Ctrl+C twice to stop the server"
echo ""

# Start Jupyter Notebook
jupyter notebook
