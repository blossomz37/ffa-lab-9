# FFA Lab 9: Building MCP Tools for AI-Assisted Writing

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An educational project demonstrating how to build Model Context Protocol (MCP) tools for AI-assisted writing and authoring workflows. This repository contains a collection of Python scripts that serve as building blocks for creating sophisticated author assistance tools.

## 🎯 Learning Objectives

This lab teaches students how to:
- Build practical MCP tools using basic Python scripting
- Create modular analysis tools for creative writing
- Implement memory systems for AI assistants
- Design author-focused utilities and workflows
- Structure educational Python projects for AI tool development

## 📚 What's Included

### Core Analysis Tools
- **`chapter_emotion_arc.py`** - Analyzes emotional progression through text using sentiment lexicons
- **`chapter_beats_detection.py`** - Identifies story beats and narrative structure patterns
- **`chapter_character_dialogue.py`** - Analyzes character dialogue patterns and voice consistency
- **`chapter_continuity_consistency.py`** - Checks for continuity errors and inconsistencies
- **`chapter_lexical_diversity.py`** - Measures vocabulary diversity and writing complexity
- **`chapter_structural_analysis.py`** - Examines chapter structure and pacing
- **`chapter_style_readability.py`** - Evaluates writing style and readability metrics
- **`chapter_mechanics_cleanup.py`** - Identifies and suggests fixes for mechanical issues

### Integration Tools
- **`writers_room_v2.py`** - Main coordination script with unit tests
- **`apply_editing_plan.py`** - Applies automated editing suggestions to manuscripts
- **`generate_html_comparison.py`** - Creates visual diff reports for revisions
- **`memory_mcp.py`** - Memory management system for AI assistants

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Basic familiarity with command line operations
- Text files to analyze (sample files included)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/blossomz37/ffa-lab-9.git
cd ffa-lab-9
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Analyze a chapter's emotional arc:**
```bash
python tools/chapter_emotion_arc.py sample.txt --window 5 --csv emotions.csv
```

2. **Check dialogue patterns:**
```bash
python tools/chapter_character_dialogue.py sample.txt --output dialogue_analysis.json
```

3. **Generate a comprehensive analysis:**
```bash
python tools/writers_room_v2.py --input sample.txt --output-dir analysis_results/
```

## 🛠️ Development Setup

### Using VS Code Dev Container (Recommended)

This project includes a complete development container setup for consistent environments:

1. Install [VS Code](https://code.visualstudio.com/) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the project in VS Code
3. When prompted, click "Reopen in Container" or use `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

The dev container includes:
- Python 3.11 with all dependencies
- Pre-configured linting and formatting (black, flake8, mypy)
- Jupyter notebook support
- Git configuration
- VS Code extensions for Python development

### Manual Development Setup

If you prefer to set up your own environment:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Format code
black tools/
flake8 tools/
```

### Using Docker

Build and run the project in Docker:

```bash
# Build the container
docker build -t ffa-lab-9 .

# Run analysis tools
docker run -v $(pwd)/samples:/app/samples ffa-lab-9 python tools/chapter_emotion_arc.py samples/sample.txt
```

## 📖 Educational Modules

### Module 1: Text Analysis Fundamentals
Learn how to build basic text analysis tools using Python's built-in libraries.

**Key Files:** `chapter_emotion_arc.py`, `chapter_lexical_diversity.py`

**Skills Learned:**
- Regular expressions for text processing
- Statistical analysis of text features
- Building extensible lexicon-based tools

### Module 2: Structural Analysis
Understand how to analyze narrative structure and story elements.

**Key Files:** `chapter_beats_detection.py`, `chapter_structural_analysis.py`

**Skills Learned:**
- Pattern recognition in narrative text
- Identifying story beats and plot points
- Measuring pacing and structure

### Module 3: Character and Dialogue Analysis
Explore techniques for analyzing character development and dialogue.

**Key Files:** `chapter_character_dialogue.py`, `chapter_continuity_consistency.py`

**Skills Learned:**
- Character voice analysis
- Dialogue attribution and consistency
- Continuity tracking across text

### Module 4: Integration and Workflow
Learn how to combine individual tools into comprehensive workflows.

**Key Files:** `writers_room_v2.py`, `apply_editing_plan.py`, `memory_mcp.py`

**Skills Learned:**
- Tool orchestration and coordination
- Building memory systems for AI
- Creating user-friendly interfaces

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tools

# Run specific test module
pytest tests/test_emotion_arc.py -v
```

## 📁 Project Structure

```
ffa-lab-9/
├── .devcontainer/          # VS Code dev container configuration
├── .github/workflows/      # CI/CD workflows
├── tools/                  # Main analysis tools
│   ├── chapter_*.py       # Individual analysis modules
│   ├── writers_room_v2.py # Main coordination script
│   ├── memory_mcp.py      # Memory management system
│   └── README-WRITERS ROOM.md
├── tests/                  # Test suite
├── samples/                # Sample text files for testing
├── docs/                   # Additional documentation
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── Dockerfile              # Docker container configuration
├── docker-compose.yml      # Multi-service Docker setup
└── README.md              # This file
```

## 🎓 Learning Exercises

### Exercise 1: Extend the Emotion Lexicon
Modify `chapter_emotion_arc.py` to include genre-specific emotion words for your favorite type of story.

### Exercise 2: Create a New Analysis Tool
Build a new tool that analyzes [specific aspect] using the existing tools as templates.

### Exercise 3: Build an MCP Server
Convert one of the analysis tools into a proper MCP server that can be used with AI assistants.

### Exercise 4: Create Visualization
Add matplotlib/plotly visualization to any of the analysis tools to create charts and graphs.

## 🤝 Contributing

This is an educational project! Contributions are welcome, especially:
- New analysis tools
- Improved documentation
- Additional test cases
- Example text samples
- Tutorial improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📚 Additional Resources

- [Model Context Protocol Documentation](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
- [Python Text Processing Guide](https://docs.python.org/3/howto/regex.html)
- [Creative Writing Analysis Techniques](docs/writing-analysis-techniques.md)
- [Building AI Tools for Authors](docs/ai-tools-guide.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for educational purposes to teach MCP tool development
- Inspired by computational linguistics and creative writing research
- Designed to be beginner-friendly while demonstrating advanced concepts

---

**Happy coding and writing! 📝✨**
