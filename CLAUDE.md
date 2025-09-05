# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FFA Lab 9 is an educational project demonstrating Model Context Protocol (MCP) tools for AI-assisted writing. It provides Python-based text analysis tools that can analyze emotional arcs, narrative structure, dialogue patterns, and other literary aspects of creative writing.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Quick MCP setup (includes all dependencies)
./scripts/setup_mcp_development.sh
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tools

# Run specific test module
pytest tests/test_emotion_arc.py -v

# Run a single test
pytest tests/test_emotion_arc.py::test_analyze_basic -v
```

### Code Quality
```bash
# Format code
black tools/

# Lint code
flake8 tools/

# Type checking
mypy tools/

# Install and use pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### Running Tools
```bash
# Basic analysis of a text file
python tools/chapter_emotion_arc.py sample.txt --window 5 --csv emotions.csv

# Start MCP server
python tools/emotion_arc_mcp_server.py --config config/mcp_server_config.yaml

# Start FastAPI server
./scripts/start_api_server.sh --port 8000 --reload

# Run comprehensive analysis
python tools/writers_room_v2.py --input sample.txt --output-dir analysis_results/
```

## Architecture

### Core Analysis Tools (`tools/`)
Each `chapter_*.py` file is a standalone analysis module with:
- Command-line interface using argparse
- JSON and CSV output capabilities
- Minimal dependencies (mostly stdlib)
- Lexicon-based or pattern-based analysis
- Common pattern: `analyze()` function returns structured data

### Integration Points
- **writers_room_v2.py**: Orchestrates multiple analysis tools
- **emotion_arc_mcp_server.py**: MCP server implementation exposing tools to AI assistants
- **emotion_arc_api_server.py**: FastAPI REST server for HTTP access
- **memory_mcp.py**: Memory management system for AI assistant context

### Data Flow
1. Text input → Individual analysis tools → Structured output (JSON/CSV)
2. MCP/API servers wrap tool functions for external access
3. Writers Room coordinates multiple analyses into comprehensive reports

## Key Implementation Patterns

### Error Handling
- Tools validate input files exist before processing
- Return structured error messages in JSON format
- MCP server uses try/except blocks with detailed error responses

### Output Formats
- All tools support both JSON and CSV output
- JSON includes metadata (timestamp, version, parameters)
- CSV includes headers with clear column names

### Testing Approach
- Unit tests in `tests/` directory
- Use pytest fixtures defined in `conftest.py`
- Test both happy path and error cases
- Mock external dependencies when needed

## Configuration

### MCP Server (`config/mcp_server_config.yaml`)
- Server settings (host, port, logging)
- Tool-specific parameters (window sizes, lexicon paths)

### API Server (`config/api_server_config.yaml`)
- FastAPI configuration
- CORS settings
- Rate limiting parameters

## Important Notes

- The lexicons in analysis tools are intentionally minimal - extend them for production use
- Tools are designed to work with plain text files (.txt)
- Memory system (`memory_mcp.py`) uses JSON for persistence
- All tools preserve original text and add annotations/metrics
- Scripts in `scripts/` handle environment setup and server startup