#!/bin/bash

# MCP Development Environment Setup Script for macOS/Linux
# This script sets up the development environment for MCP integration

set -e  # Exit on any error

echo "🚀 Setting up MCP Development Environment for FFA Lab 9"
echo "========================================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the ffa-lab-9 root directory"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python 3.8+ required, found $PYTHON_VERSION"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies if available
if [ -f "requirements-dev.txt" ]; then
    echo "🛠️  Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p scripts
mkdir -p config
mkdir -p samples/mcp_test_cases
mkdir -p docs
mkdir -p logs

# Create sample configuration file
echo "⚙️  Creating sample configuration..."
cat > config/mcp_server_config.yaml << EOF
# MCP Server Configuration
server:
  host: "localhost"
  port: 8000
  debug: true
  
analysis:
  default_window_size: 5
  max_text_length: 100000
  supported_formats: ["json", "csv", "markdown"]
  
logging:
  level: "INFO"
  file: "logs/mcp_server.log"
  max_size_mb: 10
  backup_count: 5

lexicons:
  # You can extend these lexicons for genre-specific analysis
  positive_words_file: null
  negative_words_file: null
  emotion_words_file: null
EOF

# Create sample test case
echo "📝 Creating sample test case..."
cat > samples/mcp_test_cases/sample_text.txt << EOF
The morning sun broke through the clouds, filling Sarah with joy and anticipation. She had been waiting for this day for months. However, as she approached the building, a wave of anxiety washed over her. What if things didn't go as planned? The uncertainty was almost overwhelming.

But then she remembered her friend's encouraging words from the night before. Taking a deep breath, she pushed open the door and stepped inside. The warmth of the reception area immediately calmed her nerves. This was going to be a good day after all.
EOF

# Test basic functionality
echo "🧪 Testing basic functionality..."
python3 tools/chapter_emotion_arc.py samples/mcp_test_cases/sample_text.txt --json /tmp/test_output.json --window 3

if [ -f "/tmp/test_output.json" ]; then
    echo "✅ Basic emotion analysis test passed"
    rm /tmp/test_output.json
else
    echo "⚠️  Warning: Basic functionality test failed"
fi

# Create environment activation script
cat > scripts/activate_dev_env.sh << EOF
#!/bin/bash
# Quick script to activate the development environment
cd "\$(dirname "\$0")/.."
source venv/bin/activate
echo "🔄 Development environment activated"
echo "📍 Current directory: \$(pwd)"
echo "🐍 Python: \$(which python)"
echo "📦 Packages installed: \$(pip list | wc -l) packages"
EOF

chmod +x scripts/activate_dev_env.sh

echo ""
echo "🎉 Setup complete!"
echo "========================================================"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source venv/bin/activate"
echo "2. Or use the helper script: ./scripts/activate_dev_env.sh"
echo "3. Start working on MCP integration following the task list"
echo "4. Test your changes with: python tools/chapter_emotion_arc.py samples/sample_chapter.txt"
echo ""
echo "Useful commands:"
echo "• Run tests: pytest tests/"
echo "• Check code style: black tools/ && flake8 tools/"
echo "• View task list: cat MCP_Integration_Task_List.md"
echo ""
echo "Happy coding! 🚀"
