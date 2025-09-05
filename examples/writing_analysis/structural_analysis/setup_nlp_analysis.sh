#!/bin/bash
# setup_nlp_analysis.sh
# Setup script for the novel structural analysis tool with virtual environment

echo "Setting up Novel Structural Analysis with spaCy in virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "nlp_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv nlp_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source nlp_env/bin/activate

# Install Python requirements
echo "Installing Python packages..."
pip install spacy matplotlib

# Download spaCy English models
echo "Downloading spaCy English models (this may take a few minutes)..."
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md

echo ""
echo "Setup complete! To use the analysis tools:"
echo ""
echo "1. Activate the environment:"
echo "   source nlp_env/bin/activate"
echo ""
echo "2. Run the fast analysis:"
echo "   python3 chapter_structural_analysis.py your_chapter.txt"
echo ""
echo "3. Run the comprehensive NLP analysis:"
echo "   python3 novel_structural_analysis.py your_novel.txt --output analysis.json --html report.html"
echo ""
echo "4. Deactivate when done:"
echo "   deactivate"
