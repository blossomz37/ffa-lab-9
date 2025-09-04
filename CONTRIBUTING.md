# Contributing to FFA Lab 9

Thank you for your interest in contributing to this educational project! This guide will help you get started.

## 🎯 Project Goals

This project is designed to teach students how to build MCP (Model Context Protocol) tools for AI-assisted writing. Our main objectives are:

- Educational clarity and simplicity
- Practical, real-world applications
- Beginner-friendly code with advanced concepts
- Comprehensive documentation and examples

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/yourusername/ffa-lab-9.git
cd ffa-lab-9
```

2. **Set up your development environment:**

**Option A: Using VS Code Dev Container (Recommended)**
- Open the project in VS Code
- Install the Dev Containers extension
- Click "Reopen in Container" when prompted

**Option B: Local development**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
pre-commit install
```

**Option C: Using Docker**
```bash
docker-compose up dev
```

### Project Structure

```
ffa-lab-9/
├── tools/                  # Main analysis tools
│   ├── chapter_*.py       # Individual analysis modules
│   └── writers_room_v2.py # Main coordination script
├── tests/                  # Test suite
├── samples/               # Sample text files
├── docs/                  # Documentation
└── .devcontainer/         # VS Code dev container setup
```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **New Analysis Tools** - Create new chapter analysis modules
2. **Improvements** - Enhance existing tools with new features
3. **Documentation** - Improve guides, tutorials, and code comments
4. **Tests** - Add test cases and improve test coverage
5. **Examples** - Provide sample texts and use cases
6. **Bug Fixes** - Fix issues and improve reliability

### Coding Standards

- **Python Style**: Follow PEP 8, enforced by Black formatter
- **Line Length**: Maximum 88 characters
- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Include docstrings for all public functions and classes
- **Comments**: Write clear, educational comments explaining concepts

### Educational Focus

Since this is an educational project, please ensure your contributions:

- Include clear, explanatory comments
- Provide examples of usage
- Explain the "why" behind design decisions
- Use descriptive variable and function names
- Include relevant documentation

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tools

# Run specific test file
pytest tests/test_emotion_arc.py -v
```

### Writing Tests

- Write tests for all new functionality
- Include both positive and negative test cases
- Use descriptive test method names
- Include docstrings explaining what each test validates

Example test structure:
```python
def test_emotion_analysis_with_positive_text(self):
    """Test that positive emotional text receives positive scores."""
    # Test implementation here
```

## 📚 Documentation

### Code Documentation

- Use clear, descriptive docstrings
- Include usage examples in docstrings
- Document parameters and return values
- Explain any complex algorithms or concepts

### README Updates

If your contribution affects usage or setup:
- Update the main README.md
- Include new examples if applicable
- Update the project structure diagram if needed

## 🔄 Pull Request Process

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
- Write clear, educational code
- Add appropriate tests
- Update documentation

3. **Test your changes:**
```bash
pytest
flake8 tools/
black tools/
mypy tools/
```

4. **Commit with clear messages:**
```bash
git commit -m "Add lexical diversity analysis tool

- Implements vocabulary richness metrics
- Includes type-token ratio calculation
- Adds educational examples and tests"
```

5. **Push and create a pull request:**
```bash
git push origin feature/your-feature-name
```

### Pull Request Guidelines

- **Clear Title**: Describe what your PR accomplishes
- **Detailed Description**: Explain the changes and their educational value
- **Testing**: Confirm all tests pass
- **Documentation**: Update relevant documentation
- **Educational Value**: Explain how this helps students learn

## 🎓 Educational Contributions

### Creating New Analysis Tools

When creating new tools, follow this pattern:

1. **Start with a clear educational goal**
2. **Use the existing template structure:**
   - Imports and type hints
   - Clear function definitions
   - Main function with argument parsing
   - Comprehensive docstrings

3. **Include educational elements:**
   - Step-by-step comments
   - Example usage in docstrings
   - Clear variable names
   - Modular, reusable functions

### Sample Tool Template

```python
#!/usr/bin/env python3
"""
your_analysis_tool.py
--------------------
Educational description of what this tool does and why it's useful
for authors and writing analysis.

USAGE
    python3 your_analysis_tool.py input.txt --output results.json

WHAT IT DOES
- Clear explanation of the analysis
- Step-by-step breakdown
- Educational context
"""

def main() -> None:
    """Main function with educational comments."""
    # Implementation with clear explanations
    pass

if __name__ == "__main__":
    main()
```

## 🤝 Community Guidelines

- Be respectful and supportive of learning
- Focus on educational value in discussions
- Help explain concepts to beginners
- Share knowledge and resources
- Celebrate learning achievements

## 🐛 Reporting Issues

When reporting bugs or requesting features:

1. **Use descriptive titles**
2. **Provide clear reproduction steps**
3. **Include relevant code snippets**
4. **Explain the educational impact**
5. **Suggest possible solutions if you have ideas**

## 🏷️ Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `educational` - Specifically educational improvements

## 📞 Getting Help

- Open an issue for questions or problems
- Check existing issues for similar questions
- Review the documentation and examples
- Ask in discussions for general help

Thank you for contributing to FFA Lab 9! Your contributions help make this a better learning resource for everyone. 🎉
