#!/bin/bash
# Quick script to activate the development environment
cd "$(dirname "$0")/.."
source venv/bin/activate
echo "🔄 Development environment activated"
echo "📍 Current directory: $(pwd)"
echo "🐍 Python: $(which python)"
echo "📦 Packages installed: $(pip list | wc -l) packages"
