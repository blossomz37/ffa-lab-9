#!/bin/bash
# activate_nlp.sh - Quick activation script for the NLP analysis environment

echo "Activating NLP Analysis Environment..."
source nlp_env/bin/activate
echo "Environment activated! You can now run:"
echo "  python3 novel_structural_analysis.py <file> --output analysis.json --html report.html"
echo ""
echo "Type 'deactivate' when finished."
